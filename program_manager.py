import time
from framebuf import FrameBuffer, RGB565, MONO_HLSB
import functions
from functions import color
import machine
import jacc
import gc
from writer import Writer, CWriter
import gui
from programs.BaseProgram import BaseProgram

class TestApp(BaseProgram):
    def mainloop(self, _):
        self.fb.fill(0)
        self.fb.rect(0, 10+self.counter, 10, 20, 255, True)
        self.update()
        if 10+self.counter+20>=117:
            self.jacc_os._exit()
        self.counter += 2
    def run(self):
        self.counter = 0
        #self.fb.rect(10, 10, 10, 20, 255, True)
        #self.update()
        self.timer.init(mode=machine.Timer.PERIODIC, freq=10, callback=self.mainloop)

class TestApp2(BaseProgram):
    def mainloop(self, _):
        self.fb.fill(0)
        dt = machine.RTC().datetime()
        dt_str = tuple("{:0>2}".format(str(i)) for i in dt)
        batt_volt = self.sensors["battery_voltage"]
        batt_percent = self.sensors["battery_percent"]
        mem_percent = round(gc.mem_alloc()/(gc.mem_alloc()+gc.mem_free())*100)
        ttl = self.jacc_os.last_keypress_timestamp+int(self.jacc_os.SLEEP_TIMEOUT_PERIOD/1000)-time.time()
        self.text[0] = f"bv: {batt_volt}V"
        self.text[1] = f"bp: {batt_percent}%"
        self.text[2] = f"mem: {mem_percent}%"
        self.text[5] = f"Date: {dt_str[2]}/{dt_str[1]}/{dt_str[0]}"
        self.text[6] = f"Time: {dt_str[4]}:{dt_str[5]}:{dt_str[6]}"
        self.text[8] = f"TTL: {ttl}s"
        for i, text in enumerate(self.text):
            self.fb.text(text, 0, i*8, 65535)
        self.update()
        self.text[3] = ""
    def run(self):
        self.text = ["", "", "", "", "", "", "", "", ""]
        self.jacc_os.register_keymap([{"a": "TEST1"}, {"a": "TEST2"}, {"a": "TEST3"}])
        self.sensors = functions.Sensors()
        self.timer.init(mode=machine.Timer.PERIODIC, period=500, callback=self.mainloop)
    def on_keypress(self, key, _press_type, _p_id):
        self.text[3] = key
        if key == "TEST2":
            gc.collect()

class SimpleCalculatorV2(BaseProgram):
    def run(self):
        keymap = [
            {
                "a": "1", "b": "2", "c": ("3", "BK"),
                "d": "4", "e": "5", "f": ("6", "+"),
                "g": "7", "h": "8", "i": ("9", "-"),
                "j": None, "k": "0", "l": (".", "="),
            },
            {
                "a": "^", "b": "*", "c": ("BK", "CA"),
                "d": "ROOT", "e": "/", "f": "+",
                "g": "CA", "h": (), "i": "-",
                "j": None, "k": (), "l": "=",
            }
        ]
        self.jacc_os.register_keymap(keymap)
    def on_keypress(self, key, _press_type, _p_id):
        pass

class TestProgram3(BaseProgram):
    def run(self):
        import fonts.courier20
        #wri = Writer(self.fb, fonts.cnr15, 128, 117, False)
        #wri.printstring('Hello, World!')
        textbox = gui.Textbox(fonts.courier20, 128)
        textbox.set_text("Hello, World!")
        self.fb.blit(textbox.fb, 0, 10)
        fbc = FrameBuffer(bytearray(b"\xFFFF"), 1, 1, RGB565)
        self.fb.blit(fbc, 0, 0)
        self.update()

def load_program(program_name):
    return getattr(getattr(__import__(f"programs.{program_name}"), program_name), "Program")