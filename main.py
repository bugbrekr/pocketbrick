import machine
led = machine.Pin("LED", machine.Pin.OUT)
t = machine.Timer()
t.init(mode=1, freq=10, callback=lambda _: led.toggle())
import time
import uasyncio
import network
import functions
from ST7735 import TFT, TFTColor
from sysfont import sysfont
import math
import socket
import program_manager
import jacc

wlan = network.WLAN(network.STA_IF)
wlan.active(True)

keypad = functions.Keypad()
sensors = functions.Sensors()

sdcard = functions.SDCard()
sdcard.attach()
sdcard.mount()

display = functions.Display()
display.bl(True)

tft = display.tft
tft.fill(0)

#tft.fill(display.color(255, 0, 0))
jacc_os = jacc.JACC_OS(display, keypad, sensors, wlan, sdcard, program_manager.load_program("Launcher"))
jacc_os.launcher()

t.deinit()
led.value(0)
#jacc_os.run_program(program_manager.load_program("Launcher"))
