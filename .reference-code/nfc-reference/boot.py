# External dependancies:
import network
import gc
import time
# Custom dependancies:
from fun import *

testing:bool=False

gc.collect()

print("\n")

myNets = read_json("nets.json")
nets = scan()

accNets=[]

for net in nets:
    netName=net[0].decode('utf-8')
    if testing:
        print(f"Network: {netName}")
    if netName in myNets.keys():
        accNets.append((netName, myNets[netName]))
        print(f"Found known network: {netName}")
        
priority=None
for net in accNets:
    if priority==None or net[1][1] < priority[1][1]:
        priority=net
        
ssid=priority[0]
pswd=priority[1][0]

print(f"Attempting connection to network: {ssid}\n")
connect(ssid, pswd)