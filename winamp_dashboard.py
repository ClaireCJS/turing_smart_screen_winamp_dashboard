#!/usr/bin/env python

# turing-smart-screen-python-winamp-dashboard - a Python dashboard for WinAmp an VLCPlayer users which uses the $13-on-AliExpress 5" USB-C Turing Smart Screen

# please check out the project this was created from: or XuanFang
# https://github.com/mathoudebine/turing-smart-screen-python/

# Copyright (C) 2024   Claire Sawyer (claire_cjs) —— but only updated for LcdCommRevA
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

# Import only the modules for LCD communication
from  library.lcd.lcd_comm_rev_a import LcdCommRevA, Orientation
#from library.lcd.lcd_comm_rev_b import LcdCommRevB
#from library.lcd.lcd_comm_rev_c import LcdCommRevC
#from library.lcd.lcd_comm_rev_d import LcdCommRevD
from  library.lcd.lcd_simulated  import LcdSimulated



################################## CONFIG: START ##################################
################################## CONFIG: START ##################################
################################## CONFIG: START ##################################

####### PC CONFIG: #######
#                        1) absolutely need PIL (```pip install PIL``)
#libraries:              1) absolutely required: claire_winamp.py (shoudl be included)
#                        3) only required if you want bonus VLC support: claire_winamp.py (should be included)
#com ports:              You may need to run configure.py to determine the COM port being used
#                        You can optionally edit config.yaml  and put that COM port into it for theoretical smoother sailing
#environment variables:  set NOW_PLAYING_ALBUM_ART=c:\mp3\now-playing.png —— use whatever file you configure in the NowPlaying WinAmp plugin —— will later be used for the var: now_playing_album_art = os.getenv('NOW_PLAYING_ALBUM_ART')
#                        set NOW_PLAYING_SONG_INFO=c:\mp3\now-playing.png —— use whatever file you configure in the NowPlaying WinAmp plugin —— will later be used for the var: now_playing_song_info = os.getenv('NOW_PLAYING_SONG_INFO')


####### PC / USB CONFIG: #######
# Set your COM port e.g. COM3 for Windows, /dev/ttyACM0 for Linux, etc. or "AUTO" for auto-discovery
# COM_PORT = "/dev/ttyACM0"
# COM_PORT = "COM5"
# COM_PORT = "AUTO"             <----------- this is the one you probably want, but hard-code it for potentially better/faster results!
COM_PORT = "COM4"

####### EXPERIMENTAL CONFIG: #######
vlc_support = True

####### PICTURE FRAME CONFIG: #######
device_is_upside_down = True                      #depending on where your outlet is, you might want to use the device upside down to make the cord come out in the right direction. TODO: fix bug where upside-down becomes rightside-up after power cycles
UsbPCMonitor          = True                      #if you have a model "A" that uses the UsbPCMonitor, it's resolution is actually higher than other model "A"s, so this should be set
suppress_init         = False                     #if you have a model "A" that uses the UsbPCMonitor, you don't need to do the lcd_comm.init()

####### IMAGE MANIPULATION CONFIG: #######
colorshift_cover_art  = False                     #should we shift the color in our cover art? If our text is green, we can shift some of the green out of the background image to make it easier to read
colorshift_rgb_shift  = (0,0,0)                   #(r,g,b) values for colorshift. For example, if using green text, shift (0,0,-40) to lower the amount of green on the underlying image. A dynamic solution that's a function of the text font color would be better.
darken_cover_art      = True                      #should we darken our cover art to make it easier to read the overlaying text?
darken_factor_default = 0.6                       #how much to darken the background to make it easier to read —— really thought 0.5 was good but after cycling thru songs some are too dark so tried .6, .666, .666 was hard to read sometimes but on that same image 0.55 was more darkening than necessary, so trying .6

####### PERFORMANCE THROTTLING CONFIG: #######
throttle_after_drawing_clock        = 2.00        #how long to wait, in seconds, after drawing our clock             \___ testing theory that some device crashes are due to data overload    #.10 -> .25 -> -> .75 -> 1 -> 0.25 -> .75 -> 1 -> 1.25 -> 1.5 -> 2
throttle_after_drawing_media_info   = 2.25        #how long to wait, in seconds, after drawing our media info         \___ testing theory that some device crashes are due to data overload   #.25 -> .33 -> 1.25 -> 1.5 -> 1.75 -> 2.25
throttle_after_drawing_progress_bar = 3.00        #how long to wait, in seconds, after drawing our progress bar       /  #0.15 was de crashing on Alice Cooper — Billion Dollar Babies, and later in the song, so not a cover-art-processing issue. #.25 -> .50 -> 1 -> 2 -> 2.2 -> 2.5 -> 3.0
throttle_after_end_of_loop          = 0.25        #this one mainly comes into play if nothing else is updating, so it doesn't need to be >2s like the others

####### COSMETIC/FONT CONFIG: #######
winamp_info_font_size         =  65
winamp_info_font_color_pause  = (200,200,0)
winamp_info_font_color        = (34,239,34)       #color to display our song info in ... 34/139/34 was yucky despite chatgpt's suggestion... (34,239,34) is more close to the default Winamp color, and a lot of color theory says green is the easiest color to read in this situation
winamp_info_font              = "roboto/Roboto-Bold.ttf"
winamp_info_monospaced_font   =  False            #em-dashes aren't wide enough in monospaced fonts and look too much like hyphens/en-dashes, so we use two if it's a monospaced font, but one of it isn't [because the lack of monospace nature lets them make a correctly-long dash!]
#ackground_image_filename     = f"res/backgrounds/800x480_circuit.png" #‼ might want to use this ‼
background_image_filename     =  None             #the background image will be overwritten by the cover image. If another cover image comes out that is less wide, there will be black space left over. This can be mitigated by re-drawing the background prior to drawing any cover art, but that's a slowdown!  Occasionally cover art is the same aspect ratio as the device, in which case the background would be COMPLETELY overwritten.  Perhaps redrawing it every n times would be better, or redrawing it it's wider than a square image would be at our current resolution
#lock_format                  = "%I:%M:%S"        #\_____remove :%S if you don't want seconds, add " %p" if you want AM/PM but you'd be wasting screen space for something obvious
clock_format                  = "%I:%M"           #/     but keep in mind that you will have to change the width of the element, the cosmetics are currently set up for "%I:%M"
clock_background_color        =  None             #good for testing: (0, 0, 128)
clock_font_size               =  50
clock_font_color              = (255,0,0)
progress_bar_color_pause      = (200,200, 0)      #color for progress bar when winamp is paused
progress_bar_color_stop       = (200,  0, 0)      #color for progress bar when winamp is stopped
progress_bar_color_foreground = (224,24,224)
progress_bar_color_background = ( 55,  0,83)

####### STRINGS CONFIG: #######
winamp_not_found_message = "Cannot connect to\na *Playing* instance WinAmp..."

####### ELEMENT PLACEMENT CONFIG: #######
progress_bar_width       = 800                    #width of song progress bar
progress_bar_height      =  40
clock_x                  =   0                    #x coordinate of clock        #660 # 15 #308 #400
clock_y                  = 425                    #y coordinate of clock        #425 #425      #200
clock_width              = 135                    #200 was good? #100 seemed better but cut left off?!
clock_height             =  52                    #30  was good?
winamp_info_field_width  =  22                    #width of winamp information: 21 characters wide  #21 -> 25? -> 23 ->22
winamp_info_field_height =   6                    #width of winamp information:  4    rows    high  # 4 -> 6?
winamp_info_x            =   0                    #x coordinate of winamp/song info:  0 is where we want it
winamp_info_y            =  40                    #y coordinate of winamp/song info: 40 is where we want it


################################## CONFIG: END ##################################
################################## CONFIG: END ##################################
################################## CONFIG: END ##################################

############## DEBUG: ##############
############## DEBUG: ##############
############## DEBUG: ##############
#isplay_winamp_info  = False       #the laziest way to
display_winamp_info  = True        #change these debug
#isplay_progress_bar = False       #booleans is to just 🐐
display_progress_bar = True        #comment one line
#isplay_clock        = False       #and uncomment the
display_clock        = True        #other line 😂🤣😁

debug_clock_tenacious   = False    #True == makes the clock refresh every loop cycle instead of every minute. If you want to display seconds, you need this
debug_clock_timey_wimey = False    #randomly makes the time longer/shorter (10:23 -> 1:23, 1:23 -> 01:23) for position testing
debug_darkening         = False    #\_____ True == change darkening factor to a non-default value.  We like 2.5.
debug_darkening_factor  = 2.5      #/      Thus, it is a BRIGHTening. Why? To see the edges for position testing
############## DEBUG ###############
############## DEBUG #Q#############
############## DEBUG  ##############


############## CONSTANTS: ##############
orientation_to_use                           = Orientation.LANDSCAPE          #options & values are: Orientation.PORTRAIT=0  Orientation.LANDSCAPE=2  Orientation.REVERSE_PORTRAIT=1  Orientation.REVERSE_LANDSCAPE=3 . But this program only works in landscape
if device_is_upside_down: orientation_to_use = Orientation.REVERSE_LANDSCAPE  #options & values are: Orientation.PORTRAIT=0  Orientation.LANDSCAPE=2  Orientation.REVERSE_PORTRAIT=1  Orientation.REVERSE_LANDSCAPE=3 . But this program only works in landscape




def usage():
    print("""
USAGE: winamp_dashboard {list of options}

            * options can be bare words —— or be preceeded with -, --, /
              (It's set up so you don't have to remember which!)

            * compound words work with hypens or underscores or nothing between them
              (i.e. "no-darken", "nodarken", and "no_darken" will all work)

OPTIONS:
        no-darken - Do not darken the cover art.
                    Good for seeing how the darkening affects appearance.
                    aliases: nd | darken-no | not-dark | darken't | light

        blacken   - Erase the entire screen prior to startup
                    Quite   necessary if code is changed, to do this once
                    Quite unnecessary if code is unchanged
                    aliases: black | black-first | blacken-first | reset | erase | erase-first

        song      - Forces the display of WinAmp's song info, even if code is configured not to
                    Usful for testing
                    aliases: w | s | winamp | song | display-winamp | display_winamp | displaywinamp | force-winamp | force_winamp | forcewinamp

        once      - Update the screen once, then exit
                    Good for quick code testing
                    aliases: quick | q | 1 | fast | quick-run
        """)
    sys.exit(0)





import os
import signal
import sys
import time
from datetime import datetime


############################################## LOGGING: ##############################################
import logging as dashboard_logging
for    handler in dashboard_logging.root.handlers[:]: dashboard_logging.root.removeHandler(handler)
dashboard_logging.basicConfig(level=dashboard_logging.DEBUG,format='\t\t[%(levelname)s] %(message)s')
dashboard_logger                  = dashboard_logging.getLogger(__name__)
dashboard_logger.setLevel          (dashboard_logging.DEBUG)
dashboard_logger.debug            ("dashboard logger started")
############################################## LOGGING ###############################################



############################################## UTILITY FUNCTIONS: ###############################################
try:
    import clairecjs_utils.claire_winamp as cjs_winamp            #if you have clairecjs_utils fully installed, load it this way
    import clairecjs_utils.claire_vlc    as cjs_vlc               #if you have clairecjs_utils fully installed, load it this way
    dashboard_logger.debug(f"🌟 clairecjs_utils 🌟 loaded from repo")
except ImportError:
    try:
        import clairecjs_utils_copy.claire_winamp as cjs_winamp   #but if not, local symlink ensures latest copy is included in this github's project anyway
        import clairecjs_utils_copy.claire_vlc    as cjs_vlc      #but if not, local symlink ensures latest copy is included in this github's project anyway
        dashboard_logger.debug(f"🌟 clairecjs_utils 🌟 loaded from previously-copyed local subfolder")
    except ImportError as e:
        raise ImportError("Neither 'clairecjs_utils' nor 'clairecjs_utils_copy' could be imported.") from e
############################################## UTILITY FUNCTIONS ################################################








# Fetch the values of Winamp's self-reporting from our environment variables:
now_playing_album_art = os.getenv('NOW_PLAYING_ALBUM_ART')
now_playing_song_info = os.getenv('NOW_PLAYING_SONG_INFO')
#print(f"Album Art Path: {now_playing_album_art}")
#print(f"Song Info Path: {now_playing_song_info}")




# Display revision:
# - A      for Turing 3.5" and UsbPCMonitor 3.5"/5" ——— this is what Claire got in 2024 from Amazon for $30 tho Temu sells it for $18
# - B      for Xuanfang 3.5" (inc. flagship)
# - C      for Turing 5"
# - D      for Kipye Qiye Smart Display 3.5"
# - SIMU   for 3.5" simulated LCD (image written in screencap.png)
# - SIMU5  for 5" simulated LCD
# To identify your smart screen: https://github.com/mathoudebine/turing-smart-screen-python/wiki/Hardware-revisions
REVISION = "A"

stop = False




def split_into_columns_OLD_1(input_string, width=13):
    chunks = [input_string[i:i+width] for i in range(0, len(input_string), width)]          # Split the string into chunks of 'width' characters
    padded_chunks = [chunk.ljust(width) for chunk in chunks]                                # Pad each chunk to ensure it's exactly 'width' characters long
    result = "\n".join(padded_chunks)                                                       # Join the chunks with newlines to create the final string
    return result

def split_into_columns_great_V1(input_string, width=13, height=None):
    if height is None: height = (len(input_string) + width - 1) // width                    # default height is calculated if not specified
    total_characters = width * height                                                       # Calculate the total number of characters needed
    sliced_string = input_string[:total_characters]                                         # Slice the string to ensure it fits within the specified width and height
    #hunks = [sliced_string[i:i + width] for i in range(0, len(sliced_string), width)]      # Split the sliced string into chunks of 'width' characters
    chunks = [sliced_string[i:i + width] for i in range(0,   total_characters, width)]      # Split the sliced string into 'width' character chunks
    while len(chunks) < height: chunks.append(' ' * width)                                  # Pad with empty lines if fewer lines were created
    if len(chunks[-1]) < width: chunks[-1] = chunks[-1].ljust(width)                        # Pad the last chunk if it's shorter than 'width', though I believe this is old code and unnecessary
    chunks = [chunk.ljust(width) for chunk in chunks]                                       # Ensure each chunk is exactly 'width' characters long by padding with spaces if necessary
    result = "\n".join(chunks)                                                              # Join the chunks with newlines to create the final string
    return result

def split_into_columns(input_string, width=winamp_info_field_width, height=winamp_info_field_height):
    lines        = []                                                                       # init
    current_line = ""                                                                       # init
    words        = input_string.split()                                                     # Split the input into words
    for word in words:                                                                      # for each word in our input string
        #f len(current_line) + len(word) + 1 <= width:                                      # if the next word fits on the current line (+1 accounts for a space after, but may not be necessary?)
        if len(current_line) + len(word) + 0 <= width:                                      # if the next word fits on the current line (trying without +1,           which may not be necessary?)
            current_line += (word + " ")                                                    # Add word to the current line
        else:                                                                               # otherwise:
            lines.append(current_line.rstrip())                                             # Add current line to the lines array, removing trailing spaces
            current_line  =  word + " "                                                     # Start a new line with the current word
    lines.append(current_line.rstrip())                                                     # Add the final line to the lines array
    if height is None: height = (len(input_string) + width - 1) // width                    # default height is calculated if not specified
    #🐐 lines = ["",lines]                                                                  # prepend "forbidden line" at top which will be behind our progess bar. We're extending the text to the whole screen to avoid drawing the background twice.
    while (len(lines) <= height): lines.append(" " * width)                                 # adds a final "forbidden line" to erase visual artifacts that I'm encountering —— it would have been padded to the correct width later, but lets do it now by multplying " " by our 'width' parameter
    dashboard_logger.debug(f"\t\tlines are: {lines}")
    total_characters = width * height                                                       # Calculate the total number of characters needed
    lines =  [line.ljust(width) for line in lines]                                          # Ensure each line is exactly 'width' characters long by padding with spaces if necessary
    while len(lines) < height: lines.append(' ' * width)                                    # Pad with empty lines if fewer lines were created
    result = "\n".join(lines[:height+1])                                                    # we have to add 1 to account for the "forbidden line" we added
    return result


def test_split_into_columns():
    global winamp_info_field_height, winamp_info_field_width
    input_string = "This is an example string that will be split into a rectangular shape."
    formatted_string = split_into_columns(input_string, width=winamp_info_field_width, height=winamp_info_field_height)
    print("'" + formatted_string + "'")






if __name__ == "__main__":
    try:
        startup_start = time.perf_counter()
        # get winamp info
        w = cjs_winamp.initialize_and_get_winamp_object()

        # set up which dash we use
        en_dash = "–"
        em_dash = "—"
        dash = em_dash
        if winamp_info_monospaced_font: dash = em_dash + em_dash
        else                          : dash = em_dash

        # Set the signal handlers, to send a complete frame to the LCD before exit
        def sighandler(signum, frame):
            global stop
            stop = True
        signal.signal(signal.SIGINT , sighandler)
        signal.signal(signal.SIGTERM, sighandler)
        is_posix = os.name == 'posix'
        if is_posix: signal.signal(signal.SIGQUIT, sighandler)

        lcd_comm = None

        def initialize_frame():
            global orientation_to_use
            lcd_comm_setup_start = 0
            lcd_comm_setup_end   = 99999
            dashboard_logger.info("💚INIT!💚")
            # Build your LcdComm object based on the HW revision
            build_lcdcomm_object_start = time.perf_counter()
            #lcd_comm = None
            if REVISION == "A":
                dashboard_logger.info("🅰 Selected Hardware Revision A (Turing Smart Screen 3.5\" & UsbPCMonitor 3.5\"/5\")")
                # NOTE: If you have UsbPCMonitor 5" you need to change the width/height to 480x800 below
                if UsbPCMonitor: lcd_comm = LcdCommRevA(com_port=COM_PORT, display_width=480, display_height=800)
                else           : lcd_comm = LcdCommRevA(com_port=COM_PORT, display_width=320, display_height=480)
            elif REVISION == "B":
                dashboard_logger.info("Selected Hardware Revision B (XuanFang screen 3.5\" version B / flagship)")
                lcd_comm = LcdCommRevB(com_port=COM_PORT)
            elif REVISION == "C":
                dashboard_logger.info("Selected Hardware Revision C (Turing Smart Screen 5\")")
                lcd_comm = LcdCommRevC(com_port=COM_PORT)
            elif REVISION == "D":
                dashboard_logger.info("Selected Hardware Revision D (Kipye Qiye Smart Display 3.5\")")
                lcd_comm = LcdCommRevD(com_port=COM_PORT)
            elif REVISION == "SIMU":
                dashboard_logger.info("Selected 3.5\" Simulated LCD")
                lcd_comm = LcdSimulated(display_width=320, display_height=480)
            elif REVISION == "SIMU5":
                dashboard_logger.info("Selected 5\" Simulated LCD")
                lcd_comm = LcdSimulated(display_width=480, display_height=800)
            else:
                dashboard_logger.error("⁉ Unknown revision")
                try:                   sys.exit(1)
                except Exception as e: os._exit(1)
            build_lcdcomm_object_end = time.perf_counter()
            dashboard_logger.debug(f"\t(built lcd comm object p in {build_lcdcomm_object_end - build_lcdcomm_object_start} seconds)") #5.26s
            try:
                lcd_comm_setup_start = time.perf_counter()
            except Exception as e:
                dashboard_logger.debug(f"💣 Exception when initializing frame: {e}")

            try:
                lcd_reset_start      = time.perf_counter()
            except Exception as e:
                dashboard_logger.debug(f"🎅🏻 Exception when initializing frame: {e}")
            try:
                if not suppress_init: lcd_comm.Reset(sleep_time=5)          #🐐 hardcoded value                   # Reset screen in case it was in an unstable state (screen is also cleared) - this is the slowest part of startup
            except Exception as e:
                dashboard_logger.debug(f"🥨 Exception when initializing frame: {e}")
            try:
                lcd_reset_end        = time.perf_counter()
                dashboard_logger.debug(f"\t(lcd reset in {lcd_reset_end - lcd_reset_start} seconds)")             # 5.01s until i realized the library had a sleep command in it and changed that into a parameter for startup-speed tweaks
                if not suppress_init: lcd_comm.InitializeComm()                                                   # Send initialization commands
            except Exception as e:
                dashboard_logger.debug(f"😑 Exception when initializing frame: {e}")
            try:
                #Set Brightness:  must be multiples of 5, apparantly —— Set brightness in % (warning: revision A display can get hot at high brightness! Keep value at 50% max for rev. A)
                lcd_comm.SetBrightness(level=47) #🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥 ❗❗❗❗❗ FIRE HAZARD OVER 50 ❗❗❗❗❗ 🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥                               #50->42->47
                lcd_comm.SetBackplateLedColor(led_color=(255, 255, 255))                                          # Set backplate RGB LED color (for supported HW only)
            except Exception as e:
                dashboard_logger.debug(f"🐞 Exception when initializing frame: {e}")

            try:
                lcd_comm.SetOrientation(orientation_to_use)                                                       # Set orientation (screen starts in Portrait)
                dashboard_logger.debug(f"\t🔀set orientation to {orientation_to_use} [0=p,2=l,1=rev_p,3=rev_l])") #options & values are: Orientation.PORTRAIT=0  Orientation.LANDSCAPE=2  Orientation.REVERSE_PORTRAIT=1  Orientation.REVERSE_LANDSCAPE=3
            except Exception as e:
                dashboard_logger.debug(f"👀 Exception when initializing frame: {e}")

            #timer stuff:
            lcd_comm_setup_end = time.perf_counter()
            dashboard_logger.debug(f"\t(lcd startup in {lcd_comm_setup_end - lcd_comm_setup_start} seconds)")     #5.01s

            return lcd_comm


        ############## INITIALIZE FRAME: ##############

        if not lcd_comm:
            if not suppress_init: lcd_comm = initialize_frame()
            #^^^^^^^^^^^🐐 still must consider if this is helping or hurting
            #^^^^^^^^^^^🐐 20240910 - let's try w/o
            frame_last_initialized = time.perf_counter()


        ########################################## DEALING WITH COMMAND-LINE PARAMETERS: #########################################
        usage_keys_raw                 = ["?", "h", "help", "usage"]
        blackened_keys_raw             = ["b", "black", "black-first", "black_first", "blackfirst", "blacken", "blacken-first", "blacken_first", "blackenfirst", "reset", "blacken-first", "blacken_first", "blackenfirst", "erase", "erase-first", "erase_first", "erasefirst"]
        run_once_keys_raw              = ["q", "1", "quick", "run-once", "runonce", "run_once", "once", "quick-run", "quick_run", "quickrun" "fast"]
        no_darken_keys_raw             = ["n", "nd", "nodarken", "no_darken", "no-darken", "darken-no", "darken_no", "darkenno", "light" "not-dark", "not_dark", "notdark", "darkn't"]
        force_display_winamp_info_raw  = ["w", "s", "winamp", "song", "display-winamp", "display_winamp", "displaywinamp", "force-winamp", "force_winamp", "forcewinamp"]
        usage_keys_final               = list(set(f"{p}{w.lstrip('-/')}" for w in         usage_keys_raw for p in ["--", "/", "-", ""]))
        blackened_keys_final           = list(set(f"{p}{w.lstrip('-/')}" for w in     blackened_keys_raw for p in ["--", "/", "-", ""]))
        run_once_keys_final            = list(set(f"{p}{w.lstrip('-/')}" for w in      run_once_keys_raw for p in ["--", "/", "-", ""]))
        no_darken_keys_final           = list(set(f"{p}{w.lstrip('-/')}" for w in     no_darken_keys_raw for p in ["--", "/", "-", ""]))
        force_display_winamp_info_keys = list(set(f"{p}{w.lstrip('-/')}" for w in force_display_winamp_info_raw for p in ["--", "/", "-", ""]))

        # Command-line-determined behavior:
        run_once = False
        force_display_winamp_info = False
        if len(sys.argv) > 1:
            for arg in sys.argv[1:]:
                if arg in blackened_keys_final:
                    dashboard_logger.debug("blackening background")
                    blackening_start = time.perf_counter()
                    lcd_comm.DisplayBitmap("res/backgrounds/800x480_black.png", use_cache=False)
                    blackening_end = time.perf_counter()
                    dashboard_logger.debug(f"blackening took {blackening_end - blackening_start:.3f} s")
                elif arg in     run_once_keys_final: run_once         = True
                elif arg in    no_darken_keys_final: darken_cover_art = False
                elif arg in        usage_keys_final: usage()
                elif arg in force_display_winamp_info_keys: force_display_winamp_info = True
                else: dashboard_logger.warning(f"Unrecognized argument: {arg}")
        ########################################## DEALING WITH COMMAND-LINE PARAMETERS ##########################################


        ############## DISPLAY BACKGROUND IMAGE: ##############
        if background_image_filename:
            dashboard_logger.debug("setting background_image_filename picture [if any]")
            start = time.perf_counter()
            if background_image_filename: lcd_comm.DisplayBitmap(background_image_filename)
            end = time.perf_counter()
            dashboard_logger.debug(f"background_image_filename picture set (took {end - start:.3f} s)")

        # initialize variables used in our loop
        cleared                   = False
        stopped                   = True                   #default to stopped status until we hear otherwise, so that we can check on vlc player intead
        playing                   = False
        paused                    = False
        force_update_clock        = True                   #we want the clock on our first draw
        force_update_winamp_info  = True                   #and our title on the first draw too
        #force_update_cover       = False
        track_has_been_changed    = True                   #True so we initialize the same way as if we just switched to that track
        last_playing_status       = None
        status                    = None
        vlc_title                 = None
        bar_value                 = 0
        track_progress_percentage = 100
        last_displayed_message    = ""
        last_formatted_time       = ""
        artist_last               = ""
        title_last                = ""
        winamp_info_for_printing  = winamp_not_found_message
        last_params_without_bg    = {}
        params_without_bg         = {}

        #conclude startup
        startup_end = time.perf_counter()
        dashboard_logger.debug(f"\t(started up in {startup_end - startup_start} seconds)") #5.26s

        #MAIN: THIS IS THE MAIN MAIN MAIN: infinitely loop through to keep updating our display:
        while True:
            force_frame_init = False
            main_loop_start = time.perf_counter()



            dashboard_logger.debug(f"🚼🚼🚼🚼🚼 lcd_comm.successfully_reset=={lcd_comm.successfully_reset} 🚼🚼🚼🚼🚼")
            if lcd_comm.successfully_reset:
                powercycle_update_needed    = True
                lcd_comm.successfully_reset = False
            else:
                powercycle_update_needed    = False



            ################################# DISPLAY CLOCK: ################################
            dashboard_logger.debug(f"\n\n\n\n🕘 TIME: decide whether to render clock or not")
            if not display_clock:
                dashboard_logger.debug("🕘 TIME: ⛔ No, not rendering the clock")
            else:
                time_draw_start = time.perf_counter()
                ### fixes orientation after unplugging->replugging:
                try:
                    lcd_comm.SetOrientation(orientation_to_use)                                                       # Set orientation (screen starts in Portrait)
                    dashboard_logger.debug(f"\t🔀set orientation to {orientation_to_use} [0=p,2=l,1=rev_p,3=rev_l])") #options & values are: Orientation.PORTRAIT=0  Orientation.LANDSCAPE=2  Orientation.REVERSE_PORTRAIT=1  Orientation.REVERSE_LANDSCAPE=3
                except Exception as e:
                    dashboard_logger.debug(f"👀 Exception when initializing frame: {e}")
                try:
                    formatted_time = datetime.now().strftime(clock_format)
                    dashboard_logger.debug(f"🕘 TIME: ✅1️⃣formatted time: {formatted_time}")
                    coin_flip = 0
                    if debug_clock_timey_wimey:
                        import random
                        if (random.randint(1, 2)==2): coin_flip=1
                    if formatted_time.startswith("0"):
                        if not debug_clock_timey_wimey or (debug_clock_timey_wimey and coin_flip==1):
                            formatted_time = formatted_time .lstrip('0').replace(' 0', ' ')
                    elif formatted_time.startswith("1") and debug_clock_timey_wimey:
                        if coin_flip==1: formatted_time = formatted_time[1:]
                    dashboard_logger.debug(f"🕘 TIME: ✅3️⃣formatted time: '{formatted_time}'")
                    if (formatted_time != last_formatted_time) or force_update_clock or debug_clock_tenacious:
                        params = {
                            "font"             : "roboto/Roboto-Bold.ttf"   ,
                            "font_size"        :  clock_font_size           ,
                            "x"                :  clock_x                   ,
                            "y"                :  clock_y                   ,
                            "font_color"       : (255, 0,   0)              ,
                            "background_color" :  clock_background_color    ,
                            "background_image" :  None                      ,
                            "text"             :  formatted_time            ,
                            "width"            :  clock_width               ,
                            "height"           :  clock_height              ,
                            "align"            : "left"                     ,
                            "transparent"      : True                       ,   #not sure how this will play out
                            #"anchor"          : "rb"                       ,
                        }
                        #  ANCHOR:
                        #  Horizontal Text:
                        #        'la' (Left Align): Anchors text at the left side.
                        #        'ra' (Right Align): Anchors text at the right side.
                        #        NOT IMPLEMENTED:'ca' (Center Align): Anchors text at the center horizontally.
                        #  Vertical Text:
                        #        'lt' (Top Left): Anchors text at the top-left corner.
                        #        'ct' (Center Top): Anchors text at the center of the top edge.
                        #        'rt' (Top Right): Anchors text at the top-right corner.
                        #        'lb' (Bottom Left): Anchors text at the bottom-left corner.
                        #        'cb' (Center Bottom): Anchors text at the center of the bottom edge.
                        #        'rb' (Bottom Right): Anchors text at the bottom-right corner.
                        #        'mc' (Middle Center): Anchors text at the center of the bounding box.
                        #NO BG FOR CLOCK! if background_image_filename is not None: params["background_image"] = background_image_filename
                        #dashboard_logger.debug(f"🕘 TIME: about to render...params={params}")
                        lcd_comm.DisplayText(**params)
                        #lcd_comm.DisplayTextOriginal(**params)
                        dashboard_logger.debug("🕘 TIME: ✅✅✅✅ Clock rendered! ✅✅✅✅")
                        time.sleep(throttle_after_drawing_clock)
                        last_formatted_time = formatted_time
                        if force_update_clock: force_update_clock = False
                except Exception as e:
                    force_frame_init = True
                    dashboard_logger.debug(f"*********************some kinda exception with printing the current time:\n{e}")
                    #import traceback
                    #traceback.print_exc()
                time_draw_end = time.perf_counter()
                dashboard_logger.debug(f"🕘 TIME: ⏱ drawing time-of-day took {time_draw_end - time_draw_start}s ———\n\n") #0







            ####################################### DETERMINE WINAMP INFO: ######################################
            winamp_state = "unknown"
            try:
                last_playing_status = status
                status = w.get_playing_status()                                         #0.0003s
                if last_playing_status != status or powercycle_update_needed:
                    play_status_changed = True
                    force_display_winamp_info = True   #let's leave it here so the cover art doesn't disappear
                else:
                    play_status_changed = False
                dashboard_logger.debug(f"\n\n\n▶      status = {status} ... changed = {play_status_changed}")
                if   status == cjs_winamp.PlayingStatus.Paused : winamp_state, playing, paused, stopped = ("pause", False,  True, False)
                elif status == cjs_winamp.PlayingStatus.Stopped: winamp_state, playing, paused, stopped = ( "stop", False, False,  True)
                else                                           : winamp_state, playing, paused, stopped = ( "play", True , False, False)
            except Exception as e:
                dashboard_logger.debug(f"\n\n\nFailed to get winamp status!?!?!\n{e}")
                time.sleep(throttle_after_drawing_progress_bar) #TODO use a unique sleep value here

            try:
                if status == cjs_winamp.PlayingStatus.Paused or status == cjs_winamp.PlayingStatus.Stopped and not cleared: #"if the track has changed"
                    cleared                = True
                    previous_track         = ""
                    last_displayed_message = ""
                elif status == cjs_winamp.PlayingStatus.Playing:
                    pass

                ##### The song has changed, so refresh/compute/set all the values here:
                first_bar_since_song = False       #shortens lag between drawing progress bar and drawing the art by reducing the post-bar throttle time to something shorter than the usual post-bar throttle time.
                read_info_start = time.perf_counter()

                #f not use_vlc_info:
                using_winamp_info = True
                if not stopped:
                    trackinfo_raw                = w.get_trackinfo_raw()
                    track_length, track_position = w.get_track_status()
                    artist, title                = w.get_artist(), w.get_title()
                    title                        = cjs_winamp.strip_winamp_title_suffixes(title)
                    using_winamp_info = True
                else:

                    ####################################### DETERMINE VLCPLAYER INFO IF WINAMP IS STOPPED: ######################################
                    if cjs_vlc.is_vlc_running():
                        try:
                            #print(f"\n\n\n******* vlc nice info? *******")
                            vlc_status = cjs_vlc.get_vlc_status()
                            if vlc_status:
                                vlc_information   = vlc_status     .get(  "information", {"Unknown"           })
                                vlc_length_in_s   = vlc_status     .get(       "length", {"Unknown"           })
                                vlc_position_in_s = vlc_status     .get(         "time", {"Unknown"           })
                                vlc_category      = vlc_information.get(     "category", {"Unknown"           })
                                vlc_meta          = vlc_category   .get(         "meta", {"Unknown"           })
                                vlc_season        = vlc_meta       .get( "seasonNumber", {"Unknown"           })
                                vlc_episode       = vlc_meta       .get("episodeNumber", {"Unknown"           })
                                vlc_filename      = vlc_meta       .get(     "filename", {"Unknown"           })
                                vlc_duration      = vlc_meta       .get(     "duration", {"Unknown"           })
                                vlc_title_fresh   = vlc_meta       .get(        "title", {"Unknown"           })  #fall back on filename?
                                if vlc_title_fresh:
                                    if vlc_title_fresh is not vlc_title:
                                        vlc_title_last = vlc_title
                                        vlc_title      = vlc_title_fresh

                            dashboard_logging.debug(f"\t\tvlc    title: {vlc_title   }")
                            dashboard_logging.debug(f"\t\tvlc   season: {vlc_season  }")
                            dashboard_logging.debug(f"\t\tvlc       ep: {vlc_episode }")
                            dashboard_logging.debug(f"\t\tvlc filename: {vlc_filename}")

                            trackinfo_raw  =      ""
                            artist         =     None
                            title          =   vlc_title
                            track_length   =   vlc_length_in_s
                            track_position = vlc_position_in_s

                            using_winamp_info = False
                        except Exception as e:
                            dashboard_logger.debug(f"\n\n\nVLC running, but couldn't get status —— not a problem if it was just closed\n{e}")
                    else:
                        dashboard_logger.debug(f"\n\n\nVLC not running")

                track_progress_percentage = track_position / track_length
                if artist != artist_last or title != title_last: track_has_been_changed = True
                else                                           : track_has_been_changed = False
                if track_has_been_changed:
                    dashboard_logger.debug(f"————— track has been changed because artist={artist} ne artist_last={artist_last} —————")
                    blurb = ""
                    if artist: blurb = artist
                    if artist and title: blurb = blurb + f" {dash} "
                    if title: blurb = blurb + title
                    artist_last              = artist
                    title_last               = title
                    force_update_winamp_info = True
                    #force_update_cover      = True
                    force_update_clock       = True
                    filename                 = None                     #we're only running w.get_current_track_file_path() when we absolutely have to
                    winamp_info_for_printing = split_into_columns(blurb, width=winamp_info_field_width, height=winamp_info_field_height)
                    winamp_info_for_debug    = "\n".join([f"                 ———> [{line}]" for line in winamp_info_for_printing.splitlines()])
                else:
                    dashboard_logger.debug(f"——— track has NOT been changed because artist={artist} eq artist_last={artist_last} ———")

                read_info_end  = time.perf_counter()
                dashboard_logger.debug(f"\t\t(read all info in {read_info_end - read_info_start} seconds)") #0.001s
                dashboard_logger.debug(f"     info_raw = {trackinfo_raw}\n       artist = '{artist}'\n       title  = '{title}'\n     position = {track_position}\n       length = {track_length}      \n   progress % = {track_progress_percentage}\ninfo_for_debug:\n{winamp_info_for_debug}")        #dashboard_logger.debug(f"\n\t\twinamp_info_for_printing='{winamp_info_for_printing}'")
            except Exception as e:
                dashboard_logger.debug(f"\n\n\nUmmmm!?!?! =============> {e}")
            dashboard_logger.debug(f"👻end of gathering ⚡winamp/vlc📺 info\n\n\n\n\n")







            ####################################### DISPLAY PROGRESS BAR: BEGIN ######################################
            if not display_progress_bar:
                dashboard_logger.debug(f"🚫 NOT Displaying Progress Bar!")
            else:
                dashboard_logger.debug(f"☑ Displaying Progress Bar")
                progress_bar_start = time.perf_counter()
                bar_value = (bar_value + 2) % 101
                try:
                    #if playing:
                    bar_color_to_use             = progress_bar_color_foreground
                    if playing: bar_color_to_use = progress_bar_color_foreground    #just making sure
                    if stopped: bar_color_to_use = progress_bar_color_stop
                    if paused:  bar_color_to_use = progress_bar_color_pause
                    dashboard_logger.debug(f"bar_color_to_use is {bar_color_to_use}")
                    params = {
                                "value"             : track_progress_percentage ,
                                "min_value"         :   0                       ,
                                "max_value"         :   1                       ,
                                "x"                 :   0                       , #15
                                "y"                 :   0                       ,
                                "height"            : progress_bar_height       , #40
                                "width"             : progress_bar_width        , #800 #785
                                "bar_outline"       : True                      ,
                                "bar_color"         : bar_color_to_use          , #the color of the *foreground* of the bar
                                "background_color"  : ( 55,  0,  83)            ,
                                "bar_outline_color" : (196, 24,   0)            ,
                                #background_color"  : ( 64, 12,   0)            , #48/64 too low, 96/112 too high but once i added red outline 80 was too high for my taste
                    }
                    if background_image_filename: params["background_image"] = background_image_filename
                    lcd_comm.DisplayProgressBar(**params)
                    if first_bar_since_song: throttle_time_to_use = 0.1
                    else:                    throttle_time_to_use = throttle_after_drawing_progress_bar
                    time.sleep              (throttle_time_to_use)
                except Exception as e:
                    dashboard_logger.debug(f"An error occurred: {e} [X2!]")
                    force_frame_init = True
                first_bar_since_song = False
                progress_bar_end = time.perf_counter()
                dashboard_logger.debug(f"✅(displaying progress bar took {progress_bar_end - progress_bar_start} seconds) 🚒🚒🚒\n\n\n") #0.22
            #################################### DISPLAY PROGRESS BAR: END ########################################



            ####################################### DISPLAY ALBUM ART: ######################################
            #WE'RE NOT CURRENTLY DOING THIS SEPARATELY, LEAVING THIS HERE IN CASE WE CHANGE OUR MIND LATER: #dashboard_logger.debug("drawing album art")        #start = time.perf_counter()        #if force_update_cover:        #    lcd_comm.DisplayBitmap(now_playing_album_art, use_cache=False)        #    force_update_cover = False        #    force_update_winamp_info = True        #end = time.perf_counter()        #dashboard_logger.debug(f"album art (took {end - start:.3f} s)")
            #dashboard_logger.debug(f"————————————————————————————————————————")
            #SAMPLE CODE FOR RADIAL PROGRESS BAR: lcd_comm.DisplayRadialProgressBar(222, 260, 40, 13, min_value=0, max_value=100, angle_start=405, angle_end=135, angle_steps=10, angle_sep=5, clockwise=False, value=bar_value, bar_color=(255, 255, 0), text=f"{10 * int(bar_value / 10)}°C", font="geforce/GeForce-Bold.ttf", font_size=20, font_color=(255, 255, 0), background_image=background)



            ####################################### DISPLAY WINAMP INFO: ######################################
            if display_winamp_info or force_display_winamp_info or powercycle_update_needed:
                dashboard_logger.debug(f"📺📺📺⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡ We gonna display Winamp/VLC info? ⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡⚡📺📺📺")
                try:
                    dashboard_logger.debug(f"📺📺📺⚡⚡⚡ we'll we're gonna try, at least! 📺📺📺⚡⚡⚡")
                    if paused or stopped: force_update_winamp_info = False                               #don't lose the drawn cover art just because that file doesn't exist anymore
                    if play_status_changed or last_displayed_message != winamp_info_for_printing or force_update_winamp_info:
                        dashboard_logger.debug(f"📺📺📺⚡⚡⚡ Looks like play status as changed, getting closer! 📺📺📺⚡⚡⚡")
                        winamp_info_start = time.perf_counter()
                        darken_factor_to_use=1
                        if darken_cover_art:
                            if debug_darkening:  darken_factor_to_use = debug_darkening_factor
                            else:                darken_factor_to_use = darken_factor_default            #0.5 seems good #1.5=make 50% brighter, 0.5=make 50% darker, 1=make same
                        #dashboard_logger.debug(f"\n ***************** Preparing to draw winamp info: ***************** [darken_factor_to_use={darken_factor_to_use}]")
                        background_image_path_to_use = None
                        if not using_winamp_info: background_image_path_to_use = None #🐐this would be where we place a vlc screenshot/cover art
                        if os.path.exists(now_playing_album_art): background_image_path_to_use = now_playing_album_art
                        if paused: color_to_use = winamp_info_font_color_pause
                        else:      color_to_use = winamp_info_font_color
                        dashboard_logger.debug(f"💛💛winamp_info_for_printing={winamp_info_for_printing}")
                        params = {
                               "text"             :  winamp_info_for_printing               ,
                              #"text"             : "Long John Textstring —— I haven't in a long time but yea, wanted to do one for the Barbie movie and a couple others. Lorem ipsum Lorem ipsum Lorem ipsum Lorem ipsum Lorem ipsum Lorem ipsum I keep an email list for movie nightsEOL" ,
                              #"font"             : "roboto-mono/RobotoMono-Regular.ttf"    , #two em-dashes in a row do not quite touch each other 😢
                              #"font"             : "roboto-mono/RobotoMono-SemiBold.ttf"   , #two em-dashes in a row do not quite touch each other 😢
                              #"font"             : "roboto-mono/RobotoMono-Bold.ttf"       , #two em-dashes in a row do not quite touch each other 😢
                              "x"                 :  winamp_info_x                          ,
                              "y"                 :  winamp_info_y                          ,
                              #"font"             : "jetbrains-mono/JetBrainsMono-Bold.ttf" , #LOOKS PRETTY GOOD
                              "font"              :  winamp_info_font                       ,
                              "font_size"         :  winamp_info_font_size                  ,
                              "font_color"        :  color_to_use                           ,
                              #"transparent"      :  True                                   ,
                              #"transparency"     :  0                                      , #0=trans, 128=half, 256=opaque
                              "darken_background" :  True                                   ,
                              "darken_factor"     :  darken_factor_to_use                   ,
                              #"background_color" : (  0,   0, 0)                           ,
                              #"background_color" : (255,   0, 0)                           ,
                              #"background_image" :  None                                   , #DEBUG
                              "use_resizing"      :  True                                   , #to fix the size of the album art image
                              "use_colorshift"    :  colorshift_cover_art                   , #to shift the colors of the art image for readibility
                              "colorshift"        :  colorshift_rgb_shift                   ,
                              #"anchor"           : "mi"                                    ,
                              "transparent"       :  True                                   ,
                              "width"             :  800                                    ,
                              "height"            : (480-progress_bar_height)               ,
                              "bg_image_align"    : "right"                                 , #only right or None works

                        }
                        params_without_bg=params
                        params["background_image"] = None
                        #dashboard_logger.debug(f"WINAMP DISPLAY: params={params}")
                        print(f"WINAMP DISPLAY: params={params}")#need the speed
                        if last_params_without_bg == params_without_bg:
                            dashboard_logger.debug(f"📺📺📺⚡⚡⚡ 🚫🚫🚫 Skipping drawing because we've already used these params:\n\t{params_without_bg}")
                        else:
                            try:
                                dashboard_logger.debug(f"📺📺📺⚡⚡⚡ ✅✅✅✅✅ Drawing!!!! ✅✅✅✅ {winamp_info_for_printing}")
                                if background_image_path_to_use and os.path.exists(background_image_path_to_use): params["background_image"] = background_image_path_to_use                     #it literally may have disappeared in the meanwhile, because the winamp plugin deletes the file if you pause or stop. We really need to use cache it when it exists, except an issue was submitted to the NowPlaying WinampPlugin to create an optio to not deletethe file on pause/stop 🐐
                                #todo: enable image persistence when song is paused/stopped —— and if we enable that, make sure to test what happens when we switch to VLCPlayer
                                #todo: return the generated image from lcd.comm.DisplayText and store output image in last_image variable
                                #todo: run lcd.comm.DisplayText, submitting the last_image:
                                #todo                 If the new image created is the same as last_image, skip drawing.
                                #todo                 If the path to the image no longer exists, substitute last_image rather than having no image at all.
                                lcd_comm.DisplayText(**params)
                                last_params_without_bg=params_without_bg
                            except Exception as e:
                                dashboard_logger.debug(f"some kinda exception with DisplayText:\n{e}")
                            last_displayed_message   = winamp_info_for_printing
                            force_update_clock       = True
                            force_update_winamp_info = False
                            winamp_info_end          = time.perf_counter()
                            dashboard_logger.debug(f"\t\t(drawing winamp info took {winamp_info_end - winamp_info_start:3f} seconds, about to sleep for {throttle_after_drawing_media_info} seconds)")
                            time.sleep(throttle_after_drawing_media_info)
                except Exception as e:
                    force_frame_init = True
                    dashboard_logger.debug(f"some kinda exception with printing the winamp info:\n{e}")
                    import traceback
                    traceback.print_exc()

            if run_once: break

            ##alas, if we have turned the device off and on, it may return in the wrong orientation
            ##let's not slow down the speedy display of cover art when we go to the next track however...
            ##in this situation, we'll render it upside-down 1 time before getting to the end of the loop
            ##fixing it. I think one upside-down display is better than an orientation-setting-delay every song ever
            if force_frame_init:
                cd_comm                = initialize_frame()
                frame_last_initialized = time.perf_counter()
                force_frame_init       = False

            main_loop_end = time.perf_counter()
            dashboard_logger.debug(f"\t\t...main loop took {main_loop_end - main_loop_start:.3f} s")
            time.sleep(throttle_after_end_of_loop)

    except Exception as e:
        dashboard_logger.debug(f"🔥🔥🔥 __main__ exception: 🔥🔥🔥\n🔥🔥🔥 —————> {e}")
        lcd_comm.closeSerial()                          #            Close serial connection at exit

    if lcd_comm: lcd_comm.closeSerial()                 # No. Really close serial connection at exit








spiel_on_inspiration_for_this_project="""
I bought a $13 5-inch screen that has software that creates a dashboard for your PC.  Mine cost $3800 in the end so I did want to monitor it more closely to know what's happening when things go bad. At 11:30pm i googled "usb lcd screen github" and found a python package that could manage it.  Stayed up past dawn and got what I wanted: What song my music player is playing on the device. It was hard to figure out how to grab winamp's various statuses via win32api calls, but someone else had a library i imported that made it a bit simpler.
But it couldn't get the filename of the curently playing song, because they never included an api call for that in their library.
I realized they have a playlist query and a playlist position query, so I could ask it to send the playlist, then go to the correct position in the playlist, and get the filename from there.
But that's a lot of work just to get cover art to send to a 5-inch display.  And what if i'm running it from another computer that doesn't have access to software running on mine? I want wifey to be able to have a display telling her what song is on too, so it needs to work on her computer

Wow. Github was so useful. I found a winamp plugin that actually exports the band/artist name and current cover art to a jpg.  And  since i have all computers' harddrives mapped to all other computers', with environment varaibles for drive letters so the harcoding is the same even when the letters are diferent...
...i can just read those 2 files and not fuck with the api call at all, and have it work from any computer in the house? (There's 3)
Then, i realized they didn't support transparent text, so long song titles were obscuring the image. I need text *over* images.  The original python library didn't have support for that. It was really hard to create transparent text.
In the end, I found a way to combine 2 images, and rendered the text and album art images together as 1 image before sending it to the device as 1 image.
And that was saturday today I'm working on trying to harden the program by catching all the various exceptions so that if i unplug the screen and plug it back in, it still works.
Problem , my outlet is on the right, and the power port is on the left, so i had to create a frame_is_upside_down=True variable and turn the pictture upside down so the cord comes out in the right direction.
My current issue now is after turning the frame on and off again, it doesn't remember that things were upside down, and displays them right-side-eup, which is upside-down-for-me.
It may be something with how big and messy my loop code is. I've been refactoring it into functions but my management variables aren't grouped in a type (which would have been a better way to do it, i now realize) so it's kind of a pain setting up the variable passing just to make the code look prettier. But i also think if i go through the discipline of that, i'll probably find the source of upside-down-after-turning-off-and-on
I don't think it's quite ready to publish though. With aa music collection of 40,000 songs with differently sourced album art, there is a wide enough variance in album art that some files are technically incorrect. And this tends to crash the frame, which is a bummer. But yea, it's not designed for that, so i'm in the kitchen getting a little burned by that aspect.
Was it because i greens-shifted the G in my RGB value down by 64 (but bringing it back up to 0 if i hit the negative) ... in order to make my green text more readable, by removing the green underneath it?
I don't think so. But technically i'm re-encoding the miage when i do that, so how the fuck are some images (out of 40,000, found 2 so far, had to denote what song it was for future testing) randomly causing the frame to crash?   It definitely sends it's data really slow. The screens' framerate is literally like 0.5fps if you're drawing the whole screen. It's not made for this.
I'm hoping i can figure out the image problem. I thought they were being re-encoded internally, so i wonder if the library to convert them isn't handling malformed images correctly, adn if i need to submit a github issue to the author of that library. But then i'm beholden to waiting for him to fix it, and i'm really obsessed with this and the fix might not come for months.
Better to find  it myself.
"""



chat_gps_spiel_on_power_cycling_usb_devices="""
Yes, many modern PCs have USB ports that can be controlled by the operating system or software to turn on and off. This feature is often used for power management, but it can also be used to power cycle devices connected to those ports. Here's how you can achieve this:

1. Using Windows Device Manager: Steps: Open Device Manager. Expand the "Universal Serial Bus controllers" section.
Right-click on the USB Root Hub (there may be multiple) and select "Properties." Go to the "Power Management" tab.
Check or uncheck "Allow the computer to turn off this device to save power." Limitations: This method relies on power-saving features and might not provide direct on-demand control.
2. Using USB Hub with Power Control: Hardware-Based Solution: Some USB hubs come with switches or software control that allows you to turn individual ports on and off. This is useful if you want hardware-level control over power cycling.
3. Using Software Control: USBDeview (by NirSoft): A free utility that allows you to enable/disable USB devices connected to your computer. This can be used to power cycle the device.
DevCon (Microsoft's Device Console): A command-line tool that can enable/disable devices, including USB ports, allowing you to create scripts to power cycle devices.
4. Motherboard-Specific Software: BIOS/UEFI Settings:

Some motherboards allow USB port control through BIOS/UEFI settings. This is typically more common in high-end motherboards.
Manufacturer Software:
Some manufacturers provide utilities that allow you to control USB ports, especially on gaming or workstation motherboards.

5. Advanced Power Management (APM) API: For Developers:
If you’re comfortable with programming, you can use Windows APIs to control USB ports programmatically.
Considerations: Not all USB ports or motherboards support on-demand power cycling.
Some devices may not respond well to power cycling via software control, so hardware solutions like a controllable USB hub might be more reliable.
This feature is particularly useful for troubleshooting or resetting USB devices without physically unplugging them.
"""


rejected_todos="""
REJECTED TODO: DRAW CLOCK WITH BG THAT IS CACHED SECTION OF OTHER IMAGE SO IT'S TRANSLUCENt. maybe merge it together with other updates if they exist, or just update the clock if they don't. However, this is a LOT of work just to save a single clock update, so nah, let's not do this.
"""


#songs_that_crash_us="""
#
#SONGS THAT CRASH THE SCREEN:
#DEFNITELY - twice C:\mp3\Ramones\1987 - Halfway To Sanity\01_I Wanna Live.flac
#
#??        C:\mp3\NoFX\2020 - NOFX vs Frank Turner - West Coast vs Wessex\07_Frank Turner - Bob (by NoFX).flac
#
#American Dad: Krampus & Steve - Krampus And...(?)
#
#"""

