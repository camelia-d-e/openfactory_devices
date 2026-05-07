import asyncio
import csv
import os
import time
from datetime import datetime

import pyshark

from dust_trak.dust_trak_initializer import DustTrakInitializer


class DustTrakSniffer:
    "Sniffer for DustTrak data packets"
    def __init__(self, network_interface: str, device_ip: str, initializer: DustTrakInitializer, data_export_type: str, current_dir: str = os.path.dirname(os.path.abspath(__file__))):
        self.network_interface = network_interface
        self.device_ip = device_ip
        self.dust_trak_initializer = initializer
        self.data_export_type = data_export_type
        self.current_dir = current_dir
        self.data_updates_timer = 0
        self.no_packet_received_timer = 0

        self.latest_data = {
            "pm1_concentration": 0.0,
            "pm2_5_concentration": 0.0,
            "pm4_concentration": 0.0,
            "pm10_concentration": 0.0,
        }

    def get_latest_data(self) -> dict[str, float]:
        "Return the latest data as a dictionary"
        return self.latest_data

    def run_capture(self, running: bool = True):
        "Continuous capture loop running in background thread"
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            print(f"Starting packet capture on {self.network_interface} from {self.device_ip}...")

            # L'interface Ethernet 4 est créé lorsque la dusttrak est en marche
            capture = pyshark.LiveCapture(
                interface=self.network_interface, display_filter=f"ip.src=={self.device_ip}"
            )

            for packet in capture.sniff_continuously():
                if not running:
                    break

                if hasattr(packet, "tcp") and hasattr(packet.tcp, "payload"):
                    parsed_data: list[str] = self._parse_hex_data(packet.tcp.payload)
                    if not self._is_empty_data(parsed_data) and len(parsed_data) >= 4:
                        converted_data = self._convert_to_percent(parsed_data)

                        if (
                            not self._is_data_updated(converted_data)
                            and self.data_updates_timer == 0
                        ):
                            self.data_updates_timer = time.time()
                            time.sleep(1)
                        elif (
                            not self._is_data_updated(converted_data)
                            and time.time() - self.data_updates_timer > 30
                        ):
                            print(
                                "No new data received for 20 seconds, restarting monitoring..."
                            )
                            self.dust_trak_initializer.launch_dust_trak_monitoring()
                            self.data_updates_timer = 0
                        elif self._is_data_updated(converted_data):
                            self.data_updates_timer = 0

                            self.latest_data = {
                                "pm1_concentration": converted_data[0],
                                "pm2_5_concentration": converted_data[1],
                                "pm4_concentration": converted_data[2],
                                "pm10_concentration": converted_data[3],
                            }

            if self.no_packet_received_timer == 0:
                self.no_packet_received_timer = time.time()
            elif time.time() - self.no_packet_received_timer > 30:
                print("No packets received for 30 seconds, restarting monitoring...")
                self.dust_trak_initializer.launch_dust_trak_monitoring()
                self.no_packet_received_timer = 0
        except (OSError, ValueError, KeyError, RuntimeError) as e:
            print(f"Error in capture loop: {e}")
        finally:
            try:
                loop.close()
            except RuntimeError as e:
                print(f"Error closing event loop: {e}")

    
    def _parse_hex_data(self, raw_data: str) -> list[str]:
        "Decodes and parses raw hex data from TCP messages"
        try:
            bytes_obj = bytes.fromhex(raw_data.replace(":", ""))
            decoded_str = bytes_obj.decode("utf-8")

            parsed_data = decoded_str.split(",")
            data_values = parsed_data[1:-1]
            return data_values
        except (ValueError, UnicodeDecodeError) as e:
            print(f"Error parsing hex data: {e}")
            return [""]

    def _convert_to_percent(self, concentrations: list[str]) -> list[float]:
        "Convert concentration values to percentage"
        percentages = []
        for concentration in concentrations:
            try:
                value = (float(concentration) / 1225000) * 100
                percentages.append(value)
            except (ValueError, ZeroDivisionError) as e:
                print(f"Error converting {concentration}: {e}")
                percentages.append(0.0)
        return percentages

    def _write_to_csv(self, data: dict[str, str]) -> None:
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

    def _is_empty_data(self, parsed_data) -> bool:
        "Check if message contains useful data"
        is_empty = True
        for data_point in parsed_data:
            if float(data_point) != 0.0 and float(data_point) != 91.0:
                is_empty = False
        return is_empty

    def _is_data_updated(self, new_data: list[float]) -> bool:
        "Check if the new data is different from the latest data"
        return not (
            self.latest_data["pm1_concentration"] == new_data[0]
            and self.latest_data["pm2_5_concentration"] == new_data[1]
            and self.latest_data["pm4_concentration"] == new_data[2]
            and self.latest_data["pm10_concentration"] == new_data[3]
        )
    
