import pytest

def test_circuit_breaker():
    bridge = SecureBridge(...)
    with pytest.raises(Exception):
        for _ in range(5):
            bridge.start_client({"operation": "fail"})
