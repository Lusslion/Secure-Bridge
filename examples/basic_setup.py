from secure_bridge import SecureBridge
import asyncio
import json

async def setup_example():
    # 1. Generar claves
    service1_secret, service1_public = SecureBridge.generate_curve_keypair()
    service2_secret, service2_public = SecureBridge.generate_curve_keypair()
    
    # Guardar claves (en producción usar almacenamiento seguro)
    with open('keys.json', 'w') as f:
        json.dump({
            'service1': {
                'secret': service1_secret,
                'public': service1_public
            },
            'service2': {
                'secret': service2_secret,
                'public': service2_public
            }
        }, f, indent=2)
    
    print("Claves generadas y guardadas en keys.json")
    
    # 2. Ejemplo de configuración básica
    bridge = SecureBridge(
        server_port=5555,
        client_port=5556,
        private_key=service1_secret,
        public_key=service1_public,
        peer_public_key=service2_public,
        jwt_secret="ejemplo_secreto"
    )
    
    return bridge

if __name__ == "__main__":
    asyncio.run(setup_example())
