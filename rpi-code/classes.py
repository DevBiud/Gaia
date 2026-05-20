import board
import time
import digitalio as dio
import numpy as np
import RPi.GPIO as GPIO
from PIL import Image, ImageDraw, ImageFont
from adafruit_rgb_display import st7789
from pathlib import Path

class Screen(st7789.ST7789):
    def __init__(
            self,
            spi: board.SPI=board.SPI(),
            dc: dio.DigitalInOut=dio.DigitalInOut(board.D25),
            cs: dio.DigitalInOut=dio.DigitalInOut(board.CE0),
            bl: int=12,
            rst: dio.DigitalInOut|None=None,
            backlit:bool=True,
            width: int=240,
            native_height: int=320,
            real_height: int=280,
            baudrate: int=24000000,
            x_offset: int=0,
            y_offset: int=0,
            rotation: int=90,
            color_schemes: list[list[tuple[int, int, int]|Color]]|None=None,
            radius: int=45
        ):
        super().__init__(spi, cs=cs, dc=dc, rst=rst, width=width, height=native_height, baudrate=baudrate, x_offset=x_offset, y_offset=y_offset, rotation=rotation)
        self.real_x=self.width
        self.real_y=real_height
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(bl, GPIO.OUT)
        if backlit:
            GPIO.output(bl, GPIO.HIGH)
        else:
            GPIO.output(bl, GPIO.LOW)
        self.bl=bl
        if color_schemes:
            self.__schemes=color_schemes
        else:
            self.schemes=None
        self.radius=radius

    def test(self,
                headText:str="TEST SCREEN",
                bodyText:str="Testing . . .",
                bgCol:tuple[int,int,int]=(35,0,50),
                textCol:tuple[int,int,int]=(200,200,255),
                altTextCol:tuple[int,int,int]|None=(0,225,200),
                bordCol:tuple[int,int,int]=(200,175,0),
                bordThick:int=4,
                offset:int=15
            ):
        def makeTestGraphic() -> Image:
            if self.rotation == 90 or self.rotation == 270:
                width=280
                height=240
            else:
                width=240
                height=280

            # Create image object:
            image = Image.new("RGB", (width, height), (0, 20, 40))
            draw = ImageDraw.Draw(image)

            # Load font to use for testing:
            try:
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
            except OSError:
                font = ImageFont.load_default()

            # Draw background:
            draw.rectangle([0, 0, width, height], outline=None, fill=bgCol)

            # Draw a border to make edges clear:
            draw.rounded_rectangle([0, 0, width-((bordThick/2)-1), height-((bordThick/2)-1)], outline=bordCol, width=bordThick, radius=self.radius)

            # Draw title text:
            if not altTextCol == None:
                col=altTextCol
            else:
                col=textCol
            draw.text((offset, 40), headText, font=font, fill=col)

            # Draw body text:
            draw.text((offset, 100), bodyText, font=font, fill=textCol)

            return image

        image=makeTestGraphic()
        adj_buffer = Image.new("RGB", (320, 240), (0, 0, 0))
        adj_buffer.paste(image, (20, 0))

        self.image(adj_buffer)

    def animTest(self, numLoops:int=2, speed:int=5):
        per=3/speed
        for i in range(numLoops):
            for j in range(4):
                dots=" ."*j
                self.test(bodyText=f"Testing{dots}")
                time.sleep(per)
        self.test(bodyText="Testing")

    def on(self):
        self.backlit=True
        GPIO.output(self.bl, GPIO.HIGH)

    def off(self):
        self.backlit=False
        GPIO.output(self.bl, GPIO.LOW)

    def image(self, image:Image=None, path:str|Path=None, fit:bool=True):
        pass
