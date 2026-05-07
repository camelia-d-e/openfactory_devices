import os
import time

import pyautogui


class DustTrakInitializer:
    "Handles GUI interactions to launch and set up DustTrak monitoring"
    def __init__(self, current_dir: str, readings_average_num: int):
        self.current_dir = current_dir
        self.config_data = []
        self.current_dir = current_dir
        self.readings_average_num = readings_average_num
        self.is_dust_trak_app_open = True

    def launch_dust_trak_monitoring(self):
        "Launch DustTrak monitoring"
        try:
            pyautogui.hotkey("win", "d")
            time.sleep(2)
        except (pyautogui.FailSafeException, OSError) as e:
            print(f"Could not show desktop: {e}")

        current_screenshot_path = os.path.join(
            self.current_dir,
            "templates",
            "current_desktop.png",
        )
        pyautogui.screenshot(current_screenshot_path)

        self._open_dust_trak_app()

        pyautogui.screenshot(current_screenshot_path)

        is_on_data_tab = self._check_if_on_data_tab()

        if is_on_data_tab:
            self._go_to_connect_tab()
            time.sleep(2)

            pyautogui.screenshot(current_screenshot_path)

            self._disconnect_from_instrument()

        self._connect_to_instrument()
        time.sleep(2)

        pyautogui.screenshot(current_screenshot_path)

        self._go_to_data_tab()

        pyautogui.screenshot(current_screenshot_path)

        self._set_readings_nb()

        self._start_monitoring()

    def _open_dust_trak_app(self):
        "Open the dust trak app"
        ## Open from task bar if app was already opened
        task_bar_path = os.path.join(
            self.current_dir, "templates", "dust_trak_task_bar.png"
        )
        if not os.path.exists(task_bar_path):
            print(f"Template image not found at {task_bar_path}")
            return
        try:
            if self.is_dust_trak_app_open:
                task_bar_location = pyautogui.locateOnScreen(
                    task_bar_path, confidence=0.7
                )
                if task_bar_location:
                    pyautogui.click(task_bar_location, button="left", clicks=1)
                    return
        except pyautogui.ImageNotFoundException:
            print(f"Could not find the image on screen at {task_bar_path}")
            self.is_dust_trak_app_open = False

        shortcut_path = os.path.join(
            self.current_dir, "templates", "dust_trak_shortcut.png"
        )
        if not os.path.exists(shortcut_path):
            print(f"Template image not found at {shortcut_path}")
            return

        # Else use shortcut on desk
        try:
            if not self.is_dust_trak_app_open:
                shortcut_location = pyautogui.locateOnScreen(
                    shortcut_path, confidence=0.9
                )
                if shortcut_location:
                    pyautogui.click(shortcut_location, button="left", clicks=2)
                    self.is_dust_trak_app_open = True
                    time.sleep(5)
        except pyautogui.ImageNotFoundException:
            print(f"Could not find the image at {shortcut_path}")

    def _check_if_on_data_tab(self):
        "Check if already on data tab"
        is_on_data_tab = False
        play_btn_path = os.path.join(self.current_dir, "templates", "play_btn.png")
        if not os.path.exists(play_btn_path):
            print(f"Template image not found at {play_btn_path}")
            return
        try:
            play_btn_location = pyautogui.locateOnScreen(play_btn_path, confidence=0.7)
            is_on_data_tab = play_btn_location is not None
        except pyautogui.ImageNotFoundException:
            print(f"Could not find the image at {play_btn_path}")

        stop_btn_path = os.path.join(self.current_dir, "templates", "stop_btn.png")
        if not os.path.exists(stop_btn_path):
            print(f"Template image not found at {stop_btn_path}")
            return

        try:
            stop_btn_location = pyautogui.locateOnScreen(stop_btn_path, confidence=0.7)
            is_on_data_tab = stop_btn_location is not None
        except pyautogui.ImageNotFoundException:
            print(f"Could not find the image at {stop_btn_path}")

        return is_on_data_tab

    def _go_to_data_tab(self):
        "Go to data tab on DustTrak app"
        data_tab_path = os.path.join(self.current_dir, "templates", "data_tab.png")
        if not os.path.exists(data_tab_path):
            print(f"Template image not found at {data_tab_path}")
            return

        try:
            data_tab_location = pyautogui.locateOnScreen(data_tab_path, confidence=0.7)
            if data_tab_location:
                pyautogui.click(data_tab_location, button="left", clicks=1)
        except pyautogui.ImageNotFoundException:
            print(f"Could not find the image at {data_tab_path}")

    def _go_to_connect_tab(self):
        "Go to data tab on DustTrak app"
        connect_tab_path = os.path.join(
            self.current_dir, "templates", "connect_tab.png"
        )
        if not os.path.exists(connect_tab_path):
            print(f"Template image not found at {connect_tab_path}")
            return

        try:
            connect_tab_location = pyautogui.locateOnScreen(
                connect_tab_path, confidence=0.7
            )
            if connect_tab_location:
                pyautogui.click(connect_tab_location, button="left", clicks=1)
        except pyautogui.ImageNotFoundException:
            print(f"Could not find the image at {connect_tab_path}")

    def _connect_to_instrument(self):
        "Connect to instrument on DustTrak app"
        is_connected = False
        first_attempt = False
        connect_btn_path = os.path.join(
            self.current_dir, "templates", "connect_btn.png"
        )
        if not os.path.exists(connect_btn_path):
            print(f"Template image not found at {connect_btn_path}")
            return

        connect_to_instrument_btn_path = os.path.join(
            self.current_dir, "templates", "connect_to_instrument_btn.png"
        )
        if not os.path.exists(connect_btn_path):
            print(f"Template image not found at {connect_btn_path}")
            return

        disconnect_btn_path = os.path.join(
            self.current_dir, "templates", "disconnect_btn.png"
        )
        if not os.path.exists(disconnect_btn_path):
            print(f"Template image not found at {disconnect_btn_path}")
            return

        try:
            connect_btn_location = pyautogui.locateOnScreen(
                connect_btn_path, confidence=0.7
            )
            if connect_btn_location:
                pyautogui.click(connect_btn_location, button="left", clicks=1)
                is_connected = True
                first_attempt = True
        except pyautogui.ImageNotFoundException:
            print(f"Could not find image at {connect_btn_path}")

        try:
            connect_to_instrument_btn_location = pyautogui.locateOnScreen(
                connect_to_instrument_btn_path, confidence=0.7
            )
            if connect_to_instrument_btn_location and not is_connected:
                pyautogui.click(
                    connect_to_instrument_btn_location, button="left", clicks=1
                )
        except pyautogui.ImageNotFoundException:
            print(f"Could not find image at {connect_to_instrument_btn_path}")

        try:
            while True:
                disconnect_btn_location = pyautogui.locateOnScreen(
                    disconnect_btn_path, confidence=0.7
                )
                if disconnect_btn_location:
                    break
                if first_attempt:
                    pyautogui.click(
                        pyautogui.locateOnScreen(connect_btn_path, confidence=0.7),
                        button="left",
                        clicks=1,
                    )
                else:
                    pyautogui.click(
                        pyautogui.locateOnScreen(
                            connect_to_instrument_btn_path, confidence=0.7
                        ),
                        button="left",
                        clicks=1,
                    )
                time.sleep(2)
        except pyautogui.ImageNotFoundException:
            print(
                f"Could not find image at {disconnect_btn_path}, {connect_btn_path} or {connect_to_instrument_btn_path}"
            )

    def _disconnect_from_instrument(self):
        "Disconnect from instrument on DustTrak app"
        disconnect_btn_path = os.path.join(
            self.current_dir, "templates", "disconnect_btn.png"
        )
        if not os.path.exists(disconnect_btn_path):
            print(f"Template image not found at {disconnect_btn_path}")
            return
        try:
            disconnect_btn_location = pyautogui.locateOnScreen(
                disconnect_btn_path, confidence=0.7
            )
            pyautogui.click(disconnect_btn_location, button="left", clicks=1)
        except pyautogui.ImageNotFoundException:
            print(f"Could not find the image at {disconnect_btn_path}")

    def _set_readings_nb(self):
        "Set number of readings in Dust Trak app"
        readings_nb_input_path = os.path.join(
            self.current_dir, "templates", "readings_nb_input.png"
        )
        if not os.path.exists(readings_nb_input_path):
            print(f"Template image not found at {readings_nb_input_path}")
            return

        try:
            readings_nb_input_location = pyautogui.locateOnScreen(
                readings_nb_input_path, confidence=0.7
            )
            if readings_nb_input_location:
                pyautogui.click(
                    pyautogui.center(readings_nb_input_location),
                    button="left",
                    clicks=1,
                )
                pyautogui.press(["backspace", "backspace", "backspace"])
                pyautogui.write(str(self.readings_average_num))
        except pyautogui.ImageNotFoundException:
            print(f"Could not find the image at {readings_nb_input_path}")

        set_btn_path = os.path.join(self.current_dir, "templates", "set_btn.png")
        if not os.path.exists(set_btn_path):
            print(f"Template image not found at {set_btn_path}")
            return

        try:
            set_btn_location = pyautogui.locateOnScreen(set_btn_path, confidence=0.7)
            if set_btn_location:
                pyautogui.click(set_btn_location, button="left", clicks=1)
                time.sleep(2)
        except pyautogui.ImageNotFoundException:
            print(f"Could not find the image at {set_btn_path}")

    def _start_monitoring(self):
        "Start monitoring instrument on DustTrak app"
        play_btn_path = os.path.join(self.current_dir, "templates", "play_btn.png")
        if not os.path.exists(play_btn_path):
            print(f"Template image not found at {play_btn_path}")
            return

        try:
            play_btn_location = pyautogui.locateOnScreen(play_btn_path, confidence=0.7)
            if play_btn_location:
                pyautogui.click(play_btn_location, button="left", clicks=1)
        except pyautogui.ImageNotFoundException:
            print(f"Could not find the image at {play_btn_path}")