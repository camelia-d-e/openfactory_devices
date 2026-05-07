import csv
import os
from datetime import datetime
from typing import Any


class DustTrakCSVLogger:
    def __init__(self, csv_file_path: str, current_dir: str):
        self.csv_file_path = csv_file_path
        self.current_dir = current_dir

    def write_to_csv(self, data: dict[str, Any]) -> None:
        "Write data to CSV file"
        csv_data = data.copy()

        file_path = os.path.join(
            self.current_dir, "logs", f"{datetime.today().strftime('%Y-%m-%d')}.csv"
        )

        csv_data["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with open(file=file_path, mode="a", newline="", encoding="utf-8") as csvfile:
            fieldnames = []
            for key in csv_data:
                fieldnames.append(key)

            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            csvfile.seek(0, 2)
            if csvfile.tell() == 0:
                writer.writeheader()

            writer.writerow(csv_data)