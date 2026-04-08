from machine import UART, Pin
import config

class GPS:
    def __init__(self):
        self.uart = UART(0, baudrate=9600, tx=Pin(config.GPS_TX), rx=Pin(config.GPS_RX))

    def read(self):
        if self.uart.any():
            return self.uart.readline()
        return None
