# Publicación en PyPI

1. Instalar herramientas de publicación:
```bash
pip install twine build
```

2. Construir distribución:
```bash
python -m build
```

3. Verificar distribución:
```bash
twine check dist/*
```

4. Publicar en TestPyPI (opcional):
```bash
twine upload --repository testpypi dist/*
```

5. Publicar en PyPI:
```bash
twine upload dist/*
```

## Actualización de Versión

1. Actualizar versión en `setup.py`
2. Crear nueva distribución
3. Subir a PyPI

## Configuración de Credenciales

Crear archivo `~/.pypirc`:
```ini
[pypi]
username = __token__
password = your-token-here
```
