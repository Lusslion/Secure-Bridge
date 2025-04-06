import asyncio
import json
from secure_bridge import SecureBridge

async def run_server():
    # Cargar claves
    with open("keys/keys.json") as f:
        keys = json.load(f)
    
    # Configurar servidor
    bridge = SecureBridge(
        server_port=5555,
        client_port=5556,
        private_key=keys["service1"]["secret"],
        public_key=keys["service1"]["public"],
        peer_public_key=keys["service2"]["public"],
        jwt_secret="mi_secreto_jwt"
    )
    
    # Ejemplo de handler
    def suma_handler(data):
        a, b = data["a"], data["b"]
        return {"resultado": a + b}
    
    bridge.register_handler("suma", suma_handler)
    print("Servidor iniciado en puerto 5555")
    await bridge.start_server()

if __name__ == "__main__":
    asyncio.run(run_server())
