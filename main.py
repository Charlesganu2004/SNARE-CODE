import time
from machine import Pin, SoftI2C
from Button import Button
from Storage import Storage
from Ultrasonic import Ultrasonic
from IR_Sensor import D6T
from Motor_Control import MotorControl
import Wifi_manager
from Bluetooth_manager import BluetoothManager
import config

# --- Sensors ---
ultra1 = Ultrasonic(config.ULTRA1_TRIG, config.ULTRA1_ECHO, max_distance=500)
ultra2 = Ultrasonic(config.ULTRA2_TRIG, config.ULTRA2_ECHO, max_distance=500)
ultra3 = Ultrasonic(config.ULTRA3_TRIG, config.ULTRA3_ECHO, max_distance=500)
ultra4 = Ultrasonic(config.ULTRA4_TRIG, config.ULTRA4_ECHO, max_distance=500)

# IR Sensors using SoftI2C for flexible GPIO pins
ir1_i2c = SoftI2C(sda=Pin(config.IR1_SDA), scl=Pin(config.IR1_SCL), freq=100000)
ir2_i2c = SoftI2C(sda=Pin(config.IR2_SDA), scl=Pin(config.IR2_SCL), freq=100000)

ir1 = D6T(config.IR1_SDA, config.IR1_SCL)
ir1.i2c = ir1_i2c
ir2 = D6T(config.IR2_SDA, config.IR2_SCL)
ir2.i2c = ir2_i2c

motor = MotorControl()
button = Button()
bluetooth = BluetoothManager()

# --- LEDs ---
red_led = Pin(config.RED_LED_PIN, Pin.OUT)     # external red LED
green_led = Pin(config.GREEN_LED_PIN, Pin.OUT) # onboard Pico LED

# --- Constants ---
DATA_LIMIT = 50
ROTATION_TIME = 80  # seconds for full 360 degrees rotation

# --- Global stop flag ---
stop_flag = False

# --- LED helper functions ---
def red_on(): red_led.value(1)
def red_off(): red_led.value(0)
def green_on(): green_led.value(1)
def green_off(): green_led.value(0)

def flash_both(duration=0.2):
    red_on(); green_on()
    time.sleep(duration)
    red_off(); green_off()
    time.sleep(duration)

def flash_green(times=1, duration=0.5):
    for _ in range(times):
        green_on(); time.sleep(duration)
        green_off(); time.sleep(duration)

# --- Stop button check ---
def check_stop():
    global stop_flag
    if button.pressed():
        start = time.time()
        while button.pressed():
            time.sleep(0.1)
            if time.time() - start >= 30:
                stop_flag = True
                print("STOP triggered by user!")
                for _ in range(3):
                    red_on(); green_on(); time.sleep(0.1)
                    red_off(); green_off(); time.sleep(0.1)
                return True
    return False

# --- Scanning function ---
def scan_with_rotation():
    global stop_flag
    print("Starting 360° scan (1m20s)")

    # Flash green LED for 5 seconds at start
    start_time = time.time()
    while time.time() - start_time < 5:
        if stop_flag or check_stop():
            return
        green_on(); time.sleep(0.5)
        green_off(); time.sleep(0.5)

    red_on()               # solid red during scan
    motor.set_speed_percent(40)  # slow rotation
    start = time.time()

    while time.time() - start < ROTATION_TIME:
        if stop_flag or check_stop():
            motor.stop()
            red_off()
            return

        # --- Read IR sensors ---
        ir_results = [ir1.check_hidden_camera(), ir2.check_hidden_camera()]

        # --- Combine ultrasonic with IR detection ---
        heat_detected = any(r in ["Hidden Camera", "Maybe Hidden Camera"] for r in ir_results)
        ultra_results = [u.check_hidden_camera(heat_detected=heat_detected) for u in [ultra1, ultra2, ultra3, ultra4]]

        # --- Store scan data ---
        data = Storage.load()
        if len(data) < DATA_LIMIT:
            data.append({"ultra": ultra_results, "ir": ir_results, "timestamp": time.time()})
            Storage.save(data)

        # --- LED feedback ---
        if "Hidden Camera" in ir_results + ultra_results or "Maybe Hidden Camera" in ir_results + ultra_results:
            flash_both(0.2)
            red_on()  # back to solid red

        time.sleep(1)

    motor.stop()
    red_off()
    print("Scan complete.")

# --- Long press action: Wi-Fi + Bluetooth setup ---
def long_press_action():
    global stop_flag
    print("Long press detected: activating Bluetooth + Wi-Fi setup")
    bluetooth.start()
    led_flash_interval = 0.5

    Wifi_manager.start_setup()  # Pico becomes Access Point

    # Flash red while connecting
    while not stop_flag:
        red_led.value(int(time.time() % (led_flash_interval*2) < led_flash_interval))
        if Wifi_manager.connect_wifi():
            red_off()
            print("Wi-Fi connected. Sending stored data...")
            Storage.clear()
            print("Data sent and cleared.")
            break
        if check_stop():
            break
        time.sleep(0.2)

# --- Boot: initial scan ---
print("Device powering on: initial scan")
scan_with_rotation()

# --- Main loop ---
while True:
    if stop_flag:
        print("Execution stopped by user.")
        motor.stop()
        red_off()
        green_off()
        break

    if button.pressed():
        press_start = time.time()
        while button.pressed():
            time.sleep(0.1)
        press_duration = time.time() - press_start

        if press_duration >= 10:
            long_press_action()  # Long press -> Wi-Fi + Bluetooth
        elif press_duration >= 5:
            scan_with_rotation() # Short press -> scan again

    check_stop()
    time.sleep(0.2)
