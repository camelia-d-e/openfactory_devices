import pytest
import pytest_asyncio
from opcua_base.opcua_server import OPCUAServer
 
@pytest_asyncio.fixture(scope="session")
async def server():
    s = OPCUAServer(endpoint="opc.tcp://localhost:14850")
    await s.start()
    await s.create_equipment_node("TestDevice")
    await s.create_equipment_node("TestDevice2")
    yield s
    await s.stop()
 
@pytest.mark.asyncio
async def test_create_equipment_node(server):
    assert "TestDevice" in server.equipment_nodes
 
@pytest.mark.asyncio
async def test_add_and_get_variable(server):
    await server.add_variable("TestDevice2", "temperature", 0.0, writable=True)
    await server.set_value("TestDevice2", "temperature", 42.0)
    assert await server.get_value("TestDevice2", "temperature") == 42.0
 
@pytest.mark.asyncio
async def test_unknown_equipment_raises(server):
    with pytest.raises(ValueError):
        await server.add_variable("NonExistent", "temperature", 0.0)