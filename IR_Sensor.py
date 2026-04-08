from machine import SoftI2C, Pin
import struct

class D6T:
    def __init__(self, sda, scl, heat_min=27, heat_max=55):
        # SoftI2C to allow any GPIO pins
        self.i2c = SoftI2C(
            sda=Pin(sda),
            scl=Pin(scl),
            freq=100000
        )
        self.address = 0x0A
        self.heat_min = heat_min
        self.heat_max = heat_max

    def read(self):
        try:
            data = self.i2c.readfrom(self.address, 19)
        except OSError:
            # If no response, return all zeros
            return [0] * 8
        temps = []
        for i in range(1, 17, 2):
            temp = struct.unpack('<h', data[i:i+2])[0] / 10
            temps.append(temp)
        return temps

    def check_hidden_camera(self):
        temps = self.read()
        min_temp = min(temps)
        max_temp = max(temps)

        # Detection logic
        if self.heat_min <= min_temp <= self.heat_max and self.heat_min <= max_temp <= self.heat_max:
            return "Hidden Camera"
        elif any(self.heat_min <= t <= self.heat_max for t in temps):
            return "Maybe Hidden Camera"
        else:
            return "No Detection"
