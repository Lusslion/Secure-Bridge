from setuptools import setup, find_packages

setup(
    name="secure-bridge",
    version="0.1.0",
    packages=find_packages(),
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
