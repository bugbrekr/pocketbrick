from programs.BaseProgram import BaseProgram
import machine
import json
import functions

def color(r, g, b):
    return ((b//8 & 0xF8) << 8) | ((r//8 & 0xFC) << 3) | (g//4 >> 3)

class Program(BaseProgram):
    options_list = [("WiFi", "WiFi"), ("Time and Date", "TimeAndDate"), ("Storage", "Storage")]
    ELEMENTS_PER_PAGE = 7
    def run(self):
        self.register_keymap([{
                "a": None, "b": "SELECT", "c": ("UP", "TOP"),
                "d": None, "e": None, "f": ("DOWN", "BOTTOM"),
                "g": None, "h": None, "i": None,
                "j": None, "k": None, "l": None,
            }])
        self.selector = 0
        self.show_options_index = 0
        self.draw()
    def draw(self):
        self.fb.fill(0)
        #offset = min(0, self.selector-ELEMENTS_PER_PAGE+1)
        for i, setting in enumerate(self.options_list[self.show_options_index:self.show_options_index+self.ELEMENTS_PER_PAGE]):
            self.fb.text(setting[0], 2, 8+16*i, color(255, 255, 255))
        relative_selected_option = self.selector-self.show_options_index
        self.fb.rect(0, 4+16*relative_selected_option, 127, 16, color(112, 128, 144))
        self.update()
    def on_keypress(self, key, _press_type, _p_id):
        if key in ["UP", "DOWN"]:
            if key == "UP":
                if self.selector == 0:
                    self.selector = 0
                else:
                    self.selector -= 1
            elif key == "DOWN":
                if self.selector+1 == len(self.options_list):
                    self.selector = len(self.options_list)-1
                else:
                    self.selector += 1
            if self.selector < self.show_options_index:
                self.show_options_index -= 1
            elif self.selector >= self.show_options_index+self.ELEMENTS_PER_PAGE:
                self.show_options_index += 1
            self.draw()
        elif key == "TOP":
            self.selector = 0
            self.show_options_index = 0
            self.draw()
        elif key == "BOTTOM":
            self.selector = len(self.options_list)-1
            self.show_options_index = max(0, len(self.options_list)-self.ELEMENTS_PER_PAGE)
            self.draw()
        elif key == "SELECT":
            selection = self.options_list[self.selector][1]
            if selection == "WiFi":
                self.jacc_os.run_program(WiFi)
            elif selection == "TimeAndDate":
                self.jacc_os.run_program(TimeAndDate)
            elif selection == "Storage":
                self.jacc_os.run_program(Storage)

class WiFi(BaseProgram):
    def run(self):
        self.register_keymap([{
                "a": "BACK", "b": "TOGGLE_CONNECTION"
            }])
        with open("config.json") as f:
            config = json.loads(f.read())
        self.wifi_ssid = config["wlan_ssid"]
        self.wifi_password = config["wlan_password"]
        self.jacc_os.wlan.active(True)
        self.draw()
    def draw(self, _=None):
        self.fb.fill(0)
        _status = self.jacc_os.wlan.status()
        wlan_status = ["Disconnected", "Link Join", "Link NOIP", "Connected", "BAD AUTH", "NONET", "FAIL"][_status]
        self.fb.text("[TOGGLE]", 0, 0, color(255, 255, 255))
        self.fb.text(wlan_status, 0, 10, color(169, 169, 169))
        if _status == 3:
            ifconfig = self.jacc_os.wlan.ifconfig()
            self.fb.text(ifconfig[0], 0, 20, color(169, 169, 169))
            self.fb.text(ifconfig[1], 0, 30, color(169, 169, 169))
            self.fb.text(ifconfig[2], 0, 40, color(169, 169, 169))
            self.fb.text(ifconfig[3], 0, 50, color(169, 169, 169))
        self.update()
        if _status > 0 and _status < 3:
            self.timer.init(mode=0, period=500, callback=self.draw)
    def on_keypress(self, key, _press_type, _p_id):
        if key == "BACK":
            self.jacc_os.run_program(Program)
        elif key == "TOGGLE_CONNECTION":
            if self.jacc_os.wlan.status() > 0:
                self.jacc_os.wlan.disconnect()
                self.jacc_os.wlan.deinit()
            else:
                self.jacc_os.wlan.active(True)
                self.jacc_os.wlan.connect(self.wifi_ssid, self.wifi_password)
            self.draw()
            self.timer.init(mode=0, period=500, callback=self.draw)

class TimeAndDate(BaseProgram):
    def run(self):
        self.register_keymap([{
                "a": "BACK", "b": "SYNC_TIME"
            }])
    def on_keypress(self, key, _press_type, _p_id):
        if key == "BACK":
            self.jacc_os.run_program(Program)
        elif key == "SYNC_TIME":
            self.fb.fill(0)
            self.fb.text("Synchronising...", 0, 0, color(255, 255, 255))
            self.update()
            functions.synchronise_time()
            self.fb.fill(0)
            self.fb.text("Synchronised!", 0, 0, color(255, 255, 255))
            self.update()

class Storage(BaseProgram):
    def run(self):
        self.register_keymap([{
                "a": "BACK", "b": "MOUNT_SD"
            }])
        self._draw()
    def _draw(self, text=None):
        self.fb.fill(0)
        is_attached = self.jacc_os.sdcard.is_attached
        is_mounted = self.jacc_os.sdcard.is_mounted
        mount_path = self.jacc_os.sdcard.mount_point
        self.fb.text("[TOGGLE]", 0, 0, color(255, 255, 255))
        self.fb.text("Attached" if is_attached else "Not attached", 0, 10, color(255, 255, 255))
        self.fb.text(f"Mounted: {mount_path}" if is_mounted else "Not Mounted", 0, 20, color(255, 255, 255))
        if text:
            self.fb.text(text, 0, 40, color(255, 255, 255))
        self.update()
    def on_keypress(self, key, _press_type, _p_id):
        if key == "BACK":
            self.jacc_os.run_program(Program)
        elif key == "MOUNT_SD":
            if self.jacc_os.sdcard.is_mounted:
                self.jacc_os.sdcard.unmount()
            else:
                try:
                    self.jacc_os.sdcard.attach()
                except OSError:
                    self._draw("FAILED TO ATTACH")
                    return
                try:
                    self.jacc_os.sdcard.mount()
                except:
                    self._draw("FAILED TO MOUNT")
                    return
            self._draw()
