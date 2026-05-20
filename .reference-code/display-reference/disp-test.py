import board
import digitalio
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from adafruit_rgb_display import st7789

# --- Hardware Configuration ---
CS_PIN = board.CE0
DC_PIN = board.D25
RESET_PIN = board.D24
BAUDRATE = 24000000  # Start stable, then increase to 64M later

spi = board.SPI()

# Initialize the display
# For a 240x280 screen in 270 landscape:
# We use the native 240x320 driver and handle the 280-pixel crop via PIL
display = st7789.ST7789(
    spi,
    cs=digitalio.DigitalInOut(CS_PIN),
    dc=digitalio.DigitalInOut(DC_PIN),
    rst=digitalio.DigitalInOut(RESET_PIN),
    baudrate=BAUDRATE,
    width=240,   
    height=320,  # Native chip height
    x_offset=0,
    y_offset=0,
    rotation=90 # This should handle the MADCTL correctly
)

def create_and_show_graphic():
    # In 270 rotation, the display width/height swap.
    # We want to draw on a 280x240 canvas.
    width = 280
    height = 240
    
    # 1. Create PIL Image
    image = Image.new("RGB", (width, height), (0, 20, 40))
    draw = ImageDraw.Draw(image)
    
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
    except OSError:
        font = ImageFont.load_default()

    # Draw a border to see the edges
    draw.rectangle([0, 0, width-1, height-1], outline=(0, 255, 0), width=2)
    draw.text((10, 40), "STABLE LANDSCAPE", font=font, fill=(255, 204, 0))
    draw.text((10, 100), "Complex Graphics", font=font, fill=(255, 255, 255))

    # 2. THE SECRET SAUCE: Correcting the Offset
    # These screens are usually offset by 20 pixels on the Y axis in landscape.
    # We create a 320x240 'buffer' image and paste our 280x240 into it.
    full_buffer = Image.new("RGB", (320, 240), (0, 0, 0))
    # Adjust the '20' here if the image is still shifted
    full_buffer.paste(image, (20, 0)) 

    # 3. Push to display
    # The rgb_display library handles the internal SPI calls correctly
    display.image(full_buffer)

if __name__ == "__main__":
    create_and_show_graphic()