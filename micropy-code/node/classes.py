# Built-in dependancies:
import time
from machine import Pin, UART, I2C
from neopixel import NeoPixel
# Specialised dependancies:
import pn532
from PN532 import PN532_I2C

# Custom dependancies:
from fun import *

class UID():
    def __init__(self, value:bytes):
        self.__bytes:bytes=value
        self.__value:List[int] = list(self.__bytes)

    def __str__(self) -> str:
        ret=[]
        for value in self.__value:
            ret.append(f"{value:02x}")
        return f"UID: {"-".join(ret)}"

    def getValue(self, retType:type) -> str|list:
        if retType == list:
            return self.__value
        elif retType == str:
            ret=""
            for value in self.__value:
                ret+=f"{value:02x}"
            return ret
        else:
            print(f"ERROR can only return value as string or list; {retType} not supported")

    def getBytes(self):
        return self.__bytes

    def numBytes(self) -> int:
        return len(self.__value)


class NFC_I2C(PN532_I2C):
    def __init__(self, i2c:I2C, debug:bool=False):
        super().__init__(i2c, debug=debug)

    def getUid(self):
        passive=self.getPassive()
        uid=passive[-1]
        return uid

    def getTg(self):
        passive=self.getPassive()
        tg=passive[0]
        return tg

    def readPassive(self, tout:int=10000):
        data=self.list_passive_target(timeout=tout)
        if data:
            return data
        else:
            return None

    def getPassive(self):
        cardFound=False
        while not cardFound:
            try:
                passive=self.readPassive()
                if passive:
                    cardFound=True
                    return passive
            except Exception as e:
                continue

    def autoAuth(self, block):
        uid=self.getUid()
        tg=self.getTg()
        key=[0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]
        key_type=0x01
        self.mifare_classic_auth(uid=uid, tg=tg, key=key, key_type=key_type, block=block)

    def readUltraLight(self):
        tg=self.getTg()
        uid=self.getUid()
        start=4
        raw_data = self.mifare_classic_read(tg, start)
        print(f"Raw-Data: {raw_data}")
        decoded=""
        for c in raw_data:
            try:
                decoded += chr(c)
            except Exception as e:
                print(f"Unicode Error: ", e)
        print(f"Decoded-Data: {decoded}")

    def writeUltralight(self, data, page=4):
        """
        Writes exactly 4 bytes of data to a specific MIFARE Ultralight page number.
        data: must be a bytes/bytearray object of exactly 4 bytes.
        """
        tg=self.getTg()
        if len(data) != 4:
            raise ValueError("MIFARE Ultralight writes must be exactly 4 bytes (1 page) at a time.")
        
        # 0x40 = _CMD_InDataExchange
        # 0xA0 = _MIFARE_WRITE
        # Build the exact hardware packet parameters: [tg, command, page, byte1, byte2, byte3, byte4]
        param = [tg, 0xA0, page] + list(data)
        
        # Send command over I2C
        self.write_cmd(0x40, param)
        
        if not self.wait_ready(): 
            raise OSError("Device not ready")
            
        res = self.read_frame()
        
        # Check if response code matches expected InDataExchange response
        if res[0] != 0x41: 
            raise OSError("Invalid response from device")
        if res[1] & 0x3F != 0x00:
            raise OSError("Write command failed (card rejected it)")
        
        print(f"Successfully wrote 4 bytes to Page {page}!")

    def readBlock(self, block):
        self.autoAuth(block)
        self.mifare_classic_read(self.getTg(), block)


class NFC(pn532.PN532Uart):
    def __init__(self, uart_num:int, tx:int, rx:int, baudRt:int=9600, debug:bool=False):
        self.uart=uart_num
        self.tx=tx
        self.rx=rx
        super().__init__(uart_num, tx, rx, debug=debug)

    def debugInfo(self) -> str:
        return f"Firmware: {self.get_firmware_version()}\nUART: {self.uart}\ntx/rx: {self.tx}/{self.rx}"

    def readUID(self, timeout:int=-1):
        def tryRead() -> UID|None:
            try:
                uid=self.read_passive_target()
                time.sleep(0.2)
            except Exception as e:
                #print(f"Err: {e}")
                self.release_targets()
                return None
            uid=UID(uid)
            return uid
        cardID=None
        if timeout > 0:
            startTime=time.time()
            while cardID == None and (time.time() - startTime) < timeout:
                cardID=tryRead()
            return cardID
        else:
            while cardID == None:
                cardID = tryRead()
            return cardID

    def test_read_id(self):
        #print(f"\nReady to read NFC card ID . . .")
        uid=self.readUID(25)
        if not uid == None:
            print(f"NFC card detected:\n{uid}")
        else:
            print("No NFC card read/detected")

    def test_write_data(self, data:str="Hello World!"):
        print(f"Writing data: \"{data}\" . . .")
        writeData=bytearray(data, 'utf-8')
        self._write_frame(writeData)

    def test_read_data(self):
        print(f"\nReady to read NFC card data . . .")
        try:
            data=self.wait_read_len(len=1)
            print(data)
        except Exception as e:
            print("Encountered error: ", e)

colors=read_json("colors.json")

class Color():
    def __init__(self, rgb:tuple(float, float, float)|None=None, colorName:str|None=None):
        if (rgb != None and colorName != None) or (rgb == None and colorName == None):
            self.__red = 1
            self.__green = 1
            self.__blue = 1
            self.__color = ""
        elif colorName == None:
            self.__red:float=rgb[0]
            self.__green:float=rgb[1]
            self.__blue:float=rgb[2]
            self.__color = ""
        elif rgb == None:
            if not colorName in colors.keys():
                self.__red = 1
                self.__green = 1
                self.__blue = 1
                self.color = ""
            else:
                col=colors[colorName]
                self.__color=colorName
                self.__red = col[0]
                self.__green = col[1]
                self.__blue = col[2]
        if self.__red > 1:
            self.__red = self.__red % 1
        if self.__green > 1:
            self.__green = self.__green % 1
        if self.__blue > 1:
            self.__blue = self.__blue % 1

    def __str__(self) -> str:
        ret="Color: "
        if self.__color != "":
            ret+=f"{self.__color}\n"
        else:
            ret+="\n"
        ret+=f"R:{self.__red} | "
        ret+=f"G:{self.__green} | "
        ret+=f"B:{self.__blue}"
        return ret

    def normalize(self, brightness:int) -> tuple[int, int, int]:
        if brightness > 255:
            brightness = 255
        elif brightness < 0:
            brightness = 0
        red=round(self.__red*brightness)
        green=round(self.__green*brightness)
        blue=round(self.__blue*brightness)
        if red > 255:
            red = 255
        elif red < 0:
            red = 0
        if green > 255:
            green = 255
        elif green < 0:
            green = 0
        if blue > 255:
            blue = 255
        elif blue < 0:
            blue = 0
        return (red, green, blue)
        
    def getRed(self, brightness:int = -1) -> int|float:
        if brightness < 0:
            return self.__red
        elif brightness > 255:
            brightness = 255
        else:
            return round(self.__red*brightness)

    def getGreen(self, brightness:int = -1) -> int|float:
        if brightness < 0:
            return self.__green
        elif brightness > 255:
            brightness = 255
        else:
            return round(self.__green*brightness)

    def getBlue(self, brightness:int = -1) -> int|float:
        if brightness < 0:
            return self.__blue
        elif brightness > 255:
            brightness = 255
        else:
            return round(self.__blue*brightness)


class Pixels(NeoPixel):
    def __init__(self, pin:int, pixCount:int, brightness:int=255):
        self.__numPixels:int=pixCount
        self.__pinNum:int=pin
        if brightness > 255:
            self.__brightness = 255
        elif brightness < 0:
            self.__brightness = 0
        else:
            self.__brightness = brightness
        super().__init__(Pin(self.__pinNum), self.__numPixels)

    def debugInfo(self) -> str:
        return "!WIP!"

    def nameToColor(self, name:str) -> tuple[float, float, float]|None:
        if name in self.colors.keys():
            return self.colors[name]
        else:
            return None

    def setPixel(self, pixel:int, color:Color, brightness:int=-1, writeCol:bool=True):
        if brightness < 0 or brightness > self.__brightness:
            brightness = self.__brightness
        normCol=color.normalize(brightness)
        #print(f"Pixel #{pixel}\nNormalized color: {normCol}\n")
        self[pixel]=normCol
        if writeCol:
            self.write()

    def dispAll(self, color:Color|tuple|str, brightness=-1):
        if brightness < 0 or brightness > self.__brightness:
            brightness = self.__brightness
        if type(color) != Color:
            color = Color(color)
        for i in range(self.__numPixels):
            self.setPixel(i, color, brightness)
        self.write()

    def off(self):
        self.dispAll(color="off")

    def flare(self, color:Color|tuple[float|int, float|int, float|int]|str, speed:int=5):
        step:int=2
        per=1/(speed*5)
        if type(color) == str:
            color = Color(colorName=color)
        elif type(color) == tuple:
            color = Color(rgb=color)

        bright = 0

        while bright <= self.__brightness:
            self.dispAll(color, brightness=bright)
            bright += step
            #print(f"Brightness: {bright}")
            time.sleep(per)
        bright = self.__brightness
        self.dispAll(color, brightness=bright)

        while bright >= 0:
            self.dispAll(color, brightness=bright)
            bright -= step
            #print(f"Brightness: {bright}")
            time.sleep(per)
        bright = 0
        self.dispAll(color, brightness=bright)

    def test(self):
        print("Testing . . .")
        for col in colors.keys():
            print(f"Flaring color: {col}")
            self.flare(color=col)
        print("done")