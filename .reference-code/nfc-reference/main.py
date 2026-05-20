# External dependancies:
import time
from os import listdir
from sys import exit
# Custom dependancies:
from fun import *
from classes import *

def printDebugInfo(nfcObj:NFC=None, pixObj:Pixels=None, printAll:bool=True, lastActn:bool=False):
    print("DEBUG INFO:")
    if nfcObj:
        print(f"\n\nNFC-object debug info:\n{nfcObj.debugInfo()}")
    if pixObj:
        print(f"\n\nNeoPixel-LED debug info: {pixObj.debugInfo()}")
    if printAll:
        print(f"\n\nDirectory contents: {listdir()}")

    if lastActn:
        print("Exiting . . .")
        exit()

pins = read_json("pinout.json")

nfc=NFC(2, pins["tx2"], pins["rx2"])
nfc.SAM_configuration()

idToColor=try_read_json("id-to-color.json", True, type(dict))

pixels=Pixels(pins["pixels"], 5, 150)

printDebugInfo(nfc, pixels, lastActn=True)

colors=read_json("colors.json")