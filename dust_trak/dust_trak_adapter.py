import json
import os
import random
import threading

from dust_trak.dust_trak_csv_logger import DustTrakCSVLogger
from dust_trak.dust_trak_initializer import DustTrakInitializer
from dust_trak.dust_trak_sniffer import DustTrakSniffer


class DustTrak:
    "DustTrak device adapter"
    def __init__(self, virtual=False):
        config_data = []
        self.virtual = virtual

        self.network_interface = "Ethernet 4"
        
        self.current_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(self.current_dir, "config.json")
        with open(file_path, encoding="utf-8") as file:
            config_data = json.load(file)

        self.data_export_type = config_data["data_export_type"]
        self.device_ip = config_data["device_ip"]

        self.latest_data = {
            "pm1_concentration": 0.0,
            "pm2_5_concentration": 0.0,
            "pm4_concentration": 0.0,
            "pm10_concentration": 0.0,
        }
        self.capture_thread = None
        self.running = False

        self.initializer = DustTrakInitializer(current_dir=self.current_dir, readings_average_num=config_data["numberOfReadings"])
        self.sniffer = DustTrakSniffer(network_interface=self.network_interface, device_ip=self.device_ip, initializer=self.initializer, data_export_type=self.data_export_type, current_dir=self.current_dir)
        self.csv_logger = DustTrakCSVLogger(csv_file_path=os.path.join(self.current_dir, "logs"), current_dir=self.current_dir)

        if not virtual:
            self.initializer.launch_dust_trak_monitoring()

    def start_capture(self):
        "Start capturing data in a background thread"
        if not self.running:
            self.running = True
            self.capture_thread = threading.Thread(
                target=self.sniffer.run_capture, args=(self.running,), daemon=True
            )
            self.capture_thread.start()
            print("Started data capture thread")

    def stop_capture(self):
        "Stop capturing data"
        self.running = False
        if self.capture_thread and self.capture_thread.is_alive():
            self.capture_thread.join(timeout=2)
            print("Stopped data capture thread")

    def read_data(self) -> dict[str, float]:
        if self.virtual:
            self.latest_data["pm1_concentration"] = random.uniform(0, 0.5)
            self.latest_data["pm2_5_concentration"] = random.uniform(0, 0.5)
            self.latest_data["pm4_concentration"] = random.uniform(0, 0.5)
            self.latest_data["pm10_concentration"] = random.uniform(0, 0.5)
            return self.latest_data.copy()

        latest_data = self.sniffer.get_latest_data().copy()
        if self.data_export_type == "csv":
            self.csv_logger.write_to_csv(latest_data)
        return latest_data
