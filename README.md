# ![Icon](https://raw.githubusercontent.com/mathoudebine/turing-smart-screen-python/main/res/icons/monitor-icon-17865/24.png) turing-smart-screen-python


### How to get this project to work:

This is basicaly functionality that I wrote on top of the ```turing_smart_screen-python``` project, which had a couple enhancements made.

To get this to work:

1. Be a WinAmp & Python user 😉

1. Buy one of the usb screens below ($13 on AliExpress as of 2024/08/15)

1. Change WinAmp's title formatting so that we can parse artist & band properly:
    * Go into ```WinAmp->Preferences```, to the ```Titles``` section (the 5th line on the left). 
    * Look for the ```Advanced Title Formatting``` section on the right
    * Make sure ```Use Advanced title formatting when possible``` is *checked*
    * Change the hypen (-) after ```%artist%``` into an en-dash (–).
    * I prefer the following avanced title display format:<BR>
      ```[%artist% – ]$if2(%title%,$filepart(%filename%))')```
    * This is done because there are many song names and band names that have hyphens in them, and it can be confusing where to split something like "One - Two - Three - Four - Five - Six".  Is it a band named "One - Two - Three - Four" who has a song named "Five - Six", or is it a band named "One - Two" who has a song named "Three - For - Five - Six"?  The ambiguity disappears if you use a wider en-dash (–) to separate the artist from the track title. And frankly it looks better.

1. Configure WinAmp to save the song info & album art of the current song playing song to a file. This allows us to grab that information with fewer resources than sending it through API calls. And allows one to get the same feed on a different computer.
    * 1. Unzip [Aldviva's](https://github.com/Aldaviva) [NowPlayingToFile plugin](https://github.com/Aldaviva/WinampNowPlayingToFile/releases/latest/download/WinampNowPlayingToFile.zip) into your WinAmp folder, right next to ```WinAmp.exe```. 
    * Restart WinAmp
    * Go into ```WinAmp->Preferences```, to the ```Plug-ins``` section (closer to the bottom)
    * Expand the ```Plug-ins``` section to locate the ```General Purpose``` settings (5 lines underneath)
    * In the right pane, your plugins should be listed, and you should see ```Now Playing To File v2.2.0``` as one of the plugins.
    * Click ```Configure selected plug-in``` to open up the ```Now Playing To File plug-in configuration``` pop-up.
    * If you change the format of the plugin's info file, please only add new stuff to the end 😉
    * Change the ```Save album art as``` file location if you are inclined and adventurous  
      (If you do, make sure to change both locations, so that they stay in the same folder together.)
    * Take note of the ```Save album art as``` location — whether you changed it or not.
    * Go to the next track, and verify that the album art correctly saved to that location

1. Let this program know where those files are.
    * set an environment variable called ```NOW_PLAYING_SONG_INFO``` to point to the location of the txt file
    * set an environment variable called ```NOW_PLAYING_ALBUM_ART``` to point to the location of the jpg file
```
   rem EXAMPLE:
   set NOW_PLAYING_ALBUM_ART=c:\mp3\lists\winamp_now_playing.jpg
   set NOW_PLAYING_SONG_INFO=c:\mp3\lists\winamp_now_playing.txt
```
    
1. Configure options in the ```winamp_dashboard.py`` script. At this point, relevant instructions in the configuration section at the top of that file, and more likely to be up-to-date and accurate there.   Set things like:
	* Do you want to    blur    the background cover art to make information easier to read? How much?
	* Do you want to colorshift the background cover art to make information easier to read? Which colors and how much? Green font?  Shift green down 40 by setting colorshift to (0,0,-40)!
	* Is your frame upside-down or not? (because the cable comes out in the wrong direction for your situation)
	* Do you want the clock in the corner? Do you want it to display the seconds as well?
	* What color(s) do you want the progress bar to be? 
	* Do you even want a progress bar? [if you don't: might want to expand–and–move-up cover art by 40px]
	* What font do you want the information to be?
	* Do you want it to tell you what you're watching in VLCplayer too? 
	* How long do you want to wait after drawing each element?



# You're done!  But there are some potential bonus features:

1. For VLC functionality (experimental):
	* make sure ```vlc.exe``` is always called with the ```--extraintf http --http-password password``` options to open access to VLCplayer
	* install the python-vlc library with ```pip install python-vlc```
	* if you see a bunch of ```stale plugins cache``` errors, you can fix with ```"C:\Program Files\VideoLAN\VLC\vlc-cache-gen.exe" "C:\Program Files\VideoLAN\VLC\plugins"``` (found the [answer here](https://stackoverflow.com/questions/68246840/how-to-avoid-main-libvlc-error-when-using-the-python-vlc-package)])
	* Enable the HTTP Interface in VLC:
		* Open *VLC* and go to ```Tools > Preferences```.
		* At the bottom, select ```All``` under ```Show settings```.
		* Search for ```lua``` in the search box. (Alternate instructions are to navigate to ```Interface > Main``` interfaces and check the ```HTTP``` checkbox, but I think searching is easier.)
		* Under ```Interface > Main interfaces > Lua```, you can set a password for the HTTP interface. Use ```winampdashboard``` as a password if you don't want to change what I've hardcoded already
		* Set the port to ```8080```.  My default was something else, but the ```python-vlc``` library instructions mention port 8080 a
		* The HTTP interface will run on *localhost:8080 by* default, or whatever alternate port you just chose.







```


### ⚠️ DISCLAIMER - PLEASE READ ⚠️

This project is **not affiliated, associated, authorized, endorsed by, or in any way officially connected with Turing / XuanFang / Kipye brands**, or any of theirs subsidiaries, affiliates, manufacturers or sellers of their products. All product and company names are the registered trademarks of their original owners.

This project is an open-source alternative software, NOT the original software provided for the smart screens. **Please do not open issues for USBMonitor.exe/ExtendScreen.exe or for the smart screens hardware here**.
* for Turing Smart Screen, use the official forum here: http://discuz.turzx.com/
* for other smart screens, contact your reseller
---


A Python Winamp monitor program for **small IPS USB-C (UART) displays.**    

Supported operating systems : macOS, Windows, Linux (incl. Raspberry Pi), basically all OS that support Python 3.8+  

### Supported smart screens models:

| ✅ Turing Smart Screen 3.5"                           | ✅ XuanFang 3.5"                                   | ✅ Turing Smart Screen 5"                    |
|------------------------------------------------------|---------------------------------------------------|---------------------------------------------|
| <img src="res/docs/turing.webp"/>                    | <img src="res/docs/xuanfang.webp"/>               | <img src="res/docs/turing5inch.png"/>       |
| also improperly called "revision A" by the resellers | revision B & flagship (with backplate & RGB LEDs) | basic support (no video or storage for now) |

| ✅ [UsbPCMonitor 3.5" / 5"](https://aliexpress.com/item/1005003931363455.html)                       | ✅ [Kipye Qiye Smart Display 3.5"](https://www.aliexpress.us/item/3256803899049957.html) |
|-----------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------|
| <img src="res/docs/UsbPCMonitor_5inch.webp" width="60%" height="60%"/>                              | <img src="res/docs/kipye-qiye-35.webp" width="60%" height="60%"/>                       |
| Unknown manufacturer, visually similar to Turing 3.5" / 5". Original software is `UsbPCMonitor.exe` | Front panel has an engraved inscription "奇叶智显" Qiye Zhixian (Qiye Smart Display)        |

### [> What is my smart screen model?](https://github.com/mathoudebine/turing-smart-screen-python/wiki/Hardware-revisions)  

**Please note all listed smart screens are different products** designed and produced by different companies, despite having a similar appearance. Their communication protocol is also different.  
This project offers an abstraction layer to manage all of these products in a unified way, including some product-specific features like backplate RGB LEDs for available models!

If you haven't received your screen yet but want to start developing your theme now, you can use the [**"simulated LCD" mode!**](https://github.com/mathoudebine/turing-smart-screen-python/wiki/Simulated-display)

### Not (yet) supported / not tested smart screen models:

| ❔ _Turing Smart Screen 8.8"_                                                                                                                     | ❔ _Turing Smart Screen 2.1"_                                                                                                                     | ❌ _[(Fuldho?) 3.5" IPS Screen](https://aliexpress.com/item/1005005632018367.html)_                                                                                                                                                                                                                |
|--------------------------------------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| <img src="res/docs/turing8inch.jpg"/>                                                                                                            | <img src="res/docs/turing2inch.webp"/>                                                                                                           | <img src="res/docs/fuldho_3.5.jpg"/>                                                                                                                                                                                                                                                              |
| Very similar protocol than the 5". [Support planned in a future version.](https://github.com/mathoudebine/turing-smart-screen-python/issues/264) | Very similar protocol than the 5". [Support planned in a future version.](https://github.com/mathoudebine/turing-smart-screen-python/issues/264) | Managed by [proprietary Windows software `SmartMonitor.exe`](https://smartdisplay.lanzouo.com/b04jvavkb). Cannot be supported by this project: [see here](https://github.com/mathoudebine/turing-smart-screen-python/discussions/298). Use alternative library https://github.com/braewoods/hidss |

| ❌ _Waveshare [2.1inch](https://www.waveshare.com/wiki/2.1inch-USB-Monitor) / [2.8inch](https://www.waveshare.com/wiki/2.8inch-USB-Monitor) / [5inch](https://www.waveshare.com/wiki/5inch-USB-Monitor) / [7inch](https://www.waveshare.com/wiki/7inch-USB-Monitor) USB-Monitor_                                                                                                            | ❌ _[GUITION Smart screen](https://aliexpress.com/item/1005006169962183.html)_                                                                                                                                                                                                               |
|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| <img src="res/docs/waveshare-21inch-28inch.png"/>                                                                                                                                                                                                                                                                                                                                          | <img src="res/docs/guition.webp"/>                                                                                                                                                                                                                                                          |
| Sold on [Waveshare shop](https://www.waveshare.com/2.8inch-usb-monitor.htm) or [Aliexpress](https://fr.aliexpress.com/item/1005006071685067.html). Managed by [proprietary Windows software "Waveshare PC Monitor"](https://github.com/mathoudebine/turing-smart-screen-python/wiki/Vendor-apps#waveshare-pc-monitor---vendor-app). Cannot be supported by this project: needs a firmware. | Managed by [proprietary Windows software "GUITION Smart screen"](https://github.com/mathoudebine/turing-smart-screen-python/wiki/Vendor-apps#guition---vendor-app). Cannot be supported by this project: [see here](https://github.com/mathoudebine/turing-smart-screen-python/issues/426). |

| ❔ _[SmartCool Lcd](https://aliexpress.com/item/1005005443609423.html) / [GeekTeches AD35](https://aliexpress.com/item/1005004858688084.html) / AIDA64 / AX206_                                   |
|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| <img src="res/docs/ax206.jpg" width="30%" height="30%" /> <img src="res/docs/geekteches_ad35.jpg" width="30%" height="30%" /> <img src="res/docs/smartcool_lcd.webp" width="30%" height="30%" /> |
| Not supported. Produced by multiple manufacturers, all use the same [Appotech AX206 hacked photo frame firmware](https://github.com/dreamlayers/dpf-ax). Supported by AIDA64 and lcd4linux       |

## How to start

### [> Follow instructions on the wiki to configure and start this project.](https://github.com/mathoudebine/turing-smart-screen-python/wiki)

There are 2 possible uses of this project Python code:
* **[as a System Monitor](#system-monitor)**, a standalone program working with themes to display your computer HW info and custom data in an elegant way.
[Check if your hardware is supported.](https://github.com/mathoudebine/turing-smart-screen-python/wiki/System-monitor-:-hardware-support)
* **[integrated in your project](#control-the-display-from-your-python-projects)**, to fully control the display from your own Python code.

## System monitor

This project is mainly a complete standalone program to use your screen as a system monitor, like the original vendor app.  
Some themes are already included for a quick start!  
### [> Configure and start system monitor](https://github.com/mathoudebine/turing-smart-screen-python/wiki/System-monitor-:-how-to-start)
<img src="res/docs/config_wizard.png"/>  

* Fully functional multi-OS code base (operates out of the box, tested on Windows, Linux & MacOS).
* Display configuration using GUI configuration wizard or `config.yaml` file: no Python code to edit.
* Compatible with [3.5" & 5" smart screen models (Turing, XuanFang...)](https://github.com/mathoudebine/turing-smart-screen-python/wiki/Hardware-revisions). Backplate RGB LEDs are also supported for available models!
* Support [multiple hardware sensors and metrics (CPU/GPU usage, temperatures, memory, disks, etc)](https://github.com/mathoudebine/turing-smart-screen-python/wiki/System-monitor-:-themes#stats-entry) with configurable refresh intervals.
* Allow [creation of themes (see `res/themes`) with `theme.yaml` files using theme editor](https://github.com/mathoudebine/turing-smart-screen-python/wiki/System-monitor-:-themes) to be [shared with the community!](https://github.com/mathoudebine/turing-smart-screen-python/discussions/categories/themes)
* Easy to expand: [custom Python data sources](https://github.com/mathoudebine/turing-smart-screen-python/wiki/System-monitor-:-themes#add-custom-stats-to-a-theme) can be written to pull specific information and display it on themes like any other sensor.
* Auto-detect COM port based on the selected smart screen model.
* Tray icon with Exit option, useful when the program is running in background.

### [> List and preview of included themes](res/themes/themes.md)
<img src="res/themes/3.5inchTheme2/preview.png" height="150" /> <img src="res/themes/Terminal/preview.png" height="150" /> <img src="res/themes/Cyberpunk-net/preview.png" height="150" /> <img src="res/themes/bash-dark-green-gpu/preview.png" height="150" /> <img src="res/themes/Landscape6Grid/preview.png" width="150" /> <img src="res/themes/LandscapeMagicBlue/preview.png" width="150" /> <img src="res/themes/LandscapeEarth/preview.png" width="150" /> ... [view full list](res/themes/themes.md)
### [> Themes creation/edition (using theme editor)](https://github.com/mathoudebine/turing-smart-screen-python/wiki/System-monitor-:-themes)
### [> Themes shared by the community](https://github.com/mathoudebine/turing-smart-screen-python/discussions/categories/themes)
<img src="https://user-images.githubusercontent.com/79225820/203648707-6f043068-5c9d-454d-9c0a-3d9ea02ece77.jpg" height="150" /> <img src="https://user-images.githubusercontent.com/121983479/210663324-994c987a-6489-4482-8883-db74ef566014.jpg" height="150" />
<img src="https://user-images.githubusercontent.com/120036534/208128675-897f60cd-5647-40b7-b074-b56b67e775dd.png" height="150" /> <img src="https://user-images.githubusercontent.com/65172896/217549510-149913ac-ef4e-4f61-8f5e-6d768483a02c.png" height="150" /> and more... Share yours!

## Control the display from your Python projects

If you don't want to use your screen for system monitoring, you can just use this project as a module from any Python code to do some simple operations on the display:
- **Display custom picture**
- **Display text**
- **Display horizontal / radial progress bar**
- **Screen rotation**
- Clear the screen (blank)
- Turn the screen on/off
- Display soft reset
- Set brightness
- Set backplate RGB LEDs color (on supported hardware rev.) 

This project will act as an abstraction library to handle specific protocols and capabilities of each supported smart screen models in a transparent way for the user.
Check `simple-program.py` as an example.

### [> Control the display from your code](https://github.com/mathoudebine/turing-smart-screen-python/wiki/Control-screen-from-your-own-code)

## Troubleshooting
If you have trouble running the program as described in the wiki, please check [open/closed issues](https://github.com/mathoudebine/turing-smart-screen-python/issues) & [the wiki Troubleshooting page](https://github.com/mathoudebine/turing-smart-screen-python/wiki/Troubleshooting)

## They're talking about it!

* [Hackaday - Cheap LCD Uses USB Serial](https://hackaday.com/2023/09/11/cheap-lcd-uses-usb-serial/)  


* [CNX Software - Turing Smart Screen – A low-cost 3.5-inch USB Type-C information display](https://www.cnx-software.com/2022/04/29/turing-smart-screen-a-low-cost-3-5-inch-usb-type-c-information-display/)


* [Phazer Tech - Turing Smart Screen Python ](https://phazertech.com/tutorials/turing-smart-screen.html)

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=mathoudebine/turing-smart-screen-python&type=Date)](https://star-history.com/#mathoudebine/turing-smart-screen-python&Date)

