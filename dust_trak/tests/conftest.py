import pytest


@pytest.fixture
def opcua_endpoint():
    return "opc.tcp://localhost:4841"