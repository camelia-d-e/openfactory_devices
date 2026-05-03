import threading
import os
import time
import csv
import asyncio
import pyshark
import pyautogui
import json
from datetime import datetime
from typing import Dict, List

class DustTrak():
    "DustTrak device"

    def __init__(self):
        config_data = []
        self.current_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(self.current_dir, 'config.json')
        with open(file_path, 'r', encoding='utf-8') as file:
            config_data = json.load(file)

        self.data_export_type = config_data['data_export_type']
        self.device_ip = config_data['device_ip']
        
        self.latest_data = {
            'pm1_concentration': 0.0,
            'pm2_5_concentration': 0.0,
            'pm4_concentration': 0.0,
            'pm10_concentration': 0.0
        }
        self.capture_thread = None
        self.running = False
        self.data_updates_timer = 0
        self.no_packet_received_timer = 0
        self.readings_average_num = config_data['numberOfReadings']
        self.is_dust_trak_app_open = True
        self.launch_dust_trak_monitoring()
    
    def launch_dust_trak_monitoring(self):
        "Launch DustTrak monitoring"
        try:
            pyautogui.hotkey('win', 'd')
            time.sleep(2)
        except (pyautogui.FailSafeException, OSError) as e:
            print(f"Could not show desktop: {e}")

        current_screenshot_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates', 'current_desktop.png')
        pyautogui.screenshot(current_screenshot_path)

        self.open_dust_trak_app()

        pyautogui.screenshot(current_screenshot_path)

        is_on_data_tab = self.check_if_on_data_tab()

        if is_on_data_tab:
            self.go_to_connect_tab()
            time.sleep(2)

            pyautogui.screenshot(current_screenshot_path)

            self.disconnect_from_instrument()

        self.connect_to_instrument()
        time.sleep(2)

        pyautogui.screenshot(current_screenshot_path)

        self.go_to_data_tab()

        pyautogui.screenshot(current_screenshot_path)

        self.set_readings_nb()

        self.start_monitoring()

        self.APP_LAUNCHED = True
    
    def open_dust_trak_app(self):
        "Open the dust trak app"
         ## Open from task bar if app was already opened
        task_bar_path = os.path.join(self.current_dir, 'templates', 'dust_trak_task_bar.png')
        if not os.path.exists(task_bar_path):
            print(f"Template image not found at {task_bar_path}")
            return
        try:
            if self.is_dust_trak_app_open:
                task_bar_location = pyautogui.locateOnScreen(task_bar_path, confidence=0.7)
                if task_bar_location:
                    pyautogui.click(task_bar_location, button='left', clicks=1)
                    return
        except  pyautogui.ImageNotFoundException:
            print(f"Could not find the image at {task_bar_path}")
            self.is_dust_trak_app_open = False

        shortcut_path = os.path.join(self.current_dir, 'templates', 'dust_trak_shortcut.png')
        if not os.path.exists(shortcut_path):
            print(f"Template image not found at {shortcut_path}")
            return
        
        #Else use shortcut on desk
        try:
            if not self.is_dust_trak_app_open:
                shortcut_location = pyautogui.locateOnScreen(shortcut_path, confidence=0.9)
                if shortcut_location:
                    pyautogui.click(shortcut_location, button='left', clicks=2)
                    self.is_dust_trak_app_open = True
                    time.sleep(5)
        except pyautogui.ImageNotFoundException:
            print(f"Could not find the image at {shortcut_path}")

    def check_if_on_data_tab(self):
        "Check if already on data tab"
        is_on_data_tab = False
        play_btn_path = os.path.join(self.current_dir, 'templates', 'play_btn.png')
        if not os.path.exists(play_btn_path):
            print(f"Template image not found at {play_btn_path}")
            return
        try:
            play_btn_location = pyautogui.locateOnScreen(play_btn_path, confidence=0.7)
            is_on_data_tab = play_btn_location is not None
        except pyautogui.ImageNotFoundException:
            print(f"Could not find the image at {play_btn_path}")
        
        stop_btn_path = os.path.join(self.current_dir, 'templates', 'stop_btn.png')
        if not os.path.exists(stop_btn_path):
            print(f"Template image not found at {stop_btn_path}")
            return
        
        try:
            stop_btn_location = pyautogui.locateOnScreen(stop_btn_path, confidence=0.7)
            is_on_data_tab = stop_btn_location is not None
        except pyautogui.ImageNotFoundException:
            print(f"Could not find the image at {stop_btn_path}")

        return is_on_data_tab

    def go_to_data_tab(self):
        "Go to data tab on DustTrak app"
        data_tab_path = os.path.join(self.current_dir, 'templates', 'data_tab.png')
        if not os.path.exists(data_tab_path):
            print(f"Template image not found at {data_tab_path}")
            return

        try:
            data_tab_location = pyautogui.locateOnScreen(data_tab_path, confidence=0.7)
            if data_tab_location:
                pyautogui.click(data_tab_location, button='left', clicks=1)
        except pyautogui.ImageNotFoundException:
            print(f"Could not find the image at {data_tab_path}")

    def go_to_connect_tab(self):
        "Go to data tab on DustTrak app"
        connect_tab_path = os.path.join(self.current_dir, 'templates', 'connect_tab.png')
        if not os.path.exists(connect_tab_path):
            print(f"Template image not found at {connect_tab_path}")
            return

        try:
            connect_tab_location = pyautogui.locateOnScreen(connect_tab_path, confidence=0.7)
            if connect_tab_location:
                pyautogui.click(connect_tab_location, button='left', clicks=1)
        except pyautogui.ImageNotFoundException:
            print(f"Could not find the image at {connect_tab_path}")

    def connect_to_instrument(self):
        "Connect to instrument on DustTrak app"
        is_connected = False
        first_attempt = False
        connect_btn_path = os.path.join(self.current_dir, 'templates', 'connect_btn.png')
        if not os.path.exists(connect_btn_path):
            print(f"Template image not found at {connect_btn_path}")
            return
        
        connect_to_instrument_btn_path = os.path.join(self.current_dir, 'templates', 'connect_to_instrument_btn.png')
        if not os.path.exists(connect_btn_path):
            print(f"Template image not found at {connect_btn_path}")
            return

        disconnect_btn_path = os.path.join(self.current_dir, 'templates', 'disconnect_btn.png')
        if not os.path.exists(disconnect_btn_path):
            print(f"Template image not found at {disconnect_btn_path}")
            return
        
        try:
            connect_btn_location = pyautogui.locateOnScreen(connect_btn_path, confidence=0.7)
            if connect_btn_location:
                pyautogui.click(connect_btn_location, button='left', clicks=1)
                is_connected = True
                first_attempt = True
        except pyautogui.ImageNotFoundException:
            print(f"Could not find image at {connect_btn_path}")


        try:
            connect_to_instrument_btn_location = pyautogui.locateOnScreen(connect_to_instrument_btn_path, confidence=0.7)
            if connect_to_instrument_btn_location and not is_connected:
                pyautogui.click(connect_to_instrument_btn_location, button='left', clicks=1)
        except pyautogui.ImageNotFoundException:
            print(f"Could not find image at {connect_to_instrument_btn_path}")

        try:
            while True:
                disconnect_btn_location = pyautogui.locateOnScreen(disconnect_btn_path, confidence=0.7)
                if disconnect_btn_location:
                    break
                if first_attempt:
                    pyautogui.click(pyautogui.locateOnScreen(connect_btn_path, confidence=0.7), button='left', clicks=1)
                else:
                    pyautogui.click(pyautogui.locateOnScreen(connect_to_instrument_btn_path, confidence=0.7), button='left', clicks=1)
                time.sleep(2)
        except pyautogui.ImageNotFoundException:
            print(f"Could not find image at {disconnect_btn_path}, {connect_btn_path} or {connect_to_instrument_btn_path}")
    
    def disconnect_from_instrument(self):
        "Disconnect from instrument on DustTrak app"
        disconnect_btn_path = os.path.join(self.current_dir, 'templates', 'disconnect_btn.png')
        if not os.path.exists(disconnect_btn_path):
            print(f"Template image not found at {disconnect_btn_path}")
            return
        try:
            disconnect_btn_location = pyautogui.locateOnScreen(disconnect_btn_path, confidence=0.7)
            pyautogui.click(disconnect_btn_location, button='left', clicks=1)
        except pyautogui.ImageNotFoundException:
            print(f"Could not find the image at {disconnect_btn_path}")

    def set_readings_nb(self):
        "Set number of readings in Dust Trak app"
        readings_nb_input_path = os.path.join(self.current_dir, 'templates', 'readings_nb_input.png')
        if not os.path.exists(readings_nb_input_path):
            print(f"Template image not found at {readings_nb_input_path}")
            return

        try:
            readings_nb_input_location = pyautogui.locateOnScreen(readings_nb_input_path, confidence=0.7)
            if readings_nb_input_location:
                pyautogui.click(pyautogui.center(readings_nb_input_location), button='left', clicks=1)
                pyautogui.press(['backspace', 'backspace', 'backspace'])
                pyautogui.write(str(self.readings_average_num))
        except pyautogui.ImageNotFoundException:
            print(f"Could not find the image at {readings_nb_input_path}")

        set_btn_path = os.path.join(self.current_dir, 'templates', 'set_btn.png')
        if not os.path.exists(set_btn_path):
            print(f"Template image not found at {set_btn_path}")
            return
        
        try:
            set_btn_location = pyautogui.locateOnScreen(set_btn_path, confidence=0.7)
            if set_btn_location:
                pyautogui.click(set_btn_location, button='left', clicks=1)
                time.sleep(2)
        except pyautogui.ImageNotFoundException:
            print(f"Could not find the image at {set_btn_path}")

    def start_monitoring(self):
        "Start monitoring instrument on DustTrak app"
        play_btn_path = os.path.join(self.current_dir, 'templates', 'play_btn.png')
        if not os.path.exists(play_btn_path):
            print(f"Template image not found at {play_btn_path}")
            return

        try:
            play_btn_location = pyautogui.locateOnScreen(play_btn_path, confidence=0.7)
            if play_btn_location:
                pyautogui.click(play_btn_location, button='left', clicks=1)
        except pyautogui.ImageNotFoundException:
            print(f"Could not find the image at {play_btn_path}")

    def start_capture(self):
        "Start capturing data in a background thread"
        if not self.running:
            self.running = True
            self.capture_thread = threading.Thread(target=self._capture_loop, daemon=True)
            self.capture_thread.start()
            print("Started data capture thread")

    def stop_capture(self):
        "Stop capturing data"
        self.running = False
        if self.capture_thread and self.capture_thread.is_alive():
            self.capture_thread.join(timeout=2)
            print("Stopped data capture thread")

    def _capture_loop(self):
        "Continuous capture loop running in background thread"
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            print(f"Starting packet capture on Ethernet 4 from {self.device_ip}...")

            capture = pyshark.LiveCapture(
                interface='Ethernet 4',
                display_filter=f'ip.src=={self.device_ip}'
            )

            for packet in capture.sniff_continuously():
                if not self.running:
                    break

                if hasattr(packet, 'tcp') and hasattr(packet.tcp, 'payload'):
                    parsed_data: List[str] = self.parse_hex_data(packet.tcp.payload)
                    if not self.is_empty_data(parsed_data) and len(parsed_data) >= 4:
                        if self.data_export_type == "csv":
                            self.write_to_csv({
                                'pm1_concentration': parsed_data[0],
                                'pm2_5_concentration': parsed_data[1],
                                'pm4_concentration': parsed_data[2],
                                'pm10_concentration': parsed_data[3],
                            })
                        elif self.data_export_type == "openfactory":
                            converted_data = self.convert_to_percent(parsed_data)

                            if not self.is_data_updated(converted_data) and self.data_updates_timer == 0:
                                self.data_updates_timer = time.time()
                                time.sleep(1)
                            elif not self.is_data_updated(converted_data) and time.time() - self.data_updates_timer > 30:
                                print("No new data received for 20 seconds, restarting monitoring...")
                                self.launch_dust_trak_monitoring()
                                self.data_updates_timer = 0
                            elif self.is_data_updated(converted_data):
                                self.data_updates_timer = 0

                                self.latest_data = {
                                    'pm1_concentration': converted_data[0],
                                    'pm2_5_concentration': converted_data[1],
                                    'pm4_concentration': converted_data[2],
                                    'pm10_concentration': converted_data[3]
                                }

            if self.no_packet_received_timer == 0:
                self.no_packet_received_timer = time.time()
            elif time.time() - self.no_packet_received_timer > 30:
                print("No packets received for 30 seconds, restarting monitoring...")
                self.launch_dust_trak_monitoring()
                self.no_packet_received_timer = 0
        except (OSError, ValueError, KeyError, RuntimeError) as e:
            print(f"Error in capture loop: {e}")
        finally:
            try:
                loop.close()
            except RuntimeError as e:
                print(f"Error closing event loop: {e}")
                
    def is_data_updated(self, new_data: List[float]) -> bool:
        "Check if the new data is different from the latest data"   
        return not (self.latest_data['pm1_concentration'] == new_data[0] and
                self.latest_data['pm2_5_concentration'] == new_data[1] and
                self.latest_data['pm4_concentration'] == new_data[2] and
                self.latest_data['pm10_concentration'] == new_data[3])

    def read_data(self) -> Dict[str, float]:
        "Return the latest captured data"
        return self.latest_data.copy()

    def parse_hex_data(self, raw_data: str) -> List[str]:
        "Decodes and parses raw hex data from TCP messages"
        try:
            bytes_obj = bytes.fromhex(raw_data.replace(":", ""))
            decoded_str = bytes_obj.decode('utf-8')

            parsed_data = decoded_str.split(',')
            data_values = parsed_data[1:-1]
            return data_values
        except (ValueError, UnicodeDecodeError) as e:
            print(f"Error parsing hex data: {e}")
            return ['']

    def convert_to_percent(self, concentrations: List[str]) -> List[float]:
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
    
    def write_to_csv(self, data: Dict[str, str]) -> None:
        "Write data to CSV file"
        csv_data = data.copy()

        file_path = os.path.join(self.current_dir, 'logs', f'{datetime.today().strftime('%Y-%m-%d')}.csv')

        csv_data['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        with open(file=file_path, mode='a', newline='', encoding='utf-8') as csvfile:
            fieldnames = []
            for key in csv_data.keys():
                fieldnames.append(key)

            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            csvfile.seek(0, 2)
            if csvfile.tell() == 0:
                writer.writeheader()

            writer.writerow(csv_data)
    
    def is_empty_data(self, parsed_data) -> bool:
        "Check if message contains useful data"
        is_empty = True
        for data_point in parsed_data:
            if (float(data_point) != 0.0 and float(data_point) != 91.0):
                is_empty = False
        return is_empty
