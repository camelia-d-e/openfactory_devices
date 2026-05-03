import pytest
import pytest_asyncio
from unittest.mock import MagicMock, patch

from wtvb01.wtvb01_server import WTVB01Server


ANY_VALID_DATA = {
    "temp": 25.0,
    "acc_x": 980.665,
    "acc_y": 0.0,
    "acc_z": 9806.65,
    "vx": 1.2,
    "vy": 0.8,
    "vz": 0.3,
    "angle_x": 10.0,
    "angle_y": 5.0,
    "angle_z": 0.0,
    "dx": 0.5,
    "dy": 0.2,
    "dz": 0.1,
    "hx": 50.0,
    "hy": 60.0,
    "hz": 55.0,
}


@pytest.fixture
def mock_adapter():
    adapter = MagicMock()
    adapter.read_data.return_value = ANY_VALID_DATA.copy()
    return adapter


@pytest_asyncio.fixture
async def server(opcua_endpoint, mock_adapter):
    with patch("wtvb01.wtvb01_server.WTVB01", return_value=mock_adapter):
        s = WTVB01Server(endpoint=opcua_endpoint)
        await s.start()
        yield s
        await s.stop()


class TestWTVB01ServerInit:

    @pytest.mark.asyncio
    async def test_all_variables_registered(self, server):
        expected = {
            "WTVB01.temp", "WTVB01.acc_x", "WTVB01.acc_y", "WTVB01.acc_z",
            "WTVB01.vx", "WTVB01.vy", "WTVB01.vz",
            "WTVB01.angle_x", "WTVB01.angle_y", "WTVB01.angle_z",
            "WTVB01.dx", "WTVB01.dy", "WTVB01.dz",
            "WTVB01.hx", "WTVB01.hy", "WTVB01.hz",
        }
        assert expected.issubset(server.variables.keys())

    @pytest.mark.asyncio
    async def test_no_avail_variable(self, server):
        assert "WTVB01.avail" not in server.variables

    @pytest.mark.asyncio
    async def test_equipment_node_created(self, server):
        assert "WTVB01" in server.equipment_nodes


class TestWTVB01ServerPublishing:

    async def _publish(self, server):
        data = server.adapter.read_data()
        for key, value in data.items():
            await server.set_value("WTVB01", key, value)

    @pytest.mark.asyncio
    async def test_publishes_temp(self, server):
        await self._publish(server)
        assert await server.get_value("WTVB01", "temp") == 25.0

    @pytest.mark.asyncio
    async def test_publishes_all_axes(self, server):
        await self._publish(server)
        assert await server.get_value("WTVB01", "acc_x") == 980.665
        assert await server.get_value("WTVB01", "vx") == 1.2
        assert await server.get_value("WTVB01", "angle_x") == 10.0
        assert await server.get_value("WTVB01", "dx") == 0.5
        assert await server.get_value("WTVB01", "hx") == 50.0

    @pytest.mark.asyncio
    async def test_handles_empty_data_gracefully(self, server, mock_adapter):
        mock_adapter.read_data.return_value = {}
        data = server.adapter.read_data()
        for key, value in data.items():
            await server.set_value("WTVB01", key, value)

    @pytest.mark.asyncio
    async def test_values_update_on_successive_reads(self, server, mock_adapter):
        await self._publish(server)
        assert await server.get_value("WTVB01", "temp") == 25.0

        mock_adapter.read_data.return_value = {**ANY_VALID_DATA, "temp": 30.0}
        await self._publish(server)
        assert await server.get_value("WTVB01", "temp") == 30.0