# Json:
import json

def read_json(path:str) -> list|dict|None:
    if not path.endswith(".json"):
        return None
    with open(path, 'r', encoding='utf-8') as file:
        return json.load(file)

def write_json(path:str, conts:list|dict) -> bool:
    with open(path, 'w', encoding='utf-8') as file:
        json.dump(conts, file)
    return conts == read_json(path)

def try_read_json(chkPath:str, mkOnFail:bool=False, placeHolder:type(list)|type(dict)=type(dict)): # returns contents if file exists, None if file DNE and not created, or filepath/filename if DNE and created
    try:
        return read_json(chkPath)
    except OSError:
        if mkOnFail:
            if placeHolder == type(list):
                write_json(chkPath, [])
            else:
                write_json(chkPath, {})
            return chkPath
        else:
            return None
        
# Network:
import network
import time

def getWLan(activate:bool = True) -> network.WLAN:
    wlan = network.WLAN(network.STA_IF)
    wlan.active(activate)
    return wlan

def scan() -> list:
    wlan=getWLan()
    nets = wlan.scan()
    return nets

def netInfo(print_details:bool=True) -> tuple:
    wlan=getWLan()
    info=wlan.ifconfig()
    if print_details:
        print("Network info:")
        print(f"IP Address:\t\t{info[0]}")
        print(f"SubNet Mask:\t\t{info[1]}")
        print(f"Gateway:\t\t{info[2]}")
        print(f"Primary DNS Server(s):\t{info[3]}")
    return info

def connected(print_details:bool=True) -> bool:
    wlan=getWLan()
    if wlan.isconnected():
        if print_details:
            print("Network Status: CONNECTED\n")
        return True
    else:
        if print_details:
            print("Network Status: DISCONNECTED")
        return False

def connect(ssid:str, pswd:str, print_details:bool=True, timeout:int=10) -> bool:
    # Initialise wlan object and initiate connection attempt
    wlan=getWLan()
    wlan.connect(ssid, pswd)
    
    # Wait until connected or timeout reached
    start_time = time.time()
    while not wlan.isconnected() and (time.time() - start_time) < timeout:
        pass
    
    # Determine and present outcome
    if wlan.isconnected():
        if print_details:
            print("Connection attempt successful\n")
        return True
    else:
        if print_details:
            print("Connection attempt failed")
        return False