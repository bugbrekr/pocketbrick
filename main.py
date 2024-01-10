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

def test_main():
    tft.fill(TFT.BLACK)
    tft.text((0, 0), "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Curabitur adipiscing ante sed nibh tincidunt feugiat. Maecenas enim massa, fringilla sed malesuada et, malesuada sit amet turpis. Sed porttitor neque ut ante pretium vitae malesuada nunc bibendum. Nullam aliquet ultrices massa eu hendrerit. Ut sed nisi lorem. In vestibulum purus a tortor imperdiet posuere. ", TFT.WHITE, sysfont, 1)
    time.sleep_ms(1000)

    tftprinttest()
    time.sleep_ms(4000)

    testlines(TFT.YELLOW)
    time.sleep_ms(500)

    testfastlines(TFT.RED, TFT.BLUE)
    time.sleep_ms(500)

    testdrawrects(TFT.GREEN)
    time.sleep_ms(500)

    testfillrects(TFT.YELLOW, TFT.PURPLE)
    time.sleep_ms(500)

    tft.fill(TFT.BLACK)
    testfillcircles(10, TFT.BLUE)
    testdrawcircles(10, TFT.WHITE)
    time.sleep_ms(500)

    testroundrects()
    time.sleep_ms(500)

    testtriangles()
    time.sleep_ms(500)


def get_wifi_details():
    aps = wlan.scan()
    for ap in aps:
        if ap[0] == b"Network_24":
            return ap
        
def main():
    display.bl(True)
    tft.text((0, 0), "Enabling network...", TFT.WHITE, sysfont, 1)
    wlan.active(True)
    tft.fillrect((0, 0), (127, 8), 0)

    tft.text((0, 0), "Connecting...", TFT.WHITE, sysfont, 1)
    wlan.connect("Network_24", "Internet@localhost")
    while True:
        if wlan.status() == 3:
            break
        elif wlan.status() < 0:
            tft.fillrect((0, 0), (127, 8), 0)
            tft.text((0, 0), "Failed to connect.", TFT.WHITE, sysfont, 1)
            while True:
                time.sleep(1)
    tft.fillrect((0, 0), (127, 8), 0)

    tft.text((0, 0), "Synchronising...", TFT.WHITE, sysfont, 1)
    functions.synchronise_time()
    tft.fillrect((0, 0), (127, 8), 0)

    dt_prev = ()
    while True:
        time.sleep(0.2)
        dt = machine.RTC().datetime()
        if dt == dt_prev:
            continue
        dt_str = tuple("{:0>2}".format(str(i)) for i in dt)
        tft.fillrect((0, 0), (127, 16), 0)
        tft.text((0, 0), f"{dt_str[4]}:{dt_str[5]}:{dt_str[6]}", TFT.WHITE, sysfont, 1)
        tft.text((0, 8), f"{dt_str[2]}/{dt_str[1]}/{dt_str[0]}", TFT.WHITE, sysfont, 1)
        dt_prev = dt

def main2():
    display.bl(True)
    tft.text((0, 0), "Enabling network...", TFT.WHITE, sysfont, 1)
    wlan.active(True)
    tft.fillrect((0, 0), (127, 8), 0)
    while True:
        time.sleep(1)
        details = get_wifi_details()
        tft.fillrect((0, 0), (127, 8), 0)
        tft.text((0, 0), f"RSSI: {details[3]}", TFT.WHITE, sysfont, 1)

def main3():
    display.bl(True)
    tft.fillrect((0, 0), (127, 8), 0)
    tft.text((0, 0), "Starting AP...", TFT.WHITE, sysfont, 1)
    ap = network.WLAN(network.AP_IF)
    ap.config(essid="TestNet", password="TestPass")
    ap.active(True)

    s = socket.socket()
    s.bind(("0.0.0.0", 8080))
    s.listen(1)
    
    tft.fillrect((0, 0), (127, 8), 0)
    tft.text((0, 0), "Listening...", TFT.WHITE, sysfont, 1)
    
    while True:
        sock, addr = s.accept()
        print("client connected", addr)
        tft.fillrect((0, 0), (127, 8), 0)
        tft.text((0, 0), "Client connected.", TFT.WHITE, sysfont, 1)
        while True:
            print("waiting for incoming data")
            data = sock.recv(100).decode()
            if data != None:
                break
        tft.fillrect((0, 0), (127, 8), 0)
        tft.text((0, 0), data, TFT.WHITE, sysfont, 1)

def main4():
    display.bl(True)
    tft.fill(0)
    ba = bytearray(100 * 100 * 2)
    fb = FrameBuffer(ba, 100, 100, RGB565)
    fb.fill(255)
    tft.image(10, 10, 110, 110, fb)

jacc_os = jacc.JACC_OS(display, keypad)
jacc_os.run_program(programs.SimpleCalculator)