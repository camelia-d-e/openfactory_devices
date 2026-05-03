from dust_trak.dust_trak_server import DustTrakServer
import pytest
import pytest_asyncio
from unittest.mock import MagicMock, patch


ANY_VALID_DATA = {
    "pm1_concentration": 1.5,
    "pm2_5_concentration": 2.3,
    "pm4_concentration": 3.1,
    "pm10_concentration": 4.8,
}


@pytest.fixture
def mock_adapter():
    adapter = MagicMock()
    adapter.read_data.return_value = ANY_VALID_DATA.copy()
    return adapter


@pytest_asyncio.fixture
async def server(opcua_endpoint, mock_adapter):
    with patch("dust_trak.dust_trak_server.DustTrak", return_value=mock_adapter):
        s = DustTrakServer(endpoint=opcua_endpoint)
        await s.start()
        yield s
        await s.stop()


class TestDustTrakServerInit:

    @pytest.mark.asyncio
    async def test_all_variables_registered(self, server):
        expected = {
            "DustTrak.pm1_concentration",
            "DustTrak.pm2_5_concentration",
            "DustTrak.pm4_concentration",
            "DustTrak.pm10_concentration",
        }
        assert expected.issubset(server.variables.keys())

    @pytest.mark.asyncio
    async def test_no_avail_variable(self, server):
        assert "DustTrak.avail" not in server.variables

    @pytest.mark.asyncio
    async def test_equipment_node_created(self, server):
        assert "DustTrak" in server.equipment_nodes


class TestDustTrakServerPublishing:

    async def _publish(self, server):
        data = server.adapter.read_data()
        for key, value in data.items():
            await server.set_value("DustTrak", key, value)

    @pytest.mark.asyncio
    async def test_publishes_pm1(self, server):
        await self._publish(server)
        assert await server.get_value("DustTrak", "pm1_concentration") == 1.5

    @pytest.mark.asyncio
    async def test_publishes_all_pm_values(self, server):
        await self._publish(server)
        assert await server.get_value("DustTrak", "pm2_5_concentration") == 2.3
        assert await server.get_value("DustTrak", "pm4_concentration") == 3.1
        assert await server.get_value("DustTrak", "pm10_concentration") == 4.8

    @pytest.mark.asyncio
    async def test_handles_empty_data_gracefully(self, server, mock_adapter):
        mock_adapter.read_data.return_value = {}
        data = server.adapter.read_data()
        for key, value in data.items():
            await server.set_value("DustTrak", key, value)

    @pytest.mark.asyncio
    async def test_values_update_on_successive_reads(self, server, mock_adapter):
        await self._publish(server)
        assert await server.get_value("DustTrak", "pm1_concentration") == 1.5

        mock_adapter.read_data.return_value = {**ANY_VALID_DATA, "pm1_concentration": 9.9}
        await self._publish(server)
        assert await server.get_value("DustTrak", "pm1_concentration") == 9.9

    @pytest.mark.asyncio
    async def test_start_capture_called_on_start(self, server, mock_adapter):
        """start_capture should be called during server startup."""
        mock_adapter.start_capture.assert_called_once()