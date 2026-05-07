from unittest.mock import MagicMock, mock_open, patch

import pytest

from dust_trak.dust_trak_csv_logger import DustTrakCSVLogger


@pytest.fixture
def logger():
    return DustTrakCSVLogger(csv_file_path="/fake/dir/logs", current_dir="/fake/dir")


DATA = {
    "pm1_concentration": 1.0,
    "pm2_5_concentration": 2.0,
    "pm4_concentration": 3.0,
    "pm10_concentration": 4.0,
}


class TestWriteToCsv:
    def test_writes_row(self, logger):
        m = mock_open()
        with (
            patch("builtins.open", m),
            patch("dust_trak.dust_trak_csv_logger.datetime") as mock_dt,
        ):
            mock_dt.today.return_value.strftime.return_value = "2026-05-07"
            mock_dt.now.return_value.strftime.return_value = "2026-05-07 01:00:00"
            logger.write_to_csv(DATA)
        m.assert_called_once()

    def test_does_not_mutate_input(self, logger):
        original = DATA.copy()
        m = mock_open()
        with (
            patch("builtins.open", m),
            patch("dust_trak.dust_trak_csv_logger.datetime") as mock_dt,
        ):
            mock_dt.today.return_value.strftime.return_value = "2026-05-07"
            mock_dt.now.return_value.strftime.return_value = "2026-05-07 01:00:00"
            logger.write_to_csv(DATA)
        assert original == DATA

    def test_timestamp_added_to_row(self, logger):
        written_data = {}

        def capture_writerow(row):
            written_data.update(row)

        mock_writer = MagicMock()
        mock_writer.writerow.side_effect = capture_writerow

        m = mock_open()
        with (
            patch("builtins.open", m),
            patch("dust_trak.dust_trak_csv_logger.csv.DictWriter", return_value=mock_writer),
            patch("dust_trak.dust_trak_csv_logger.datetime") as mock_dt,
        ):
            mock_dt.today.return_value.strftime.return_value = "2026-05-07"
            mock_dt.now.return_value.strftime.return_value = "2026-05-07 01:00:00"
            logger.write_to_csv(DATA)

        assert "timestamp" in written_data
        assert written_data["timestamp"] == "2026-05-07 01:00:00"