import machine
import time
import uasyncio
import network
import functions
from ST7735 import TFT, TFTColor
from sysfont import sysfont
import math
import socket
import programs
import jacc

wlan = network.WLAN(network.STA_IF)

keypad = functions.Keypad()
display = functions.Display()
sensors = functions.Sensors()

display.bl(True)
tft = display.tft
tft.fill(0)

#tft.fill(display.color(255, 0, 255))

jacc_os = jacc.JACC_OS(display, keypad, sensors)
print("initialized")
jacc_os.run_program(programs.Pong)
