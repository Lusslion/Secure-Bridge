import uvicorn
import asyncio
from secure_bridge import SecureBridge, app

async def setup_bridge():
    # Generar claves para pruebas
    secret, public = SecureBridge.generate_curve_keypair()
    peer_secret, peer_public = SecureBridge.generate_curve_keypair()
    
    # Crear instancia del puente
    bridge = SecureBridge(
        server_port=5555,
        client_port=5556,
        private_key=secret,
        public_key=public,
        peer_public_key=peer_public,
        jwt_secret="test_secret"
    )
    
    # Registrar handlers de ejemplo
    bridge.register_handler("sum", lambda data: {"result": data["a"] + data["b"]})
    bridge.register_handler("echo", lambda data: data)
    
    # Iniciar la rotación JWT
    await bridge.init_jwt_rotation()
    
    return bridge

def main():
    # Configurar el bridge de forma asíncrona
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    bridge = loop.run_until_complete(setup_bridge())
    
    # Iniciar el servidor FastAPI
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main()
