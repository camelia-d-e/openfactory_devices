from unittest.mock import MagicMock, patch

import pytest

from wtvb01.wtvb01_adapter import WTVB01


def make_mocked_adapter(mock_device_model, return_value=1.0, is_open=True):
    """Instantiate a WTVB01 with a fully mocked DeviceModel."""
    mock_sensor = MagicMock()
    mock_sensor.isOpen = is_open
    mock_sensor.get.return_value = return_value
    mock_device_model.return_value = mock_sensor
    return WTVB01(), mock_sensor

class TestWTVB01Init:

    @patch("wtvb01.wtvb01_adapter.DeviceModel")
    def test_opens_device_on_init(self, mock_device_model):
        adapter, mock_sensor = make_mocked_adapter(mock_device_model)
        mock_sensor.openDevice.assert_called_once()

    @patch("wtvb01.wtvb01_adapter.DeviceModel")
    def test_starts_loop_read_on_init(self, mock_device_model):
        adapter, mock_sensor = make_mocked_adapter(mock_device_model)
        mock_sensor.startLoopRead.assert_called_once()


class TestWTVB01ReadData:

    @patch("wtvb01.wtvb01_adapter.DeviceModel")
    def test_returns_all_expected_keys(self, mock_device_model):
        adapter, _ = make_mocked_adapter(mock_device_model)
        data = adapter.read_data()
        expected_keys = {
            "temp",
            "acc_x", "acc_y", "acc_z",
            "vx", "vy", "vz",
            "angle_x", "angle_y", "angle_z",
            "dx", "dy", "dz",
            "hx", "hy", "hz",
        }
        assert expected_keys.issubset(data.keys())

    @patch("wtvb01.wtvb01_adapter.DeviceModel")
    def test_returns_empty_dict_on_io_error(self, mock_device_model):
        adapter, mock_sensor = make_mocked_adapter(mock_device_model)
        mock_sensor.get.side_effect = OSError("Serial read failed")
        data = adapter.read_data()
        assert data == {}

    @patch("wtvb01.wtvb01_adapter.DeviceModel")
    def test_no_avail_key_in_successful_read(self, mock_device_model):
        adapter, _ = make_mocked_adapter(mock_device_model)
        data = adapter.read_data()
        assert "avail" not in data

    @patch("wtvb01.wtvb01_adapter.DeviceModel")
    def test_no_avail_key_on_error(self, mock_device_model):
        adapter, mock_sensor = make_mocked_adapter(mock_device_model)
        mock_sensor.get.side_effect = OSError("Serial read failed")
        data = adapter.read_data()
        assert "avail" not in data

    @patch("wtvb01.wtvb01_adapter.DeviceModel")
    def test_acceleration_converted_to_mm_per_s2(self, mock_device_model):
        """1g should convert to 9806.65 mm/s^2"""
        adapter, mock_sensor = make_mocked_adapter(mock_device_model, return_value=1.0)
        data = adapter.read_data()
        assert pytest.approx(data["acc_x"], rel=1e-3) == 9806.65

    @patch("wtvb01.wtvb01_adapter.DeviceModel")
    def test_displacements_converted_to_mm(self, mock_device_model):
        """1000 microns should convert to 1.0 mm"""
        adapter, mock_sensor = make_mocked_adapter(mock_device_model, return_value=1000.0)
        data = adapter.read_data()
        assert pytest.approx(data["dx"], rel=1e-3) == 1.0

    @patch("wtvb01.wtvb01_adapter.DeviceModel")
    def test_none_id_fields_excluded(self, mock_device_model):
        """Fields with None MTConnect ID should not appear in output."""
        adapter, mock_sensor = make_mocked_adapter(mock_device_model)
        data = adapter.read_data()
        assert None not in data

class TestWTVB01Measurements:

    @patch("wtvb01.wtvb01_adapter.DeviceModel")
    def test_temperature_reads_correct_register(self, mock_device_model):
        adapter, mock_sensor = make_mocked_adapter(mock_device_model)
        adapter.temperature()
        mock_sensor.get.assert_called_with(str(adapter.TEMP_REGISTER))

    @patch("wtvb01.wtvb01_adapter.DeviceModel")
    def test_velocity_returns_three_axes(self, mock_device_model):
        adapter, _ = make_mocked_adapter(mock_device_model)
        result = adapter.velocity()
        assert len(result) == 3

    @patch("wtvb01.wtvb01_adapter.DeviceModel")
    def test_angles_returns_three_axes(self, mock_device_model):
        adapter, _ = make_mocked_adapter(mock_device_model)
        result = adapter.angles()
        assert len(result) == 3

    @patch("wtvb01.wtvb01_adapter.DeviceModel")
    def test_acceleration_returns_three_axes(self, mock_device_model):
        adapter, _ = make_mocked_adapter(mock_device_model)
        result = adapter.acceleration()
        assert len(result) == 3

    @patch("wtvb01.wtvb01_adapter.DeviceModel")
    def test_vibration_frequencies_returns_three_axes(self, mock_device_model):
        adapter, _ = make_mocked_adapter(mock_device_model)
        result = adapter.vibration_frequencies()
        assert len(result) == 3

    @patch("wtvb01.wtvb01_adapter.DeviceModel")
    def test_displacements_returns_three_axes(self, mock_device_model):
        adapter, _ = make_mocked_adapter(mock_device_model)
        result = adapter.displacements()
        assert len(result) == 3