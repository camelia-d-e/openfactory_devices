import json
import threading
from unittest.mock import MagicMock, mock_open, patch

import pytest

from dust_trak.dust_trak_adapter import DustTrak
from dust_trak.dust_trak_initializer import DustTrakInitializer

MOCK_CONFIG = {
    "data_export_type": "openfactory",
    "device_ip": "169.254.66.117",
    "numberOfReadings": 5,
}


@pytest.fixture
def adapter():
    with (
        patch("builtins.open", mock_open(read_data=json.dumps(MOCK_CONFIG))),
        patch("dust_trak.dust_trak_adapter.os.path.dirname", return_value="/fake/dir"),
        patch.object(DustTrakInitializer, "launch_dust_trak_monitoring"),
    ):
        return DustTrak()


@pytest.fixture
def virtual_adapter():
    with (
        patch("builtins.open", mock_open(read_data=json.dumps(MOCK_CONFIG))),
        patch("dust_trak.dust_trak_adapter.os.path.dirname", return_value="/fake/dir"),
    ):
        return DustTrak(virtual=True)


class TestInit:
    def test_latest_data_zeros(self, adapter):
        assert adapter.latest_data == {
            "pm1_concentration": 0.0,
            "pm2_5_concentration": 0.0,
            "pm4_concentration": 0.0,
            "pm10_concentration": 0.0,
        }

    def test_device_ip(self, adapter):
        assert adapter.device_ip == MOCK_CONFIG["device_ip"]

    def test_number_of_readings(self, adapter):
        assert adapter.initializer.readings_average_num == MOCK_CONFIG["numberOfReadings"]

    def test_not_running(self, adapter):
        assert adapter.running is False

    def test_capture_thread_none(self, adapter):
        assert adapter.capture_thread is None

    def test_virtual_skips_monitoring(self, virtual_adapter):
        assert virtual_adapter.virtual is True


class TestReadDataVirtual:
    def test_returns_copy(self, virtual_adapter):
        assert virtual_adapter.read_data() is not virtual_adapter.latest_data

    def test_returns_all_keys(self, virtual_adapter):
        assert set(virtual_adapter.read_data().keys()) == {
            "pm1_concentration",
            "pm2_5_concentration",
            "pm4_concentration",
            "pm10_concentration",
        }

    def test_values_within_range(self, virtual_adapter):
        for _ in range(10):
            for v in virtual_adapter.read_data().values():
                assert 0.0 <= v <= 0.5


class TestReadDataReal:
    def test_returns_sniffer_data(self, adapter):
        adapter.sniffer.latest_data = {
            "pm1_concentration": 1.1,
            "pm2_5_concentration": 2.2,
            "pm4_concentration": 3.3,
            "pm10_concentration": 4.4,
        }
        assert adapter.read_data() == adapter.sniffer.latest_data

    def test_returns_copy_not_reference(self, adapter):
        assert adapter.read_data() is not adapter.sniffer.latest_data

    def test_csv_written_when_export_type_csv(self, adapter):
        adapter.data_export_type = "csv"
        adapter.csv_logger.write_to_csv = MagicMock()
        adapter.read_data()
        adapter.csv_logger.write_to_csv.assert_called_once()

    def test_csv_not_written_for_openfactory_type(self, adapter):
        adapter.csv_logger.write_to_csv = MagicMock()
        adapter.read_data()
        adapter.csv_logger.write_to_csv.assert_not_called()


class TestCapture:
    def test_start_sets_running(self, adapter):
        with patch.object(adapter.sniffer, "run_capture"):
            adapter.start_capture()
            assert adapter.running is True

    def test_start_creates_thread(self, adapter):
        with patch.object(adapter.sniffer, "run_capture"):
            adapter.start_capture()
            assert isinstance(adapter.capture_thread, threading.Thread)

    def test_start_only_once(self, adapter):
        with patch.object(adapter.sniffer, "run_capture"):
            adapter.start_capture()
            first_thread = adapter.capture_thread
            adapter.start_capture()
            assert adapter.capture_thread is first_thread

    def test_stop_sets_running_false(self, adapter):
        with patch.object(adapter.sniffer, "run_capture"):
            adapter.start_capture()
            adapter.stop_capture()
            assert adapter.running is False