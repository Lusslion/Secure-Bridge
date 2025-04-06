import asyncio
import json
from secure_bridge import SecureBridge

async def run_client():
    # Cargar claves
    with open("keys/keys.json") as f:
        keys = json.load(f)
    
    # Configurar cliente
    bridge = SecureBridge(
        server_port=5556,
        client_port=5555,
        private_key=keys["service2"]["secret"],
        public_key=keys["service2"]["public"],
        peer_public_key=keys["service1"]["public"],
        jwt_secret="mi_secreto_jwt"
    )
    
    # Enviar petición
    result = await bridge.start_client({
        "operation": "suma",
        "token": "tu_jwt_token",
        "data": {"a": 5, "b": 3}
    })
    
    print(f"Resultado: {result}")

if __name__ == "__main__":
    asyncio.run(run_client())
