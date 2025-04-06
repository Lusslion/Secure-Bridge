# Secure Bridge

Puente seguro para comunicación entre servicios Python y Node.js

## Prerequisitos

- Python 3.7+
- Node.js 14+ (para la versión TypeScript)
- ZeroMQ (libzmq)

### Instalar ZeroMQ

```bash
# Ubuntu/Debian
sudo apt-get install libzmq3-dev

# MacOS
brew install zeromq

# Windows
# Descargar el instalador de http://zeromq.org/download
```

## Instalación

### Python

```bash
# Clonar el repositorio
git clone https://github.com/Lusslion/Secure-Bridge.git
cd secure-bridge

# Configurar entorno Python
python -m venv venv
source venv/bin/activate  # En Windows: .\venv\Scripts\activate
pip install -r requirements.txt
```

### Node.js

```bash
npm install secure-bridge zeromq@6 jsonwebtoken
```

## Ejemplo Rápido

```bash
# 1. Generar claves
python examples/generate_keys.py

# 2. Iniciar el servidor en una terminal
python examples/server.py

# 3. En otra terminal, ejecutar el cliente
python examples/client.py
```

## Estructura de Ejemplos
```
examples/
├── generate_keys.py  # Genera y guarda claves
├── server.py        # Ejemplo de servidor
└── client.py        # Ejemplo de cliente
```

## Guía Paso a Paso

### 1. Generar Claves

Primero necesitas generar las claves para ambos servicios:

```python
from secure_bridge import SecureBridge

# Servicio 1
service1_secret, service1_public = SecureBridge.generate_curve_keypair()

# Servicio 2
service2_secret, service2_public = SecureBridge.generate_curve_keypair()

# Guardar las claves de forma segura
print(f"""
Servicio 1:
  Privada: {service1_secret}
  Pública: {service1_public}

Servicio 2:
  Privada: {service2_secret}
  Pública: {service2_public}
""")
```

### 2. Configurar el Servidor

```python
# servidor.py
import asyncio
from secure_bridge import SecureBridge

async def main():
    bridge = SecureBridge(
        server_port=5555,
        client_port=5556,
        private_key=service1_secret,     # Tu clave privada
        public_key=service1_public,      # Tu clave pública
        peer_public_key=service2_public, # Clave pública del otro servicio
        jwt_secret="tu_secreto_jwt"      # Secreto para tokens JWT
    )
    
    # Definir manejadores
    def suma_handler(data):
        return {"resultado": data["a"] + data["b"]}
    
    bridge.register_handler("suma", suma_handler)
    
    # Iniciar rotación JWT y servidor
    await bridge.init_jwt_rotation()
    await bridge.start_server()

if __name__ == "__main__":
    asyncio.run(main())
```

### 3. Configurar el Cliente

```python
# cliente.py
import asyncio
from secure_bridge import SecureBridge

async def main():
    bridge = SecureBridge(
        server_port=5556,          # Puerto del servidor destino
        client_port=5555,          # Puerto local
        private_key=service2_secret,     # Tu clave privada
        public_key=service2_public,      # Tu clave pública
        peer_public_key=service1_public, # Clave pública del servidor
        jwt_secret="tu_secreto_jwt"      # El mismo secreto JWT
    )

    # Enviar petición
    resultado = await bridge.start_client({
        "operation": "suma",
        "token": "tu_jwt_token",  # Generar un token JWT válido
        "data": {"a": 5, "b": 3}
    })
    
    print(resultado)  # {"status": "success", "data": {"resultado": 8}}

if __name__ == "__main__":
    asyncio.run(main())
```

## Consideraciones de Seguridad

1. **Claves**: 
   - Guarda las claves de forma segura
   - No compartas las claves privadas
   - Rota las claves periódicamente

2. **JWT**:
   - Usa secretos fuertes para JWT
   - Implementa expiración de tokens
   - Rota los secretos JWT regularmente

3. **Puertos**:
   - Usa firewalls para restringir acceso
   - Configura SSL/TLS si es necesario
   - No expongas los puertos públicamente sin seguridad adicional

## Características

- Comunicación segura con ZeroMQ y CURVE
- Autenticación JWT
- Circuit breaker incorporado
- Métricas Prometheus
- Logs estructurados
- Serialización múltiple (JSON, MsgPack, Protobuf)
