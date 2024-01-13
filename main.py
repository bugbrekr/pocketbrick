import machine
import time
import uasyncio
import network
import functions
from ST7735 import TFT
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

jacc_os = jacc.JACC_OS(display, keypad)
jacc_os.run_program(programs.SimpleCalculator)
