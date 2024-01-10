import time
from framebuf import FrameBuffer, RGB565, MONO_HLSB
import functions
import machine
import jacc
import gc
from writer import Writer, CWriter
import gui

class Clock:
    def __init__(self):
        ba = bytearray(w * h * 2)
        self.fb = FrameBuffer(ba, w, h, RGB565) 

class TestApp(jacc.Program):
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

class TestApp2(jacc.Program):
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
    
class SimpleCalculator(jacc.Program):
    def run(self):
        keymap = [
            {
                "a": "1", "b": "2", "c": "3",
                "d": "4", "e": "5", "f": "6",
                "g": "7", "h": "8", "i": "9",
                "j": None, "k": "0", "l": ".",
            },
            {
                "a": "POWER", "b": "*", "c": ("BK", "CA"),
                "d": "ROOT", "e": "/", "f": "+",
                "g": "CLR", "h": "UP", "i": "-",
                "j": None, "k": "DOWN", "l": "=",
            }
        ]
        self.jacc_os.register_keymap(keymap)
        self.selector = -1
        self.number_1 = ""
        self.operation = ""
        self.number_2 = ""
        self.solution = ""
    def _evaluate(self, number_1, operation, number_2):
        if operation == "+":
            return number_1+number_2
        elif operation == "-":
            return number_1-number_2
        elif operation == "*":
            return number_1*number_2
        elif operation == "/":
            return number_1/number_2
        elif operation == "POWER":
            return number_1**number_2
        elif operation == "ROOT":
            return number_1**(1/number_2)
    def on_keypress(self, key, _press_type, _p_id):
        if key in "0123456789.":
            self.solution = ""
            if self.selector == -1 or self.selector == 0:
                if len(self.number_1) <= 14:
                    if key == ".":
                        if "." not in self.number_1:
                            self.number_1 += key
                    else:
                        self.number_1 += key
            elif self.selector == 1:
                if len(self.number_2) <= 14:
                    if key == ".":
                        if "." not in self.number_2:
                            self.number_2 += key
                    else:
                        self.number_2 += key
            elif self.operation == "":
                if len(self.number_1) <= 14:
                    if key == ".":
                        if "." not in self.number_1:
                            self.number_1 += key
                    else:
                        self.number_1 += key
            else:
                if len(self.number_2) <= 14:
                    if key == ".":
                        if "." not in self.number_2:
                            self.number_2 += key
                    else:
                        self.number_2 += key
        elif key in ["+", "-", "*", "/", "POWER", "ROOT"]:
            self.solution = ""
            if self.operation != "" and self.number_1 != "" and self.number_2 != "":
                sol = self._evaluate(float(self.number_1), self.operation, float(self.number_2))
                if int(sol) == sol:
                    sol = int(sol)
                self.solution = str(sol)
                self.number_1 = self.solution
                self.number_2 = ""
            self.operation = key
            if self.selector == -1:
                self.selector = 1
        elif key == "UP":
            self.selector = 0
        elif key == "DOWN":
            self.selector = 1
        elif key == "BK":
            self.solution = ""
            if self.selector == -1 or self.selector == 0:
                self.number_1 = self.number_1[:-1]
            elif self.selector == 1:
                if self.number_2 == "":
                    if self.operation == "":
                        self.selector = 0
                        self.number_1 = self.number_1[:-1]
                    else:
                        self.operation = ""
                else:
                    self.number_2 = self.number_2[:-1]
            elif self.operation == "":
                self.number_1 = self.number_1[:-1]
            else:
                if self.number_2 == "":
                    if self.operation == "":
                        self.selector = 0
                        self.number_1 = ""
                    else:
                        self.operation = ""
                else:
                    self.number_2 = self.number_2[:-1]
        elif key == "CA":
            self.solution = ""
            if self.selector == -1 or self.selector == 0:
                self.number_1 = ""
            elif self.selector == 1:
                if self.number_2 == "":
                    self.operation = ""
                else:
                    self.number_2 = ""
            elif self.operation == "":
                self.number_1 = ""
            else:
                if self.number_2 == "":
                    self.operation = ""
                else:
                    self.number_2 = ""
        elif key == "=":
            if self.number_1 != "" and self.number_2 != "" and self.operation != "":
                sol = self._evaluate(float(self.number_1), self.operation, float(self.number_2))
                if int(sol) == sol:
                    sol = int(sol)
                self.solution = str(sol)
                self.number_1 = self.solution
                self.number_2 = ""
        elif key == "CLR":
            self.number_1 = ""
            self.operation = ""
            self.number_2 = ""
            self.solution = ""
            self.selector = -1
        self.fb.fill(0)
        self.fb.text("{: >16}".format(self.number_1), 0, 8, 65535)
        self.fb.text("{: >16}".format(self.operation), 0, 16, 65535)
        self.fb.text("{: >16}".format(self.number_2), 0, 24, 65535)
        self.fb.text("="+"{: >15}".format(self.solution), 0, 40, 65535)
        self.update()

class SimpleCalculatorV2(jacc.Program):
    def run(self):
        keymap = [
            {
                "a": "1", "b": "2", "c": "3",
                "d": "4", "e": "5", "f": "6",
                "g": "7", "h": "8", "i": "9",
                "j": None, "k": "0", "l": ".",
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

class TestProgram3(jacc.Program):
    def run(self):
        import fonts.cnr15
        #wri = Writer(self.fb, fonts.cnr15, 128, 117, False)
        #wri.printstring('Hello, World!')
        textbox = gui.Textbox(fonts.cnr15, 128)
        textbox.set_text("A")
        self.fb.blit(textbox.fb, 0, 10)
        fbc = FrameBuffer(bytearray(b"\xFFFF"), 1, 1, RGB565)
        self.fb.blit(fbc, 0, 0)
        self.update()

