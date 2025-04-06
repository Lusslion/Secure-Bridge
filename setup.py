from setuptools import setup, find_packages

setup(
    name="secure-bridge",
    version="0.1.1",  # Incrementamos la versión
    packages=find_packages(),
    author="Lusslion",
    author_email="tu@email.com",
    description="Puente seguro para comunicación entre servicios Python y Node.js",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Lusslion/Secure-Bridge",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Framework :: FastAPI",
    ],
    python_requires=">=3.7",
    install_requires=[
        "fastapi",
        "uvicorn",
        "pyzmq",
        "pyjwt",
        "msgpack",
        "protobuf",
        "circuitbreaker",
        "structlog",
        "cryptography",
        "prometheus_client"
    ]
)
