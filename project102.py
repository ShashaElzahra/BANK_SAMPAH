import time
import sys
import requests
import math
import random
import RPi.GPIO as GPIO
from hx711 import HX711

TOKEN = "BBFF-ylrN8OCsbsEZ5m9TmiFfEHcoos5rX8"
DEVICE_LABEL = "bank-sampah"
VARIABLE_LABEL_1 = "data"

hx = HX711(5, 6)

def setup():
    hx.set_reading_format("MSB", "MSB")
    hx.set_reference_unit(2172)
    hx.reset()
    hx.tare()

def sensor_berat():
    val = max(0, int(hx.get_weight(5)))
    hx.power_down()
    hx.power_up()
    hx.reset()
    hx.tare()
    return val

def build_payload(nama, nis, berat):
    payload = {VARIABLE_LABEL_1: {"value": berat, "context": {"nama": nama, "nis": nis}}}
    return payload

def post_request(payload):
    # Creates the headers for the HTTP requests
    url = "http://industrial.api.ubidots.com"
    url = "{}/api/v1.6/devices/{}".format(url, DEVICE_LABEL)
    headers = {"X-Auth-Token": TOKEN, "Content-Type": "application/json"}

    # Makes the HTTP requests
    status = 400
    attempts = 0
    while status >= 400 and attempts <= 5:
        req = requests.post(url=url, headers=headers, json=payload)
        status = req.status_code
        attempts += 1
        time.sleep(1)

    # Processes results
    print(req.status_code, req.json())
    if status >= 400:
        print("[ERROR] Could not send data after 5 attempts, please check \
            your token credentials and internet connection")
        return False

    print("[INFO] request made properly, your device is updated")
    return True

def main():
    print("Silakan simpan sampah dan isi data berikut ini! \n")
    nama = input("Masukkan Nama : ")
    nis = input("Masukkan NIS : ")
    berat = sensor_berat()
    print("Berat sampah : " + str(berat))

    # Kirim data
    payload = build_payload(nama, nis, berat)
    print("[INFO] Attemping to send data")
    post_request(payload)
    print("[INFO] finished \n")

if __name__ == '__main__':
    try:
        setup()
        while True:
            main()
    except (KeyboardInterrupt, SystemExit):
        GPIO.cleanup()
        sys.exit()

