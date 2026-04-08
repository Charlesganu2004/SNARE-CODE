from machine import Pin
import config

class Button:
    def __init__(self):
        self.button = Pin(config.BUTTON_PIN, Pin.IN, Pin.PULL_UP)

    def pressed(self):
        return self.button.value() == 0
