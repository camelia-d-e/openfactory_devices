from unittest.mock import MagicMock

import pytest

from dust_trak.dust_trak_sniffer import DustTrakSniffer


@pytest.fixture
def sniffer():
    initializer = MagicMock()
    return DustTrakSniffer(
        network_interface="Ethernet 4",
        device_ip="169.254.66.117",
        initializer=initializer,
        data_export_type="openfactory",
        current_dir="/fake/dir",
    )


class TestGetLatestData:
    def test_returns_initial_zeros(self, sniffer):
        assert sniffer.get_latest_data() == {
            "pm1_concentration": 0.0,
            "pm2_5_concentration": 0.0,
            "pm4_concentration": 0.0,
            "pm10_concentration": 0.0,
        }

    def test_returns_updated_data(self, sniffer):
        sniffer.latest_data["pm1_concentration"] = 1.5
        assert sniffer.get_latest_data()["pm1_concentration"] == 1.5