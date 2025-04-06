from secure_bridge import SecureBridge
import asyncio

async def test_keys():
    # Generar par de claves para el servidor
    server_secret, server_public = SecureBridge.generate_curve_keypair()
    print("\n=== Claves Generadas para Servidor ===")
    print(f"Secret: {server_secret}")
    print(f"Public: {server_public}")

    # Generar par de claves para el cliente
    client_secret, client_public = SecureBridge.generate_curve_keypair()
    print("\n=== Claves Generadas para Cliente ===")
    print(f"Secret: {client_secret}")
    print(f"Public: {client_public}")

    # Crear instancia de prueba
    bridge = SecureBridge(
        server_port=5555,
        client_port=5556,
        private_key=server_secret,
        public_key=server_public,
        peer_public_key=client_public,
        jwt_secret="test_secret"
    )

    # Verificar las claves
    bridge.print_keys()

    return bridge

if __name__ == "__main__":
    bridge = asyncio.run(test_keys())
    print("Prueba de claves completada!")
