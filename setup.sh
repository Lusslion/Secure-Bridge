#!/bin/bash

# Crear entorno virtual
python -m venv venv

# Activar el entorno virtual
source venv/bin/activate

# Actualizar pip
pip install --upgrade pip

# Instalar dependencias
pip install -r requirements.txt

# Mostrar dependencias instaladas
pip list

echo "Entorno virtual creado y dependencias instaladas!"
