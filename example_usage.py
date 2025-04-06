from secure_bridge import SecureBridge
import asyncio

async def ejemplo_servidor():
    # Generar claves
    secret, public = SecureBridge.generate_curve_keypair()
    peer_secret, peer_public = SecureBridge.generate_curve_keypair()
    
    # Crear puente
    bridge = SecureBridge(
        server_port=5555,
        client_port=5556,
        private_key=secret,
        public_key=public,
        peer_public_key=peer_public,
        jwt_secret="tu_secreto_jwt"
    )
    
    # Registrar tus propios handlers
    bridge.register_handler("mi_operacion", lambda data: {
        "resultado": data["valor"] * 2
    })
    
    # Iniciar el servidor
    await bridge.init_jwt_rotation()
    await bridge.start_server()

# Para usar en tu proyecto:
"""
1. Instalar el paquete:
pip install -e .

2. Importar y usar:
from secure_bridge import SecureBridge

3. Implementar tus handlers:
bridge.register_handler("mi_operacion", mi_funcion_handler)

4. Iniciar el servidor:
asyncio.run(bridge.start_server())

5. Para enviar mensajes como cliente:
resultado = await bridge.start_client({
    "operation": "mi_operacion",
    "token": "token_jwt",
    "data": {"valor": 42}
})
"""
