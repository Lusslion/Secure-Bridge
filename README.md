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

## Instalación como Dependencia

### Opción 1: Usando pip desde PyPI

```bash
pip install secure-bridge
```

### Opción 2: Usando pip con Git

```bash
pip install git+https://github.com/Lusslion/Secure-Bridge.git
```

### Opción 3: Agregando a requirements.txt

```txt
secure-bridge @ git+https://github.com/Lusslion/Secure-Bridge.git
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

## Uso en Otros Proyectos

### Python

```python
from secure_bridge import SecureBridge

async def mi_servicio():
    # Generar o cargar claves existentes
    secret, public = SecureBridge.generate_curve_keypair()
    peer_secret, peer_public = SecureBridge.generate_curve_keypair()

    # Configurar el bridge
    bridge = SecureBridge(
        server_port=5555,
        client_port=5556,
        private_key=secret,
        public_key=public,
        peer_public_key=peer_public,
        jwt_secret="mi_secreto"
    )

    # Definir handlers para las operaciones
    def handler_suma(data):
        return {"resultado": data["a"] + data["b"]}

    # Registrar handlers
    bridge.register_handler("suma", handler_suma)

    # Iniciar el servidor
    await bridge.init_jwt_rotation()
    await bridge.start_server()

# Como cliente
async def ejemplo_cliente():
    bridge = SecureBridge(...)
    resultado = await bridge.start_client({
        "operation": "suma",
        "token": "tu_jwt_token",
        "data": {"a": 5, "b": 3}
    })
    print(resultado)  # {"resultado": 8}
```

### TypeScript/Node.js

```typescript
import { SecureBridge } from 'secure-bridge';

// Como servidor
const bridge = new SecureBridge({
    serverPort: 5555,
    clientPort: 5556,
    privateKey: 'tu_clave_privada',
    publicKey: 'tu_clave_publica',
    peerPublicKey: 'clave_publica_par',
    jwtSecret: 'tu_secreto'
});

bridge.registerHandler('suma', (data) => {
    return { resultado: data.a + data.b };
});

bridge.startServer();

// Como cliente
const resultado = await bridge.startClient({
    operation: 'suma',
    token: 'tu_jwt_token',
    data: { a: 5, b: 3 }
});
console.log(resultado); // { resultado: 8 }
```

## Características

- Comunicación segura con ZeroMQ y CURVE
- Autenticación JWT
- Circuit breaker incorporado
- Métricas Prometheus
- Logs estructurados
- Serialización múltiple (JSON, MsgPack, Protobuf)

