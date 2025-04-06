import zmq
import zmq.auth
from zmq.auth.thread import ThreadAuthenticator
import jwt
import json
import msgpack
import asyncio
import logging
import secrets
import time
import random
from typing import Callable, Dict
from google.protobuf.message import DecodeError  # Para Protobuf
from google.protobuf.json_format import Parse, MessageToJson  # Para Protobuf
from circuitbreaker import CircuitBreaker  # Librería externa para circuit breaker
from fastapi import FastAPI
from prometheus_client import start_http_server, Counter, Histogram
import structlog
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
import zmq.utils.z85 as z85  # Agregar al inicio con los otros imports
import binascii

# Configuración de logs estructurados
structlog.configure(
    processors=[structlog.processors.JSONRenderer(indent=2)]
)
logger = structlog.get_logger()

app = FastAPI()

REQUEST_COUNT = Counter("requests_total", "Número total de solicitudes", ["operation"])
REQUEST_LATENCY = Histogram("requests_latency_seconds", "Latencia de solicitudes", ["operation"])

@app.get("/openapi.json")
def openapi():
    return app.openapi()

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/.well-known/jwks.json")
def jwks():
    return {
        "keys": [json.loads(SecureBridge.public_jwk)]
    }

class SecureBridge:
    def __init__(self, server_port: int, client_port: int, private_key: str, public_key: str, peer_public_key: str, jwt_secret: str):
        self.server_port = server_port
        self.client_port = client_port
        # Convertir claves a bytes usando Z85
        try:
            self.private_key = z85.decode(private_key) if isinstance(private_key, str) else private_key
            self.public_key = z85.decode(public_key) if isinstance(public_key, str) else public_key
            self.peer_public_key = z85.decode(peer_public_key) if isinstance(peer_public_key, str) else peer_public_key
        except binascii.Error as e:
            raise ValueError(f"Invalid key format: {e}")
        self.jwt_secret = jwt_secret
        self.context = zmq.Context()
        self.authenticator = None
        self.handlers: Dict[str, Callable] = {}
        self.logger = logging.getLogger("SecureBridge")
        self.logger.setLevel(logging.INFO)
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=3,           # en lugar de fail_max
            recovery_timeout=30,           # en lugar de reset_timeout
            name="secure_bridge_breaker"   # nombre opcional para identificación
        )
        self.last_rotation = time.time()
        self.jwt_rotation_task = None  # Inicialmente None
        self.rsa_private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )
        self.public_jwk = self.rsa_private_key.public_key().public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

    @staticmethod
    def generate_curve_keypair():
        """Genera un par de claves CURVE y las devuelve en formato Z85"""
        public, secret = zmq.curve_keypair()
        return z85.encode(secret).decode('ascii'), z85.encode(public).decode('ascii')

    async def init_jwt_rotation(self):
        """Inicializar la tarea de rotación de JWT"""
        self.jwt_rotation_task = asyncio.create_task(self._rotate_jwt_secret())
        return self

    async def _rotate_jwt_secret(self):
        while True:
            await asyncio.sleep(3600)  # Intervalo de rotación de ejemplo
            self.jwt_secret = secrets.token_urlsafe(64)
            self.last_rotation = time.time()
            self.logger.info("JWT secret rotated")

    def start_authenticator(self):
        self.authenticator = ThreadAuthenticator(self.context)
        self.authenticator.start()
        self.authenticator.allow('127.0.0.1')
        self.authenticator.configure_curve(domain='*', location=zmq.auth.CURVE_ALLOW_ANY)

    def stop_authenticator(self):
        if self.authenticator:
            self.authenticator.stop()

    def register_handler(self, operation: str, handler: Callable):
        self.handlers[operation] = handler

    def validate_jwt(self, token: str):
        try:
            return jwt.decode(token, self.jwt_secret, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            raise ValueError("JWT expired")
        except jwt.InvalidTokenError:
            raise ValueError("Invalid JWT")

    def serialize(self, data: dict, format: str) -> bytes:
        if format == "protobuf":
            return data.SerializeToString()  # data debe ser un mensaje Protobuf
        elif format == "json":
            return json.dumps(data).encode("utf-8")
        elif format == "msgpack":
            return msgpack.packb(data)
        else:
            raise ValueError("Unsupported serialization format")

    def deserialize(self, data: bytes, format: str) -> dict:
        if format == "protobuf":
            try:
                message = BridgeMessage()  # Clase generada por Protobuf
                message.ParseFromString(data)
                return json.loads(MessageToJson(message))
            except DecodeError as e:
                raise ValueError(f"Protobuf deserialization error: {e}")
        elif format == "json":
            return json.loads(data.decode("utf-8"))
        elif format == "msgpack":
            return msgpack.unpackb(data)
        else:
            raise ValueError("Unsupported serialization format")

    async def start_server(self):
        socket = self.context.socket(zmq.REP)
        socket.curve_secretkey = self.private_key
        socket.curve_publickey = self.public_key
        socket.curve_server = True
        socket.bind(f"tcp://*:{self.server_port}")

        while True:
            try:
                with self.circuit_breaker:
                    message = socket.recv_json()
                    token = message.get("token")
                    self.validate_jwt(token)
                    operation = message.get("operation")
                    data = message.get("data")
                    if operation in self.handlers:
                        response = self.handlers[operation](data)
                        socket.send_json({"status": "success", "data": response})
                        REQUEST_LATENCY.labels(operation=operation).observe(time.time() - start_time)
                    else:
                        socket.send_json({"status": "error", "message": "Unknown operation"})
            except ValueError as e:
                self.logger.error(f"JWT validation error: {e}")
                socket.send_json({"status": "error", "message": str(e)})
            except Exception as e:
                self.logger.error(f"Error in server: {e}")
                socket.send_json({"status": "error", "message": str(e)})

    async def start_client(self, message: dict, format: str = "json"):
        socket = self.context.socket(zmq.REQ)
        socket.curve_secretkey = self.private_key
        socket.curve_publickey = self.public_key
        socket.curve_serverkey = self.peer_public_key
        socket.connect(f"tcp://localhost:{self.client_port}")
        for attempt in range(3):  # Backoff exponencial con jitter
            try:
                serialized_message = self.serialize(message, format)
                socket.send(serialized_message)
                response = socket.recv()
                return self.deserialize(response, format)
            except Exception as e:
                delay = min(2 ** attempt + random.uniform(0, 1), 10)
                self.logger.error(f"Attempt {attempt + 1} failed: {e}, retrying in {delay}s")
                await asyncio.sleep(delay)
        return {"status": "error", "message": "Max retries exceeded"}

    def shutdown(self):
        self.context.term()
        self.stop_authenticator()

    def print_keys(self):
        """Método de diagnóstico para imprimir las claves en un formato legible"""
        print("\n=== Claves CURVE ===")
        print(f"Private Key: {z85.encode(self.private_key).decode('ascii')}")
        print(f"Public Key:  {z85.encode(self.public_key).decode('ascii')}")
        print(f"Peer Public: {z85.encode(self.peer_public_key).decode('ascii')}")
        print("=================\n")