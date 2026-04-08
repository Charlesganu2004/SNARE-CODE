# Wifi_manager.py
import network
import socket
import json
import time

CONFIG_FILE = "wifi.json"

def extract_ssid(request):
    try:
        request_str = request.decode()
        ssid_start = request_str.find("ssid=") + 5
        ssid_end = request_str.find("&", ssid_start)
        if ssid_end == -1:
            ssid_end = len(request_str)
        return request_str[ssid_start:ssid_end]
    except:
        return None

def extract_password(request):
    try:
        request_str = request.decode()
        pass_start = request_str.find("password=") + 9
        pass_end = request_str.find("&", pass_start)
        if pass_end == -1:
            pass_end = len(request_str)
        return request_str[pass_start:pass_end]
    except:
        return None

def save_wifi(ssid, password):
    data = {"ssid": ssid, "password": password}
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f)

def load_wifi():
    try:
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    except:
        return None

def connect_wifi():
    creds = load_wifi()
    if not creds:
        return False

    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(creds["ssid"], creds["password"])

    timeout = 15
    while timeout > 0:
        if wlan.isconnected():
            print("Connected:", wlan.ifconfig())
            return True
        time.sleep(1)
        timeout -= 1

    return False

def start_setup():
    ap = network.WLAN(network.AP_IF)
    ap.active(True)
    ap.config(essid="Pico_Setup")

    addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
    server = socket.socket()
    server.bind(addr)
    server.listen(1)
    print("Connect phone to Pico_Setup WiFi")

    while True:
        client, addr = server.accept()
        request = client.recv(1024)

        ssid = extract_ssid(request)
        password = extract_password(request)

        if ssid and password:
            save_wifi(ssid, password)
            client.send(b"WiFi Saved. Rebooting.")
            client.close()
            break
        client.close()
