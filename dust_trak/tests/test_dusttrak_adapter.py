from dust_trak.dust_trak_adapter import DustTrak
import pytest # type: ignore
import json
from unittest.mock import patch, mock_open

MOCK_CONFIG = {
    "data_export_type": "openfactory",
    "device_ip": "169.254.66.117",
    "numberOfReadings": 5,
}


def make_adapter(mock_pyautogui, mock_pyshark, config=None):
    cfg = config or MOCK_CONFIG
    with patch("builtins.open", mock_open(read_data=json.dumps(cfg))):
        with patch("dust_trak.dust_trak_adapter.os.path.dirname", return_value="/fake/dir"):
            with patch.object(DustTrak, "launch_dust_trak_monitoring"):  # prevent GUI calls
                adapter = DustTrak()
    return adapter


class TestDustTrakInit:

    @patch("dust_trak.dust_trak_adapter.pyshark")
    @patch("dust_trak.dust_trak_adapter.pyautogui")
    def test_initialises_latest_data(self, mock_pyautogui, mock_pyshark):
        adapter = make_adapter(mock_pyautogui, mock_pyshark)
        assert adapter.latest_data["pm1_concentration"] == 0.0
        assert adapter.latest_data["pm2_5_concentration"] == 0.0
        assert adapter.latest_data["pm4_concentration"] == 0.0
        assert adapter.latest_data["pm10_concentration"] == 0.0

    @patch("dust_trak.dust_trak_adapter.pyshark")
    @patch("dust_trak.dust_trak_adapter.pyautogui")
    def test_sets_device_ip(self, mock_pyautogui, mock_pyshark):
        adapter = make_adapter(mock_pyautogui, mock_pyshark)
        assert adapter.device_ip == "169.254.66.117"

    @patch("dust_trak.dust_trak_adapter.pyshark")
    @patch("dust_trak.dust_trak_adapter.pyautogui")
    def test_reads_config_number_of_readings(self, mock_pyautogui, mock_pyshark):
        adapter = make_adapter(mock_pyautogui, mock_pyshark)
        assert adapter.readings_average_num == MOCK_CONFIG["numberOfReadings"]


class TestDustTrakReadData:

    @patch("dust_trak.dust_trak_adapter.pyshark")
    @patch("dust_trak.dust_trak_adapter.pyautogui")
    def test_returns_copy_of_latest_data(self, mock_pyautogui, mock_pyshark):
        adapter = make_adapter(mock_pyautogui, mock_pyshark)
        data = adapter.read_data()
        assert data is not adapter.latest_data

    @patch("dust_trak.dust_trak_adapter.pyshark")
    @patch("dust_trak.dust_trak_adapter.pyautogui")
    def test_returns_all_concentration_keys(self, mock_pyautogui, mock_pyshark):
        adapter = make_adapter(mock_pyautogui, mock_pyshark)
        data = adapter.read_data()
        assert set(data.keys()) == {
            "pm1_concentration",
            "pm2_5_concentration",
            "pm4_concentration",
            "pm10_concentration",
        }


class TestDustTrakParseHexData:

    @patch("dust_trak.dust_trak_adapter.pyshark")
    @patch("dust_trak.dust_trak_adapter.pyautogui")
    def test_parses_valid_hex_payload(self, mock_pyautogui, mock_pyshark):
        adapter = make_adapter(mock_pyautogui, mock_pyshark)
        # simulate dust_trak msg: ",1.0,2.0,3.0,4.0,"
        raw = ",1.0,2.0,3.0,4.0,".encode("utf-8").hex()
        hex_payload = ":".join(raw[i:i+2] for i in range(0, len(raw), 2))
        result = adapter.parse_hex_data(hex_payload)
        assert result == ["1.0", "2.0", "3.0", "4.0"]

    @patch("dust_trak.dust_trak_adapter.pyshark")
    @patch("dust_trak.dust_trak_adapter.pyautogui")
    def test_returns_empty_string_list_on_invalid_hex(self, mock_pyautogui, mock_pyshark):
        adapter = make_adapter(mock_pyautogui, mock_pyshark)
        result = adapter.parse_hex_data("zz:zz:zz")
        assert result == [""]


class TestDustTrakConvertToPercent:

    @patch("dust_trak.dust_trak_adapter.pyshark")
    @patch("dust_trak.dust_trak_adapter.pyautogui")
    def test_converts_correctly(self, mock_pyautogui, mock_pyshark):
        adapter = make_adapter(mock_pyautogui, mock_pyshark)
        result = adapter.convert_to_percent(["1225000"])
        assert pytest.approx(result[0], rel=1e-3) == 100.0

    @patch("dust_trak.dust_trak_adapter.pyshark")
    @patch("dust_trak.dust_trak_adapter.pyautogui")
    def test_returns_zero_on_invalid_value(self, mock_pyautogui, mock_pyshark):
        adapter = make_adapter(mock_pyautogui, mock_pyshark)
        result = adapter.convert_to_percent(["not_a_number"])
        assert result == [0.0]

    @patch("dust_trak.dust_trak_adapter.pyshark")
    @patch("dust_trak.dust_trak_adapter.pyautogui")
    def test_converts_multiple_values(self, mock_pyautogui, mock_pyshark):
        adapter = make_adapter(mock_pyautogui, mock_pyshark)
        result = adapter.convert_to_percent(["0", "612500", "1225000", "306250"])
        assert pytest.approx(result[0]) == 0.0
        assert pytest.approx(result[1], rel=1e-3) == 50.0
        assert pytest.approx(result[2], rel=1e-3) == 100.0
        assert pytest.approx(result[3], rel=1e-3) == 25.0


class TestDustTrakIsEmptyData:

    @patch("dust_trak.dust_trak_adapter.pyshark")
    @patch("dust_trak.dust_trak_adapter.pyautogui")
    def test_all_zeros_is_empty(self, mock_pyautogui, mock_pyshark):
        adapter = make_adapter(mock_pyautogui, mock_pyshark)
        assert adapter.is_empty_data(["0.0", "0.0", "0.0", "0.0"]) is True

    @patch("dust_trak.dust_trak_adapter.pyshark")
    @patch("dust_trak.dust_trak_adapter.pyautogui")
    def test_all_91_is_empty(self, mock_pyautogui, mock_pyshark):
        """91.0 is a known sentinel value treated as empty."""
        adapter = make_adapter(mock_pyautogui, mock_pyshark)
        assert adapter.is_empty_data(["91.0", "91.0", "91.0", "91.0"]) is True

    @patch("dust_trak.dust_trak_adapter.pyshark")
    @patch("dust_trak.dust_trak_adapter.pyautogui")
    def test_real_data_is_not_empty(self, mock_pyautogui, mock_pyshark):
        adapter = make_adapter(mock_pyautogui, mock_pyshark)
        assert adapter.is_empty_data(["1.5", "2.3", "0.8", "3.1"]) is False


class TestDustTrakIsDataUpdated:

    @patch("dust_trak.dust_trak_adapter.pyshark")
    @patch("dust_trak.dust_trak_adapter.pyautogui")
    def test_same_data_is_not_updated(self, mock_pyautogui, mock_pyshark):
        adapter = make_adapter(mock_pyautogui, mock_pyshark)
        adapter.latest_data = {
            "pm1_concentration": 1.0,
            "pm2_5_concentration": 2.0,
            "pm4_concentration": 3.0,
            "pm10_concentration": 4.0,
        }
        assert adapter.is_data_updated([1.0, 2.0, 3.0, 4.0]) is False

    @patch("dust_trak.dust_trak_adapter.pyshark")
    @patch("dust_trak.dust_trak_adapter.pyautogui")
    def test_different_data_is_updated(self, mock_pyautogui, mock_pyshark):
        adapter = make_adapter(mock_pyautogui, mock_pyshark)
        adapter.latest_data = {
            "pm1_concentration": 1.0,
            "pm2_5_concentration": 2.0,
            "pm4_concentration": 3.0,
            "pm10_concentration": 4.0,
        }
        assert adapter.is_data_updated([1.0, 2.0, 3.0, 99.0]) is True

class TestDustTrakCapture:

    @patch("dust_trak.dust_trak_adapter.pyshark")
    @patch("dust_trak.dust_trak_adapter.pyautogui")
    def test_start_capture_sets_running_true(self, mock_pyautogui, mock_pyshark):
        adapter = make_adapter(mock_pyautogui, mock_pyshark)
        with patch.object(adapter, "_capture_loop"):
            adapter.start_capture()
            assert adapter.running is True

    @patch("dust_trak.dust_trak_adapter.pyshark")
    @patch("dust_trak.dust_trak_adapter.pyautogui")
    def test_start_capture_only_starts_once(self, mock_pyautogui, mock_pyshark):
        adapter = make_adapter(mock_pyautogui, mock_pyshark)
        with patch.object(adapter, "_capture_loop"):
            adapter.start_capture()
            thread1 = adapter.capture_thread
            adapter.start_capture()  # second call should do nothing
            assert adapter.capture_thread is thread1

    @patch("dust_trak.dust_trak_adapter.pyshark")
    @patch("dust_trak.dust_trak_adapter.pyautogui")
    def test_stop_capture_sets_running_false(self, mock_pyautogui, mock_pyshark):
        adapter = make_adapter(mock_pyautogui, mock_pyshark)
        with patch.object(adapter, "_capture_loop"):
            adapter.start_capture()
            adapter.stop_capture()
            assert adapter.running is False