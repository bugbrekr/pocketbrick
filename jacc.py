from framebuf import FrameBuffer, RGB565
import machine
import time
import functions

def TFTColor( aR, aG, aB ) :
  return ((aR & 0xF8) << 8) | ((aG & 0xFC) << 3) | (aB >> 3)

class Program:
    def __init__(self, jacc_os, fb):
        self.jacc_os = jacc_os
        self.fb = fb
        self.fb.fill(0) # clear window display
        self.update() # update display with cleared image
        self.timer = machine.Timer() # main timer for periodic application activities (automatically deinit'd)
    def update(self):
        self.jacc_os._draw_buffer(self.fb)
    def _exit(self):
        self.timer.deinit() # deinit timer
        try:
            self.exit() # attempt graceful exit if supported
        except NotImplementedError:
            pass # graceful exit not implemented
    def exit(self):
        raise NotImplementedError
    def on_keypress(self, key, press_type, p_id):
        raise NotImplementedError

class StatusBar:
    def __init__(self, jacc_os):
        self.jacc_os = jacc_os
        ba = bytearray(128 * 10 * 2)
        self.fb = FrameBuffer(ba, 128, 10, RGB565)
        self.keymap_index = 0
        self.timer = machine.Timer()
        self.timer.init(mode=machine.Timer.PERIODIC, period=10000, callback=self.update)
        self.sensors = functions.Sensors()
        self.update()
    def set_keymap_index(self, index:int):
        self.keymap_index = index
        self.update()
    def update(self, _=None):
        dt = machine.RTC().datetime()
        dt_str = tuple("{:0>2}".format(str(i)) for i in dt)
        batt_percent = self.sensors["battery_percent"]
        if batt_percent >= 100:
            batt_percent = "^^"
        self.fb.fill(0)
        self.fb.text(str(self.keymap_index), 119, 0, 65535) # keymap
        self.fb.text(f"{dt_str[4]}:{dt_str[5]}", 44, 0, 65535) # time
        self.fb.rect(0, 0, 16, 8, 65535)
        self.fb.text(f"{batt_percent}", 0, 0, 65535)
        self.fb.hline(0, 8, 127, 65535)
        self.jacc_os._statusbar_draw_buffer(self.fb)

class JACC_OS:
    """
    [JACC_OS - Just A Cool Calculator OS]
    Basic OS to run and handle programs.
    """
    SLEEP_TIMEOUT_PERIOD = 30000 # 10 seconds
    LONG_PRESS_THRESHOLD_MS = 600
    EXTRA_LONG_PRESS_THRESHOLD_MS = 3000
    def __init__(self, display, keypad):
        self.display = display
        self.keypad = keypad
        self.tft = self.display.tft
        self.keypad.register_callback(self._button_press)
        self.proc_status = 0
        self.sleep_timer = machine.Timer()
        self._start_sleep_timer()
        self.keep_awake = 0
        self.active_keymap = 0
        self.keymap = {
                -1: {
                    "a": ("RESET",), "b": (), "c": (),
                    "d": (), "e": (), "f": (),
                    "g": (), "h": (), "i": ("TORCH",),
                    "j": ("MS",), "k": (), "l": ("SLEEP",), 
                },
                0: {
                    "a": (), "b": (), "c": (),
                    "d": (), "e": (), "f": (),
                    "g": (), "h": (), "i": (),
                    "j": ("MS", "SMJ"), "k": (), "l": (), 
                }
            } # MS = Mode Select, SMS = Super Mode Jump
        self.last_keypress_timestamp = 0
        self._start_sleep_timer()
        self.statusbar = StatusBar(self)
        self.torch_status = 0
        self.torch_fb = FrameBuffer(bytearray(128 * 117 * 2), 128, 117, RGB565)
        self.torch_fb.fill(65535)
    def sleep_trigger(self, _):
        if self.keep_awake == 0:
            self.display.bl(False)
    def _start_sleep_timer(self):
        self.sleep_timer.init(mode=machine.Timer.ONE_SHOT, period=self.SLEEP_TIMEOUT_PERIOD, callback=self.sleep_trigger)
        self.last_keypress_timestamp = time.time()
    def _button_press(self, p_id, dur):
        self._start_sleep_timer()
        if self.display.bl() == False:
            self.display.bl(True)
            return
        if dur < self.LONG_PRESS_THRESHOLD_MS:
            press_type = 0
        elif dur >= self.LONG_PRESS_THRESHOLD_MS and dur < self.EXTRA_LONG_PRESS_THRESHOLD_MS:
            press_type = 1
        elif dur >= self.EXTRA_LONG_PRESS_THRESHOLD_MS:
            press_type = 2
        self.button_callback(p_id, press_type)
    def register_keymap(self, keymap_list):
        _keymap = {}
        for i, keymap in enumerate(keymap_list):
            _keymap_c = {}
            for p_id in "abcdefghijkl":
                if keymap.get(p_id) == None:
                    key = ()
                elif isinstance(keymap.get(p_id), str):
                    if keymap.get(p_id) == "":
                        key = ()
                    else:
                        key = (keymap.get(p_id),)
                elif isinstance(keymap.get(p_id), int):
                    key = (keymap.get(p_id),)
                elif len(keymap.get(p_id)) <= 3:
                    key = keymap.get(p_id)
                elif len(keymap.get(p_id)) > 3:
                    key = (keymap.get(p_id)[0], keymap.get(p_id)[1], keymap.get(p_id)[2])
                _keymap_c[p_id] = key
            _keymap_c["j"] = ("MS", "SMJ")
            _keymap[i] = _keymap_c
        _keymap[-1] = self.keymap[-1]
        self.keymap = _keymap
        self.active_keymap = 0
    def deregister_keymap(self):
        self.register_keymap([{}])
        self.active_keymap = 0
    def rotate_keymap(self):
        keymap_count = len(self.keymap)-1 # ignore super jump keymap
        if self.active_keymap == keymap_count-1:
            self.active_keymap = 0
        elif self.active_keymap < 0:
            self.active_keymap = 0
        else:
            self.active_keymap += 1
        self.statusbar.set_keymap_index(self.active_keymap)
    def system_button_callback(self, key):
        if key == "MS":
            self.rotate_keymap()
        elif key == "SMJ":
            self.active_keymap = -1
            self.statusbar.set_keymap_index("^")
        elif key == "EXIT":
            self._exit()
        elif key == "SLEEP":
            self.display.bl(False)
        elif key == "RESET":
            pass
        elif key == "TORCH":
            if self.torch_status == 1:
                self.torch_status = 0
                self._draw_buffer(self._last_drawn_fb)
            else:
                self.torch_status = 1
                self.tft.image(0, 10, 127, 127, self.torch_fb)
    def button_callback(self, p_id, press_type):
        keymap = self.keymap[self.active_keymap]
        _key = keymap[p_id]
        if len(_key) < press_type+1:
            key = None
        else:
            key = _key[press_type]
        if key == None:
            return
        if self.active_keymap < 0 or p_id == "j":
            self.system_button_callback(key)
            return
        try:
            self.proc.on_keypress(key, press_type, p_id)
        except NotImplementedError:
            pass # program doesnt support keypresses
    def run_program(self, program):
        if self.proc_status == 1:
            self._exit()
        ba = bytearray(128 * 117 * 2)
        fb = FrameBuffer(ba, 128, 117, RGB565)
        self.proc = program(self, fb)
        self.proc_status = 1
        self.proc.run()
    def _draw_buffer(self, fb):
        if self.torch_status == 1:
            self.tft.image(0, 10, 127, 127, self.torch_fb)
        else:
            self._last_drawn_fb = fb
            self.tft.image(0, 10, 127, 127, fb)
    def _statusbar_draw_buffer(self, fb):
        self.tft.image(0, 0, 127, 10, fb)
    def _exit(self):
        self.tft.fill(0)
        self.proc._exit() # send graceful exit signal
        self.deregister_keymap() # unsubscribe keypresses
        self.proc_status = 0
    def wait_for_idle(self):
        while True:
            if self.proc_status == 0:
                return
            time.sleep(0.1)