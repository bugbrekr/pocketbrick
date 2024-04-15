import network
import micropython

network.country("IN")
network.hostname("pocketbrick")

micropython.alloc_emergency_exception_buf(100)