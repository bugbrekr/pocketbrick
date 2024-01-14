from programs.BaseProgram import BaseProgram
import machine
from umqtt import MQTTClient
import json

def color(r, g, b):
    return ((b//8 & 0xF8) << 8) | ((r//8 & 0xFC) << 3) | (g//4 >> 3)

class Program(BaseProgram):
    def run(self):
        self.register_keymap([{
                "a": None, "b": "LIGHT", "c": None,
                "d": None, "e": "FAN", "f": None,
                "g": None, "h": None, "i": None,
                "j": None, "k": None, "l": None,
            }])
        with open("config.json") as f:
            config = json.loads(f.read())
        self.mqtt = MQTTClient(config["mqtt_client"], config["mqtt_host"])
        self.mqtt.connect()
    def on_keypress(self, key, _press_type, _p_id):
        self.fb.fill(0)
        if key == "LIGHT":
            self.mqtt.publish("hass", json.dumps({"name": "light", "action": "toggle"}))
            self.fb.text("Toggled light", 0, 0, color(255, 255, 255))
        elif key == "FAN":
            self.mqtt.publish("hass", json.dumps({"name": "fan", "action": "toggle"}))
            self.fb.text("Toggled fan", 0, 0, color(255, 255, 255))
        self.update()
    def exit(self):
        self.mqtt.disconnect()
