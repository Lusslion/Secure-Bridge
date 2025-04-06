from secure_bridge import SecureBridge
import asyncio

async def main():
    try:
        # Generar claves para pruebas
        secret, public = SecureBridge.generate_curve_keypair()
        peer_secret, peer_public = SecureBridge.generate_curve_keypair()
        
        print("Claves generadas:")
        print(f"Secret: {secret[:10]}...")
        print(f"Public: {public[:10]}...")
        
        # Crear instancia del puente
        bridge = SecureBridge(
            server_port=5555,
            client_port=5556,
            private_key=secret,
            public_key=public,
            peer_public_key=peer_public,
            jwt_secret="test_secret"
        )
        
        # Registrar un manejador de prueba
        bridge.register_handler("sum", lambda data: {"result": data["a"] + data["b"]})
        
        # Iniciar el servidor en segundo plano
        server_task = asyncio.create_task(bridge.start_server())
        
        # Esperar un momento para que el servidor inicie
        await asyncio.sleep(1)
        
        # Probar el cliente
        result = await bridge.start_client({
            "operation": "sum",
            "token": "test_token",
            "data": {"a": 5, "b": 3}
        })
        
        print("Resultado:", result)
        
        # Cerrar todo
        await asyncio.sleep(1)
        bridge.shutdown()
    
    except Exception as e:
        print(f"Error durante la ejecución: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
