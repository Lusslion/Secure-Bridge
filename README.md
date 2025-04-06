# Secure Bridge

Puente seguro para comunicación entre servicios Python y Node.js

## Instalación

```bash
# Clonar el repositorio
git clone https://github.com/Lusslion/Secure-Bridge.git
cd secure-bridge

# Configurar entorno Python
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configurar Node.js (si usas la parte de Node)
npm install
```

```bash
pip install -e .
```

## Uso Básico

```python
from secure_bridge import SecureBridge

# Generar claves
secret, public = SecureBridge.generate_curve_keypair()

# Crear instancia
bridge = SecureBridge(
    server_port=5555,
    client_port=5556,
    private_key=secret,
    public_key=public,
    peer_public_key=peer_public,
    jwt_secret="secreto"
)

# Registrar operaciones
bridge.register_handler("mi_operacion", mi_handler)

# Iniciar servidor
await bridge.start_server()
```

## Características

- Comunicación segura con ZeroMQ y CURVE
- Autenticación JWT
- Circuit breaker incorporado
- Métricas Prometheus
- Logs estructurados
- Serialización múltiple (JSON, MsgPack, Protobuf)
