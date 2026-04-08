from machine import Pin, time_pulse_us
import time

class Ultrasonic:
    def __init__(self, trig, echo, min_distance=5, max_distance=500):
        self.trig = Pin(trig, Pin.OUT)
        self.echo = Pin(echo, Pin.IN)
        self.min_distance = min_distance
        self.max_distance = max_distance
        self.last_distance = None

    def read(self):
        # Trigger pulse
        self.trig.low()
        time.sleep_us(2)
        self.trig.high()
        time.sleep_us(10)
        self.trig.low()

        # Measure echo pulse width
        start = time.ticks_us()
        while self.echo.value() == 0:
            start = time.ticks_us()
        while self.echo.value() == 1:
            stop = time.ticks_us()

        # Distance in cm
        distance = (stop - start) * 0.0343 / 2
        self.last_distance = distance
        return distance

    def check_hidden_camera(self, heat_detected=False):
        distance = self.read()
        # Check if distance is within camera range
        in_range = self.min_distance <= distance <= self.max_distance

        if in_range and heat_detected:
            return "Hidden Camera"
        elif in_range or heat_detected:
            return "Maybe Hidden Camera"
        else:
            return "No Detection"
