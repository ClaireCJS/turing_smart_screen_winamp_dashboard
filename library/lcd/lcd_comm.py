# turing-smart-screen-python - a Python system monitor and library for USB-C displays like Turing Smart Screen or XuanFang
# https://github.com/mathoudebine/turing-smart-screen-python/

# Copyright (C) 2021-2023  Matthieu Houdebine (mathoudebine)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import copy
import math
import os
import queue
import sys
import threading
import time
from abc import ABC, abstractmethod
from enum import IntEnum
from typing import Tuple, List
import serial
#rom PIL import Image, ImageDraw, ImageFont
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
from library.log import logger


class Orientation(IntEnum):
    PORTRAIT = 0
    LANDSCAPE = 2
    REVERSE_PORTRAIT = 1
    REVERSE_LANDSCAPE = 3
    #last_image



class LcdComm(ABC):
    def __init__(self, com_port: str = "AUTO", display_width: int = 320, display_height: int = 480,
                 update_queue: queue.Queue = None):
        self.lcd_serial = None

        # String containing absolute path to serial port e.g. "COM3", "/dev/ttyACM1" or "AUTO" for auto-discovery
        self.com_port = com_port

        # Display always start in portrait orientation by default
        self.orientation = Orientation.PORTRAIT
        # Display width in default orientation (portrait)
        self.display_width = display_width
        # Display height in default orientation (portrait)
        self.display_height = display_height

        # Queue containing the serial requests to send to the screen. An external thread should run to process requests
        # on the queue. If you want serial requests to be done in sequence, set it to None
        self.update_queue = update_queue

        # Mutex to protect the queue in case a thread want to add multiple requests (e.g. image data) that should not be
        # mixed with other requests in-between
        self.update_queue_mutex = threading.Lock()

        # Create a cache to store opened images, to avoid opening and loading from the filesystem every time
        self.image_cache = {}  # { key=path, value=PIL.Image }

        # Create a cache to store opened fonts, to avoid opening and loading from the filesystem every time
        self.font_cache = {}  # { key=(font, size), value=PIL.ImageFont }

        self.last_image   = None
        self.last_message = None

    def get_orientation() -> Orientation:
        return self.Orientation

    def get_last_image(self) -> Image:
        return self.last_image

    def get_width(self) -> int:
        if self.orientation == Orientation.PORTRAIT or self.orientation == Orientation.REVERSE_PORTRAIT:
            return self.display_width
        else:
            return self.display_height

    def get_height(self) -> int:
        if self.orientation == Orientation.PORTRAIT or self.orientation == Orientation.REVERSE_PORTRAIT:
            return self.display_height
        else:
            return self.display_width

    def openSerial(self, no_exit=True, sleep_time=5):
        if self.com_port == 'AUTO':
            self.com_port = self.auto_detect_com_port()
            if not self.com_port:

                logger.error("Cannot find COM port automatically, please run Configuration again and select COM port manually.")
                if no_exit:
                    logger.error(f"Sleeping {sleep_time} seconds and trying again.")
                    time.sleep(sleep_time)
                else:
                    try:
                        sys.exit(0)
                    except:
                        os._exit(0)
            else:
                logger.debug(f"Auto detected COM port: {self.com_port}")
        else:
            logger.debug(f"Static COM port: {self.com_port}")

        try:
            #elf.lcd_serial = serial.Serial(self.com_port,   9600, timeout=1, rtscts=1)#maybe this will push it a bit less ... or maybe it will restrict it even more, ugh
            self.lcd_serial = serial.Serial(self.com_port, 115200, timeout=1, rtscts=1)
            #maybe try this one next: self.lcd_serial = serial.Serial(self.com_port,  57600, timeout=1, rtscts=1)#maybe this will push it a bit less ... or maybe it will restrict it even more, ugh
        except Exception as e:
            logger.error(f"* Cannot open COM port {self.com_port}: {e}")
            if no_exit:
                pass
            else:
                try:
                    sys.exit(0)
                except:
                    os._exit(0)

    def closeSerial(self):
        try:
            self.lcd_serial.close()
        except:
            pass

    def WriteData(self, byteBuffer: bytearray):
        self.WriteLine(bytes(byteBuffer))

    def SendLine(self, line: bytes):
        if self.update_queue:
            # Queue the request. Mutex is locked by caller to queue multiple lines
            self.update_queue.put((self.WriteLine, [line]))
        else:
            # If no queue for async requests: do request now
            self.WriteLine(line)

    def WriteLine(self, line: bytes, retry_infinitely=True):
        try:
            self.lcd_serial.write(line)
        except serial.serialutil.SerialTimeoutException:
            # We timed-out trying to write to our device, slow things down.
            logger.warning("(Write line) Too fast! Slow down! [serialTimeoutException]")
            try:
                self.closeSerial()
            except serial.serialutil.PortNotOpenError as p:
                print(p)
            except Exception as e:
                print(e)

            try:
                self.Reset(sleep_time=1)       # Reset screen in case it was in an unstable state (screen is also cleared) - this is the slowest part of startup
            except Exception as e:
                print(e)

            while True:
                try:
                    time.sleep(1)
                    self.openSerial()
                    break
                except Exception as e:
                    print(e)

        except (serial.serialutil.SerialException, serial.serialutil.PortNotOpenError) as ee:
            # Error writing data to device: close and reopen serial port, try to write again
            if retry_infinitely:
                logger.error("SerialException or PortNotOpenError: Failed to send serial data to device. Infinitely retrying.")
                self.closeSerial()
                time.sleep(3)
                try:
                    self.openSerial()
                    self.lcd_serial.write(line)
                except Exception as e:
                    print(f"Resetting due to exception: {e}")
                    try:
                        self.reset()
                        time.sleep(4)
                    except Exception as e:
                        print(e)
            else:
                logger.error("SerialException/PortNotOpenError: Failed to send serial data to device. Closing and reopening COM port before retrying once.")
                self.closeSerial()
                time.sleep(1)
                self.openSerial()
                self.lcd_serial.write(line)

    def ReadData(self, readSize: int):
        try:
            response = self.lcd_serial.read(readSize)
            # logger.debug("Received: [{}]".format(str(response, 'utf-8')))
            return response
        except serial.serialutil.SerialTimeoutException:
            # We timed-out trying to read from our device, slow things down.
            logger.warning("(Read data) Too fast! Slow down!")
        except serial.serialutil.SerialException:
            # Error writing data to device: close and reopen serial port, try to read again
            logger.error(
                "SerialException: Failed to read serial data from device. Closing and reopening COM port before retrying once.")
            self.closeSerial()
            time.sleep(1)
            self.openSerial()
            return self.lcd_serial.read(readSize)

    @staticmethod
    @abstractmethod
    def auto_detect_com_port():
        pass

    @abstractmethod
    def InitializeComm(self):
        pass

    @abstractmethod
    def Reset(self):
        pass

    @abstractmethod
    def Clear(self):
        pass

    @abstractmethod
    def ScreenOff(self):
        pass

    @abstractmethod
    def ScreenOn(self):
        pass

    @abstractmethod
    def SetBrightness(self, level: int):
        pass

    def SetBackplateLedColor(self, led_color: Tuple[int, int, int] = (255, 255, 255)):
        pass

    @abstractmethod
    def SetOrientation(self, orientation: Orientation):
        pass

    @abstractmethod
    def DisplayPILImage(
            self,
            image: Image,
            x: int = 0, y: int = 0,
            image_width: int = 0,
            image_height: int = 0
    ):
        pass

    def DisplayBitmap(self, bitmap_path: str, x: int = 0, y: int = 0, width: int = 0, height: int = 0, use_cache=True):
        logger.debug(f"\tDisplayBitmap({bitmap_path},{x},{y},{width},{height},use_cache={use_cache})")
        image = self.open_image(bitmap_path, use_cache=use_cache)
        logger.debug(f"\t\tBitmap opened")
        if image == self.last_image and use_cache:
            logger.debug(f"\t\tNot displaying this image since it's the same as self.last_image:\n\timage={image}\n\tself.last_image={self.last_image}")
        else:
            logger.debug(f"\t\tDisplayPILImage(image, {x}, {y}, {width}, {height});")
            self.last_image = image
            try:
                self.DisplayPILImage(image, x, y, width, height)
            except Exception as e:
                print(f"\t\tException for this image. Moving on. Exception={e} [X1!]")
                return None


    def load_font(self, font_path, font_size):
        key = (font_path, font_size)
        if key not in self.font_cache:
            try:
                # Load the font and cache it
                self.font_cache[key] = ImageFont.truetype("./res/fonts/" + font_path)
            except Exception as e:
                print(f"Failed to load font with key of {key}: {e}")
                raise

    def get_font(self, font_path, font_size):
        key = (font_path, font_size)
        if key not in self.font_cache:
            # Font not in cache, load it
            self.load_font(font_path, font_size)
        return self.font_cache[key]


    def DisplayTextOriginal(
            self,
            text: str,
            x: int = 0,
            y: int = 0,
            width: int = 0,
            height: int = 0,
            font: str = "roboto-mono/RobotoMono-Regular.ttf",
            font_size: int = 20,
            font_color: Tuple[int, int, int] = (0, 0, 0),
            background_color: Tuple[int, int, int] = (255, 255, 255),
            background_image: str = None,
            align: str = 'left',
            anchor: str = None,
    ):
        # Convert text to bitmap using PIL and display it
        # Provide the background image path to display text with transparent background
        # modded in 2024/08/24 to work when anchor = None, not sure why that was throwing errors

        if isinstance(font_color, str):
            font_color = tuple(map(int, font_color.split(', ')))

        if isinstance(background_color, str):
            background_color = tuple(map(int, background_color.split(', ')))

        assert x <= self.get_width(), 'Text X coordinate ' + str(x) + ' must be <= display width ' + str(
            self.get_width())
        assert y <= self.get_height(), 'Text Y coordinate ' + str(y) + ' must be <= display height ' + str(
            self.get_height())
        assert len(text) > 0, 'Text must not be empty'
        assert font_size > 0, "Font size must be > 0"

        if background_image is None:
            # A text bitmap is created with max width/height by default : text with solid background
            text_image = Image.new(
                'RGB',
                (self.get_width(), self.get_height()),
                background_color
            )
        else:
            # The text bitmap is created from provided background image : text with transparent background
            text_image = self.open_image(background_image)

        #current_directory = os.path.abspath(".")
        #print(current_directory)

        # Get text bounding box
        if (font, font_size) not in self.font_cache:
            self.font_cache[(font, font_size)] = ImageFont.truetype("./res/fonts/" + font, font_size)
        font = self.font_cache[(font, font_size)]
        d = ImageDraw.Draw(text_image)

        if width == 0 or height == 0:
            left, top, right, bottom = d.textbbox((x, y), text, font=font, align=align, anchor=anchor)

            # textbbox may return float values, which is not good for the bitmap operations below.
            # Let's extend the bounding box to the next whole pixel in all directions
            left, top = math.floor(left), math.floor(top)
            right, bottom = math.ceil(right), math.ceil(bottom)
        else:
            left, top, right, bottom = x, y, x + width, y + height

            if anchor and anchor.startswith("m"):
                x = (right + left) / 2
            elif anchor and anchor.startswith("r"):
                x = right
            else:
                x = left

            if anchor and anchor.endswith("m"):
                y = (bottom + top) / 2
            elif anchor and anchor.endswith("b"):
                y = bottom
            else:
                y = top

        # Draw text onto the background image with specified color & font
        d.text((x, y), text, font=font, fill=font_color, align=align, anchor=anchor)

        # Restrict the dimensions if they overflow the display size
        left = max(left, 0)
        top = max(top, 0)
        right = min(right, self.get_width())
        bottom = min(bottom, self.get_height())

        # Crop text bitmap to keep only the text
        #text_image = text_image.crop(box=(left, top, right, bottom))

        self.DisplayPILImage(text_image, left, top)


    def DisplayText(
            self,
            text:              str,
            x:                 int  = 0,
            y:                 int  = 0,
            width:             int  = 0,
            height:            int  = 0,
            font:              str  = "roboto-mono/RobotoMono-Regular.ttf",
            font_path:         str  = "",           #this is what the above font field should have been called
            font_size:         int  = 20,
            font_color:        Tuple[int, int, int] = (  0,   0,   0),
            background_color:  Tuple[int, int, int] = None,
            background_image:  str  =  None,
            bg_image_align:    str  =  None,
            align:             str  = 'left',
            anchor:            str  =  None,
            #—————————————————————————————— new stuff:
            use_cache:         bool =  True,
            use_resizing:      bool = False,
            use_colorshift:    bool = False,
            colorshift:        Tuple[int, int, int] = (0, 0, 0),
            darken_background: bool = False,
            darken_factor:     float= 0.3,
            transparent:       bool = False,
            transparency:      int  = 255,
    ):
        #:param anchor:  The text anchor alignment. Determines the relative location of
        #                the anchor to the text. The default alignment is top left,
        #                specifically ``la`` for horizontal text and ``lt`` for
        #                vertical text. See :ref:`text-anchors` for details.
        #  Horizontal Text:
        #        'la' (Left Align): Anchors text at the left side.
        #        'ra' (Right Align): Anchors text at the right side.
        #        'ca' (Center Align): Anchors text at the center horizontally.
        #  Vertical Text:
        #        'lt' (Top Left): Anchors text at the top-left corner.
        #        'ct' (Center Top): Anchors text at the center of the top edge.
        #        'rt' (Top Right): Anchors text at the top-right corner.
        #        'lb' (Bottom Left): Anchors text at the bottom-left corner.
        #        'cb' (Center Bottom): Anchors text at the center of the bottom edge.
        #        'rb' (Bottom Right): Anchors text at the bottom-right corner.
        #        'mc' (Middle Center): Anchors text at the center of the bounding box.
        logger.debug(f"✏ DisplayText called(text={text},x={x},y={y},width={width},height={height},font={font},font_path={font_path},font_size={font_size},font_color={font_color},background_color={background_color},background_image={background_image},align={align},anchor={anchor},use_cache={use_cache},use_resizing={use_resizing},use_colorshift={use_colorshift},colorshift={colorshift},darken_background={darken_background},darken_factor     ={darken_factor     }")

        #font is  really font_path. So if we are passed font, and no font_path
        #it's really the font path, and we need to copy font_path into font:
        if isinstance(font,                    str):
            if font_path=="" and font!="": font_path=font

        #again, font is really a font path, so if it's an actual font, that's wrong;
        if isinstance(font, ImageFont.FreeTypeFont): raise ValueError("Expected 'font' to be a string representing the font file path, got a FreeTypeFont object instead.")

        #now that we have a valid font path, we can retrieve the atual font, and make sure that's what it is
        font = self.get_font(font_path,  font_size)
        if isinstance(font,                    str): raise ValueError("Expected 'font' to be a FreeTypeFont object, got a string representing the font file path instead.")

        #we also need to double check colors are proper tuples
        if isinstance(      font_color,        str):       font_color = tuple(map(int,       font_color.split(', ')))
        if isinstance(background_color,        str): background_color = tuple(map(int, background_color.split(', ')))

        assert x <= self.get_width (), 'Text X coordinate ' + str(x) + ' must be <= display width '  + str(self.get_width ())
        assert y <= self.get_height(), 'Text Y coordinate ' + str(y) + ' must be <= display height ' + str(self.get_height())
        assert len(text) > 0,          'Text must not be empty'
        assert font_size > 0,          "Font size must be > 0"

        # determine height/width stuff, using display_maximum if nothing is passed
        use_width,      use_height = self.get_width(), self.get_height()
        if width  != 0: use_width  = width ;
        if height != 0: use_height = height;


        # —————————————————————————————— background image (or lack thereof) ———————————————————————————————————————
        if background_image is None or background_image == "":                        #background_image is a string path not an Image
            # A text bitmap is created with max width/height by default : text with solid background
            #ext_image = Image.new('RGB' ,(use_width,use_height),background_color)
            text_image = Image.new('RGBA',(int(use_width),int(use_height)),background_color)
            logger.debug(f"✏DisplayText: text_image = Image.new('RGBA',(int(use_width={use_width}),int(use_height={use_height})),background_color={background_color})")
        else:
            # The text bitmap is created from provided background image : text with transparent background
            text_image = self.open_image(background_image, use_cache=False)

        # Get text bounding box
        if (font, font_size) not in self.font_cache:
            self.font_cache[(font_path, font_size)] = ImageFont.truetype("./res/fonts/" + font_path, font_size)
        font = self.font_cache[(font_path, font_size)]

        d = ImageDraw.Draw(text_image)
        logger.debug(f" pre-height-calculation: width={width}, height={height}, self.font_cache={len(self.font_cache)}")
        if width == 0 or height == 0:
            left, top, right, bottom = d.textbbox((x, y), text, font=font, align=align, anchor=anchor)
            left, top, right, bottom = int(left), int(top), int(right), int(bottom)
            logger.debug(f" mid-height-calculation: left={left},top={top},right={right},bottom={bottom}")
            width  = right  - left
            height = bottom - top
        logger.debug(f"post-height-calculation: width={width}, height={height}, self.font_cache={len(self.font_cache)}")

        # —————————————————————————————— resize image to fit our area ———————————————————————————————————————
        original_size_background = text_image
        if use_resizing:
            logger.debug(f"BG01:         text_image: width={width}, height={height})")
            resized_background = resize_with_aspect_ratio(text_image, width, height, bg_image_align=bg_image_align)
            logger.debug(f"BG02: resized_background: width={width}, height={height})")
            if resized_background.mode != 'RGBA': resized_background = resized_background.convert('RGBA')
            logger.debug(f"DDDDDDDrawing: WWWW: resized_background dimension is {resized_background.size[0]}x{resized_background.size[1]}")
            next_background = resized_background
        else:
            next_background = original_size_background

        # —————————————————————————————— optionally darken image for readibility ————————————————————————————
        if not darken_background:
            pass                                                                    #next_background is already correctly set
        else:
            background_predarkened = resized_background
            enhancer = ImageEnhance.Brightness(resized_background)
            darkened_background = enhancer.enhance(darken_factor)
            if resized_background.mode != 'RGBA': resized_background = resized_background.convert('RGBA')
            next_background = darkened_background

        # —————————————————————————————— optionally shift colors for readibility ————————————————————————————
        # shift green away to make our green text more legible
        if not use_colorshift:
            pass                                                                    #next_background is already correctly set
        else:
            colorshifted_background = next_background
            r_shift, g_shift, b_shift = colorshift
            pixels =               next_background.load()
            for pix_y     in range(next_background.height):
                for pix_x in range(next_background.width ):
                    r, g, b, a = pixels[pix_x, pix_y]

                    # colorshift color channels
                    r = min(r + r_shift, 255)     # Ensure the value doesn't    exceed   255
                    r = max(r          ,   0)     # Ensure the value doesn't be less than  0
                    g = min(g + g_shift, 255)     # Ensure the value doesn't    exceed   255
                    g = max(g          ,   0)     # Ensure the value doesn't be less than  0
                    b = min(b + b_shift, 255)     # Ensure the value doesn't    exceed   255
                    b = max(g          ,   0)     # Ensure the value doesn't be less than  0

                    # Set the modified pixel back
                    pixels[pix_x, pix_y] = (r, g, b, a)
            next_background = colorshifted_background


        # —————————————————————————————— done with background layer, save it: ————————————————————————————
        final_background = next_background


        # —————————————————————————————— Now create a separate image for the text layer ———————————————————————————————————————
        alpha = transparency if transparent else 0
        if background_color: background_color_with_alpha = background_color + (alpha,)
        else:                background_color_with_alpha = (0,    0,    0)  + (    0,)           #might want 4th tuple to be 255 to make it default to transparent instead of black, except that makes placing new elements harder because you can't see the border if they are transparent
        #ext_layer_image = Image.new('RGBA', (    width,     height), (0, 0, 0, 0))
        #ext_layer_image = Image.new('RGBA', (use_width, use_height), (0, 0, 0, 0))
        text_layer_image = Image.new('RGBA', (use_width, use_height), background_color_with_alpha)

        # Now draw the text onto the current image
        if (font_path, font_size) not in self.font_cache:
            self.font_cache[(font_path, font_size)] = ImageFont.truetype("./res/fonts/" + font_path, font_size)

        # Create a drawing context on the text layer
        d = ImageDraw.Draw(text_layer_image)

        # Calculate the text bounding box
        logger.debug(f"DDDDDDDrawing: AAAA: width={width}, height={height}, x={x}, y={y}, anchor={anchor}")
        if width == 0 or height == 0:
            left , top, right, bottom = d.textbbox((x, y), text, font=font, align=align, anchor=anchor)
            left , top                = math.floor(left), math.floor(top)
            right, bottom             = math.ceil(right), math.ceil(bottom)
        else:
            left, top, right, bottom = x, y, x + width, y + height
            logger.debug(f"Text Layer: left={left}, top={top}, right={right}, bottom={bottom} = x={x}, y={y}, x + width={x + width}, y + height={y + height}")

            if   anchor and anchor.startswith("m"): x = (right + left) / 2
            elif anchor and anchor.startswith("r"): x = right
            else: x = left
            if   anchor and anchor.endswith("m"): y = (bottom + top) / 2
            elif anchor and anchor.endswith("b"): y = bottom
            else: y = top
        logger.debug(f"DDDDDDDrawing: BBBB: width={width}, height={height}, x={x}, y={y}, top={top}, bottom={bottom}, left={left}, right={right}, anchor={anchor}")
        logger.debug(f"DDDDDDDrawing: BBBB: top={top}, background_image={background_image}")
        logger.debug(f"DDDDDDDrawing  TEXT ———> '{text}' at ({x}, ***{y}***), font={font}, fill={font_color}, align={align}, anchor={anchor}")
        #d.text((x,y), text, font=font, fill=font_color, align=align, anchor=anchor)
        d .text((x,0), text, font=font, fill=font_color, align=align, anchor=anchor) #y is actually 0 because the text is going at y=0 *of itself*, not the same as screen-y



        # ———————————————— Combine our text and image layers into one picture: Now we've created transparency! ————————————————
        if text_layer_image.mode     != 'RGBA': text_layer_image = text_layer_image.convert('RGBA')
        if background_image:
            if final_background.mode != 'RGBA': final_background = final_background.convert('RGBA')
            logger.debug(f"DDDDDDDrawing: ABOUT TO COMBINE! dim(final_background)={final_background.size[0]}x{final_background.size[1]}, dim(text_layer_image)={text_layer_image.size[0]}x{text_layer_image.size[1]}")
            if  final_background.size[0] > text_layer_image.size[0] or final_background.size[1] > text_layer_image.size[1]:
                final_background = final_background.crop(box=(0,0,text_layer_image.size[0],text_layer_image.size[1]))
                # Ensure sizes are the same - very experimental 🐐
                if final_background.size[0] != text_layer_image.size[0] or final_background.size[1] != text_layer_image.size[1]:
                    final_background = final_background.resize(text_layer_image.size, Image.ANTIALIAS)
            combined_image = Image.alpha_composite(final_background, text_layer_image)
            final_image = combined_image
        else:
            final_image = text_layer_image

        #DEBUG SITUATIONS:
        #final_image = final_background       #JUST RIGHT!
        #final_image = text_layer_image       #JUST RIGHT!

        logger.debug(f"DDDDDDDrawing: YYYY: final_image dimension is {final_image.size[0]}x{final_image.size[1]}")
        logger.debug(f"DDDDDDDrawing: RES0:  pre-restriction-calc values: left={left},top={top},right={right},bottom={bottom}")


        # —————————————————————————————— final crop to ensure we' still in our correct confines ————————————————————————————————
        # Restrict the dimensions if they overflow the display size
        left   = max(left  , 0)
        top    = max(top   , 0)
        right  = min(right , self.get_width())
        bottom = min(bottom, self.get_height())
        logger.debug(f"DDDDDDDrawing: RES9: POST-restriction-calc values: left={left},top={top},right={right},bottom={bottom}")
        try:
            restricted_final_image = final_image.crop(box=(left, top, right, bottom))
            logger.debug(f"DDDDDDDrawing: YYYZ: restricted img dims are: {restricted_final_image.size[0]}x{restricted_final_image.size[1]}")
        except Exception as e:
            print(f"some kinda exception with generating restricted_final_image:\n{e}")
            import traceback
            traceback.print_exc()


        # —————————————————————————————— finally, draw the image! ————————————————————————————————
        logger.debug(f"DDDDDDDrawing: ZZZZ: self.DisplayPILImage(left={left}, top={top}, final_image={final_image} .... top={top}, bottom={bottom}, left={left}, right={right}, anchor={anchor})")

        self.DisplayPILImage(final_image, left, top)
        #self.DisplayPILImage(restricted_final_image, left, top)

        return final_image






    def DisplayProgressBar(self, x: int, y: int, width: int, height: int, min_value: int = 0, max_value: int = 100,
                           value             : int  = 50,
                           bar_outline       : bool = True,
                           bar_color         : Tuple[int, int, int] = (0, 0, 0),
                           bar_outline_color : Tuple[int, int, int] = (255, 255, 255),
                           background_color  : Tuple[int, int, int] = (255, 255, 255),
                           background_image  : str = None):
        # Generate a progress bar and display it
        # Provide the background image path to display progress bar with transparent background

        if isinstance(        bar_color, str):         bar_color = tuple(map(int,         bar_color.split(', ')))
        if isinstance( background_color, str):  background_color = tuple(map(int,  background_color.split(', ')))
        if isinstance(bar_outline_color, str): bar_outline_color = tuple(map(int, bar_outline_color.split(', ')))
        if bar_outline_color is None:          bar_outline_color = background+color

        #print(f"background  color is {background_color}")
        #print(f"bar         color is {bar_color}")
        #print(f"bar outline color is {bar_outline_color}")

        assert x          <= self.get_width (),  'Progress bar X coordinate must be <= display width '
        assert y          <= self.get_height(),  'Progress bar Y coordinate must be <= display height'
        assert x + width  <= self.get_width (), f'Progress bar width of {width} exceeds display width of {self.get_width()}'
        assert y + height <= self.get_height(),  'Progress bar height exceeds display height'

        # Don't let the set value exceed our min or max value, this is bad :)
        if       value < min_value: value = min_value
        elif max_value <     value: value = max_value
        assert min_value <= value <= max_value, 'Progress bar value shall be between min and max'

        if background_image is None:
            bar_image = Image.new('RGB', (width, height), background_color)          # A bitmap is created with solid background
        else:
            bar_image = self.open_image(background_image)                            # A bitmap is created from provided background image
            bar_image = bar_image.crop(box=(x, y, x + width, y + height))            # Crop bitmap to keep only the progress bar background

        # Draw progress bar
        bar_filled_width = (value / (max_value - min_value) * width) - 1
        if bar_filled_width < 0: bar_filled_width = 0
        draw = ImageDraw.Draw(bar_image)
        #raw.rectangle([0, 0, bar_filled_width, height - 1], fill=bar_color, outline=bar_color)
        draw.rectangle([0, 0, bar_filled_width, height - 1], fill=bar_color, outline=bar_outline_color)
        if bar_outline:
            draw.rectangle([0, 0, width - 1, height - 1], fill=None, outline=bar_outline_color)

        self.DisplayPILImage(bar_image, x, y)

    def DisplayLineGraph(self, x: int, y: int, width: int, height: int,
                         values: List[float],
                         min_value: int = 0,
                         max_value: int = 100,
                         autoscale: bool = False,
                         line_color: Tuple[int, int, int] = (0, 0, 0),
                         line_width: int = 2,
                         graph_axis: bool = True,
                         axis_color: Tuple[int, int, int] = (0, 0, 0),
                         background_color: Tuple[int, int, int] = (255, 255, 255),
                         background_image: str = None):
        # Generate a plot graph and display it
        # Provide the background image path to display plot graph with transparent background

        if isinstance(line_color      , str):       line_color = tuple(map(int,       line_color.split(', ')))
        if isinstance(axis_color      , str):       axis_color = tuple(map(int,       axis_color.split(', ')))
        if isinstance(background_color, str): background_color = tuple(map(int, background_color.split(', ')))

        assert x <= self.get_width(), 'Progress bar X coordinate must be <= display width'
        assert y <= self.get_height(), 'Progress bar Y coordinate must be <= display height'
        assert x + width <= self.get_width(), 'Progress bar width exceeds display width'
        assert y + height <= self.get_height(), 'Progress bar height exceeds display height'

        if background_image is None:
            # A bitmap is created with solid background
            graph_image = Image.new('RGB', (width, height), background_color)
        else:
            # A bitmap is created from provided background image
            graph_image = self.open_image(background_image)

            # Crop bitmap to keep only the plot graph background
            graph_image = graph_image.crop(box=(x, y, x + width, y + height))

        # if autoscale is enabled, define new min/max value to "zoom" the graph
        if autoscale:
            trueMin = max_value
            trueMax = min_value
            for value in values:
                if not math.isnan(value):
                    if trueMin > value:
                        trueMin = value
                    if trueMax < value:
                        trueMax = value

            if trueMin != max_value and trueMax != min_value:
                min_value = max(trueMin - 5, min_value)
                max_value = min(trueMax + 5, max_value)

        step = width / len(values)
        # pre compute yScale multiplier value
        yScale = height / (max_value - min_value)

        plotsX = []
        plotsY = []
        count = 0
        for value in values:
            if not math.isnan(value):
                # Don't let the set value exceed our min or max value, this is bad :)
                if value < min_value:
                    value = min_value
                elif max_value < value:
                    value = max_value

                assert min_value <= value <= max_value, 'Plot point value shall be between min and max'

                plotsX.append(count * step)
                plotsY.append(height - (value - min_value) * yScale)

                count += 1

        # Draw plot graph
        draw = ImageDraw.Draw(graph_image)
        draw.line(list(zip(plotsX, plotsY)), fill=line_color, width=line_width)

        if graph_axis:
            # Draw axis
            draw.line([0, height - 1, width - 1, height - 1], fill=axis_color)
            draw.line([0, 0, 0, height - 1], fill=axis_color)

            # Draw Legend
            draw.line([0, 0, 1, 0], fill=axis_color)
            text = f"{int(max_value)}"
            font = ImageFont.truetype("./res/fonts/" + "roboto/Roboto-Black.ttf", 10)
            left, top, right, bottom = font.getbbox(text)
            draw.text((2, 0 - top), text,
                      font=font, fill=axis_color)

            text = f"{int(min_value)}"
            font = ImageFont.truetype("./res/fonts/" + "roboto/Roboto-Black.ttf", 10)
            left, top, right, bottom = font.getbbox(text)
            draw.text((width - 1 - right, height - 2 - bottom), text,
                      font=font, fill=axis_color)

        self.DisplayPILImage(graph_image, x, y)

    def DisplayRadialProgressBar(self, xc: int, yc: int, radius: int, bar_width: int,
                                 min_value: int = 0,
                                 max_value: int = 100,
                                 angle_start: int = 0,
                                 angle_end: int = 360,
                                 angle_sep: int = 5,
                                 angle_steps: int = 10,
                                 clockwise: bool = True,
                                 value: int = 50,
                                 text: str = None,
                                 with_text: bool = True,
                                 font: str = "roboto/Roboto-Black.ttf",
                                 font_size: int = 20,
                                 font_color: Tuple[int, int, int] = (0, 0, 0),
                                 bar_color: Tuple[int, int, int] = (0, 0, 0),
                                 background_color: Tuple[int, int, int] = (255, 255, 255),
                                 background_image: str = None):
        # Generate a radial progress bar and display it
        # Provide the background image path to display progress bar with transparent background

        if isinstance(bar_color, str):
            bar_color = tuple(map(int, bar_color.split(', ')))

        if isinstance(background_color, str):
            background_color = tuple(map(int, background_color.split(', ')))

        if isinstance(font_color, str):
            font_color = tuple(map(int, font_color.split(', ')))

        if angle_start % 361 == angle_end % 361:
            if clockwise:
                angle_start += 0.1
            else:
                angle_end += 0.1

        assert xc - radius >= 0 and xc + radius <= self.get_width(), 'Progress bar width exceeds display width'
        assert yc - radius >= 0 and yc + radius <= self.get_height(), 'Progress bar height exceeds display height'
        assert 0 < bar_width <= radius, f'Progress bar linewidth is {bar_width}, must be > 0 and <= radius'
        assert angle_end % 361 != angle_start % 361, f'Invalid angles values, start = {angle_start}, end = {angle_end}'
        assert isinstance(angle_steps, int), 'angle_steps value must be an integer'
        assert angle_sep >= 0, 'Provide an angle_sep value >= 0'
        assert angle_steps > 0, 'Provide an angle_step value > 0'
        assert angle_sep * angle_steps < 360, 'Given angle_sep and angle_steps values are not correctly set'

        # Don't let the set value exceed our min or max value, this is bad :)
        if value < min_value:
            value = min_value
        elif max_value < value:
            value = max_value

        assert min_value <= value <= max_value, 'Progress bar value shall be between min and max'

        diameter = 2 * radius
        bbox = (xc - radius, yc - radius, xc + radius, yc + radius)
        #
        if background_image is None:
            # A bitmap is created with solid background
            bar_image = Image.new('RGB', (diameter, diameter), background_color)
        else:
            # A bitmap is created from provided background image
            bar_image = self.open_image(background_image)

            # Crop bitmap to keep only the progress bar background
            bar_image = bar_image.crop(box=bbox)

        # Draw progress bar
        pct = (value - min_value) / (max_value - min_value)
        draw = ImageDraw.Draw(bar_image)

        # PIL arc method uses angles with
        #  . 3 o'clock for 0
        #  . clockwise from angle start to angle end
        angle_start %= 361
        angle_end %= 361
        #
        if clockwise:
            if angle_end < angle_start:
                ecart = 360 - angle_start + angle_end
            else:
                ecart = angle_end - angle_start
            #
            # solid bar case
            if angle_sep == 0:
                if angle_end < angle_start:
                    angleE = angle_start + pct * ecart
                    angleS = angle_start
                else:
                    angleS = angle_start
                    angleE = angle_start + pct * ecart
                draw.arc([0, 0, diameter - 1, diameter - 1], angleS, angleE,
                         fill=bar_color, width=bar_width)
            # discontinued bar case
            else:
                angleE = angle_start + pct * ecart
                angle_complet = ecart / angle_steps
                etapes = int((angleE - angle_start) / angle_complet)
                for i in range(etapes):
                    draw.arc([0, 0, diameter - 1, diameter - 1],
                             angle_start + i * angle_complet,
                             angle_start + (i + 1) * angle_complet - angle_sep,
                             fill=bar_color,
                             width=bar_width)

                draw.arc([0, 0, diameter - 1, diameter - 1],
                         angle_start + etapes * angle_complet,
                         angleE,
                         fill=bar_color,
                         width=bar_width)
        else:
            if angle_end < angle_start:
                ecart = angle_start - angle_end
            else:
                ecart = 360 - angle_end + angle_start
            # solid bar case
            if angle_sep == 0:
                if angle_end < angle_start:
                    angleE = angle_start
                    angleS = angle_start - pct * ecart
                else:
                    angleS = angle_start - pct * ecart
                    angleE = angle_start
                draw.arc([0, 0, diameter - 1, diameter - 1], angleS, angleE,
                         fill=bar_color, width=bar_width)
            # discontinued bar case
            else:
                angleS = angle_start - pct * ecart
                angle_complet = ecart / angle_steps
                etapes = int((angle_start - angleS) / angle_complet)
                for i in range(etapes):
                    draw.arc([0, 0, diameter - 1, diameter - 1],
                             angle_start - (i + 1) * angle_complet + angle_sep,
                             angle_start - i * angle_complet,
                             fill=bar_color,
                             width=bar_width)

                draw.arc([0, 0, diameter - 1, diameter - 1],
                         angleS,
                         angle_start - etapes * angle_complet,
                         fill=bar_color,
                         width=bar_width)

        # Draw text
        if with_text:
            if text is None:
                text = f"{int(pct * 100 + .5)}%"
            font = ImageFont.truetype("./res/fonts/" + font, font_size)
            left, top, right, bottom = font.getbbox(text)
            w, h = right - left, bottom - top
            draw.text((radius - w / 2, radius - top - h / 2), text,
                      font=font, fill=font_color)

        self.DisplayPILImage(bar_image, xc - radius, yc - radius)

    # Load image from the filesystem, or get from the cache if it has already been loaded previously
    def open_image(self, bitmap_path: str, use_cache=True) -> Image:
        if use_cache:
            if bitmap_path not in self.image_cache:
                self.image_cache[bitmap_path] = Image.open(bitmap_path)
                logger.debug("Bitmap " + bitmap_path + " is now loaded in the cache")
            return copy.copy(self.image_cache[bitmap_path])
        else:
            return Image.open(bitmap_path)


###################################

def resize_with_aspect_ratio(image, target_width, target_height, bg_image_align=None):
    logger.debug(f"CALL: resize_with_aspect_ratio(image={image}, type_of(image).__name__={type(image).__name__} target_width={target_width}, target_height={target_height}")
    if type(image) == Image: logger.debug(f"TYPE: type_of(image) is, apparently, Image")
    if type(image).__name__ == " PngImageFile": pass
    if type(image).__name__ == "JpegImageFile": pass
    logger.debug(f"TYPE: type_of(image)__name__=={type(image ).__name__}")

    target_width  = int(target_width )
    target_height = int(target_height)

    #if type(image).__name__ != "Image":
    #   msg = "ValueError: Expected 'image' to be type Image [pillow], but it was ***" + type(image).__name__ + "***"
    #    raise ValueError(msg)

    # Get original dimensions
    original_width, original_height = image.size

    # Calculate aspect ratio
    aspect_ratio = original_width / original_height

    # Calculate new dimensions
    if target_width / target_height > aspect_ratio:
        new_width = int(target_height * aspect_ratio)
        new_height = target_height
    else:
        new_width  = target_width
        new_height = target_width // aspect_ratio

    # Resize image with maintained aspect ratio
    logger.debug(f"RESIZE_AR1: resized_image = image.resize((new_width={new_width}, new_height={new_height}), Image.LANCZOS)")
    resized_image = image.resize((new_width, new_height), Image.LANCZOS)
    logger.debug(f"RESIZE_AR2: resized_image = {resized_image.size[0]}x{resized_image.size[1]}")
    logger.debug(f"RESIZE_AR3: target_width={target_width} target_height={target_height}")

    # Create a new image with the target size and paste the resized image onto it
    final_image = Image.new('RGBA', (target_width, target_height), (0, 0, 0, 0))             #800x440
    left = int((target_width  - new_width ) / 2)                                             #800-533/2 > 267/2 = 133.5
    top  = int((target_height - new_height) / 2)                                             #440-440/2 >   0/2 = 0
    logger.debug(f"RESIZE_AR4: final_image.paste(resized_image, (left={left}, top={top})")   #top is 0 when it should be 50
    logger.debug(f"RESIZE_AR5:                —— target_WxH={target_width}x{target_height}") #target WxH  ==800x440
    logger.debug(f"RESIZE_AR6:                ——    new_WxH={   new_width}x{   new_height}") #new(usually)==440x440

    #at this point, left will usually be width of 440, with 220 on each side of center line, so left==220, and top==0 actually not 40
    #🐐for now, we will hard-code
    #to right align, we just need to change left to our displaywidth, minus image width
    if bg_image_align == "right": left = target_width - resized_image.size[0]
    final_image.paste(resized_image, (left, top))
    logger.debug(f"RESIZE_AR7:  final_image = {final_image.size[0]}x{final_image.size[1]}")
    return final_image

#🐐
