# Built-in dependancies:
import time
from machine import Pin, UART
from neopixel import NeoPixel
# Specialised dependancies:
import pn532

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


class NFC(pn532.PN532Uart):
    def __init__(self, uart_num:int, tx:int, rx:int, baudRt:int=9600, debug:bool=True):
        self.uart=uart_num
        self.tx=tx
        self.rx=rx
        super().__init__(uart_num, tx, rx)

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

    def test(self):
        print(f"\nReady to read NFC card . . .")
        uid=self.readUID(25)
        if not uid == None:
            print("NFC card detected:")
            print("Registering Card . . . ", end="")
            id=uid.getValue(str)
            registered=registerCard(id)
            if registered:
                print("SUCCESS")
            else:
                print("FAILED")
        else:
            print("No NFC card read/detected")

        print(f"Known/Registered cards: {registeredCards()}")

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