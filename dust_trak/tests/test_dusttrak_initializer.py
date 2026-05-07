from unittest.mock import patch

import pytest

from dust_trak.dust_trak_initializer import DustTrakInitializer


@pytest.fixture
def initializer():
    return DustTrakInitializer(current_dir="/fake/dir", readings_average_num=5)


class TestInit:
    def test_readings_average_num(self, initializer):
        assert initializer.readings_average_num == 5

    def test_current_dir(self, initializer):
        assert initializer.current_dir == "/fake/dir"

    def test_app_open_flag(self, initializer):
        assert initializer.is_dust_trak_app_open is True


class TestLaunchDustTrakMonitoring:
    def test_completes_without_error(self, initializer):
        with (
            patch("os.path.exists", return_value=False),
            patch("time.sleep"),
            patch("pyautogui.hotkey"),
            patch("pyautogui.screenshot"),
        ):
            initializer.launch_dust_trak_monitoring()

    def test_calls_screenshot(self, initializer):
        with (
            patch("os.path.exists", return_value=False),
            patch("time.sleep"),
            patch("pyautogui.hotkey"),
            patch("pyautogui.screenshot") as mock_screenshot,
        ):
            initializer.launch_dust_trak_monitoring()
            assert mock_screenshot.called