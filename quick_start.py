import os
import asyncio
import subprocess
from examples.generate_keys import generate_and_save_keys

async def quick_start():
    # 1. Verificar prerequisitos
    try:
        import zmq
        print("✓ ZeroMQ instalado correctamente")
    except ImportError:
        print("⨯ ZeroMQ no encontrado. Instálalo con:")
        print("  Ubuntu/Debian: sudo apt-get install libzmq3-dev")
        print("  MacOS: brew install zeromq")
        return

    # 2. Generar claves
    print("\nGenerando claves...")
    keys = generate_and_save_keys()
    print("✓ Claves generadas correctamente")

    # 3. Iniciar servidor en segundo plano
    print("\nIniciando servidor...")
    server_process = subprocess.Popen(
        ["python", "examples/server.py"],
        stdout=subprocess.PIPE
    )
    await asyncio.sleep(2)  # Esperar que el servidor inicie

    # 4. Ejecutar cliente de prueba
    print("\nProbando cliente...")
    try:
        subprocess.run(["python", "examples/client.py"])
        print("✓ Prueba completada correctamente")
    finally:
        server_process.terminate()

if __name__ == "__main__":
    print("=== Inicio Rápido Secure Bridge ===\n")
    asyncio.run(quick_start())
