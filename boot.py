import network
import gc
import micropython
#import machine
#import time

network.country("IN")
network.hostname("pocketbrick")

micropython.alloc_emergency_exception_buf(100)

#led = machine.Pin("LED", machine.Pin.OUT)
#led.toggle()
#time.sleep(0.5)
#led.toggle()