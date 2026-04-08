from machine import Pin, PWM
import config

class MotorControl:
    def __init__(self):
        self.ain1 = Pin(config.MOTOR_AIN1, Pin.OUT)
        self.ain2 = Pin(config.MOTOR_AIN2, Pin.OUT)
        self.stby = Pin(config.MOTOR_STBY, Pin.OUT)
        self.pwm = PWM(Pin(config.MOTOR_PWM))
        self.pwm.freq(1000)
        self.disable()  # Ensure motor is off at start

    def enable(self):
        self.stby.value(1)

    def disable(self):
        self.stby.value(0)

    def set_speed_percent(self, percent):
        # Clamp percent between 0 and 100
        percent = max(0, min(100, percent))
        duty = int(percent / 100 * 65535)
        self.pwm.duty_u16(duty)
        self.enable()

    def stop(self):
        self.pwm.duty_u16(0)
        self.disable()
    