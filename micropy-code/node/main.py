# External dependancies:
from time import sleep_ms
from os import listdir
from sys import exit
from machine import Pin, I2C
# Custom dependancies:
from fun import *
from classes import *

pins = read_json("pinout.json")

i2c=I2C(0, sda=Pin(22), scl=Pin(23), freq=100000)
print(f"I2C Devices: {i2c.scan()}")

nfc = NFC_I2C(i2c, debug=True)
nfc.set_mode()

val=nfc.readUltraLight()