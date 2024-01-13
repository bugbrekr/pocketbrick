import socket
import struct
import machine
import time
from ST7735 import TFT
from sysfont import sysfont
import sdcard
import os
from framebuf import FrameBuffer, RGB565

NTP_DELTA = 2208988800
NTP_HOST = "192.46.215.60"
TZ_DELTA = 19800

def TFTColor( aR, aG, aB ) :
  return ((aR & 0xF8) << 8) | ((aG & 0xFC) << 3) | (aB >> 3)

def synchronise_time():
    NTP_QUERY = bytearray(48)
    NTP_QUERY[0] = 0x1B
    addr = socket.getaddrinfo(NTP_HOST, 123)[0][-1]
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.settimeout(1)
        res = s.sendto(NTP_QUERY, addr)
        msg = s.recv(48)
    finally:
        s.close()
    val = struct.unpack("!I", msg[40:44])[0]
    t = val - NTP_DELTA + TZ_DELTA
    tm = time.gmtime(t)
    machine.RTC().datetime((tm[0], tm[1], tm[2], tm[6] + 1, tm[3], tm[4], tm[5], 0))

class Keypad:
    def __init__(self):
        
        self.DEBOUNCING_THRESHOLD_MS = 100
        self.LONG_PRESS_THRESHOLD_MS = 600
        self.EXTRA_LONG_PRESS_THRESHOLD_MS = 3000
        
        self.button_pin_map = [None, None, 4, 1, 9, 6, 3, 0, None, None, None, None, 11, 8, 5, 2, None, None, None, None, 7, 10] # PIN_NUMBER --> KEYPAD_INDEX
        self.button_id_map = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l"] # KEYPAD_INDEX --> KEYPAD_ID
        self.button_pin_id_map = {
            "7": "a", "3": "b", "15": "c",
            "6": "d", "2": "e", "14": "f",
            "5": "g", "20": "h", "13": "i", 
            "4": "j", "21": "k", "12": "l"
        } # PIN_NUMBER --> KEYPAD_ID
        self.button_keypad_map = {
            "a": ["1", "HOME"], "b": ["2", "UP"], "c": ["3", "ENTER"],
            "d": ["4", "LEFT"], "e": ["5", "SELECT"], "f": ["6", "RIGHT"],
            "g": ["7", "BLNK"], "h": ["8", "DOWN"], "i": ["9", "BLNK"],
            "j": ["MS", "MS"],  "k": ["0", "BLNK"], "l": ["BKSPCE", "BACK"]
        } # KEYPAD_ID --> FUNCTION?
        self.button_up_ticks = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.button_down_ticks = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
        self.button_pins = {}
        for btn_id in self.button_pin_id_map:
            self.button_pins[self.button_pin_id_map[btn_id]] = machine.Pin(
                int(btn_id),
                machine.Pin.IN,
                machine.Pin.PULL_UP
            )
            self.button_pins[self.button_pin_id_map[btn_id]].irq(
                trigger=machine.Pin.IRQ_FALLING,
                handler=self.btn_down,
                hard=False
            )
        self.callback_function = self._callback
    
    def _get_btn_index(self, p):
        return self.button_pin_map[int(str(p).split(",")[0][8:])]
    
    def _get_btn_id(self, p):
        return self.button_id_map[self._get_btn_index(p)]
    
    def btn_down(self, p):
        p.irq(
            trigger=machine.Pin.IRQ_RISING,
            handler=self.btn_up,
            hard=False
        )
        p_ind = self._get_btn_index(p)
        self.button_down_ticks[p_ind] = time.ticks_ms()
    def btn_up(self, p):
        p.irq(
            trigger=machine.Pin.IRQ_FALLING,
            handler=self.btn_down,
            hard=False
        )
        p_ind = self._get_btn_index(p)
        if time.ticks_diff(time.ticks_ms(), self.button_up_ticks[p_ind]) < self.DEBOUNCING_THRESHOLD_MS:
            self.button_down_ticks[p_ind] = 99999999999999
            return
        self.button_up_ticks[p_ind] = time.ticks_ms()
        click_duration = time.ticks_diff(time.ticks_ms(), self.button_down_ticks[p_ind])
        p_id = self.button_id_map[p_ind]
        self.callback_function(p_id, click_duration)
    def register_callback(self, callback_function):
        self.callback_function = callback_function
    def deregister_callback(self):
        self.callback_function = self._callback
    def _callback(self, p_id, dur):
        if dur < self.LONG_PRESS_THRESHOLD_MS:
            self.short_press(p_id)
        elif dur >= self.LONG_PRESS_THRESHOLD_MS and dur < self.EXTRA_LONG_PRESS_THRESHOLD_MS:
            self.long_press(p_id)
        elif dur >= self.EXTRA_LONG_PRESS_THRESHOLD_MS:
            self.extra_long_press(p_id)
    def short_press(self, p_id):
        print(p_id, "short press")
    def long_press(self, p_id):
        print(p_id, "long press")
    def extra_long_press(self, p_id):
        print(p_id, "extra long press")

class SDCard:
    def __init__(self,cs_pin:int=9, spi_id:int=1, sck_pin:int=10, mosi_pin:int=11, miso_pin:int=8):
        cs = machine.Pin(cs_pin, machine.Pin.OUT)
        spi = machine.SPI(spi_id,
            baudrate=1000000,
            polarity=0,
            phase=0,
            bits=8,
            firstbit=machine.SPI.MSB,
            sck=machine.Pin(sck_pin),
            mosi=machine.Pin(mosi_pin),
            miso=machine.Pin(miso_pin))
        self.sd = sdcard.SDCard(spi, cs)
        self.vfs = os.VfsFat(self.sd)
        self.self.mount_point = ""
    def mount(self, mount_point:str="/disk"):
        self.mount_point = mount_point
        os.mount(self.vfs, mount_point)
    def unmount(self):
        if self.mount_point != "":
            os.unmount(self.mount_point)
            self.mount_point = ""

class Sensors:
    BATTERY_BASE_VOLTAGE = 3.4
    BATTERY_CONVERSION_FACTOR = (BATTERY_BASE_VOLTAGE / (65535)) * 3
    def __init__(self):
        machine.Pin(25, machine.Pin.OUT).value(True)
        machine.Pin(29, machine.Pin.IN)
        self.battery_adc = machine.ADC(3)
    def _get_battery_voltage(self):
        return self.battery_adc.read_u16()*self.BATTERY_CONVERSION_FACTOR
    def __getitem__(self, key):
        if key == "battery_voltage":
            return round(self._get_battery_voltage(), 2)
        elif key == "battery_percent":
            return round((self._get_battery_voltage()-3.2)/.01)
        else:
            raise KeyError

class Display:
    def __init__(self, spi_id=1, sck_pin=10, mosi_pin=11, bl_pin=28):
        self._bl = machine.Pin(bl_pin, machine.Pin.OUT, machine.Pin.PULL_DOWN)
        self.bl(False)
        spi = machine.SPI(spi_id, baudrate=20000000, polarity=0, phase=0,
            sck=machine.Pin(sck_pin), mosi=machine.Pin(mosi_pin), miso=None
        )
        self.tft=TFT(spi,16,17,18, 3)
        self.tft.initr()
        self.tft.rgb(False)
    def bl(self, value=None):
        if value==None:
            return bool(self._bl.value())
        elif value==True:
            self._bl.value(1)
        elif value==False:
            self._bl.value(0)
    def color(self, r, g, b):
        r,g,b = int(r/4),int(g/4),int(b/4)
        return (r << 12) + (g << 6) + b
