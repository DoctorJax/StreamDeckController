import subprocess
import os
from PIL import Image

icon = "./pages/imgs/example/white.jpg"

def audioStatus():
    output = subprocess.getoutput(r'pactl get-default-sink | grep -Eo "CORSAIR|Dell" | head -1')
    if output == "CORSAIR":
        icon = "./pages/imgs/headphones.png"
    elif output == "Dell":
        icon = "./pages/imgs/speaker.png"
    else:
        icon = "./pages/imgs/earbuds.png"
    return icon

def batteryStatus():
    output = subprocess.getoutput(r'pactl get-default-sink | grep -Eo "CORSAIR"')
    if output == "CORSAIR":
        battery = subprocess.getoutput(r"headsetcontrol -b | grep Battery | awk -F ' ' '{ print $2 }'")
        if battery == "Unavailable":
            battery = "Off"
    else:
        battery = ""
    return battery

def nextTickWait(coords, page, serial):
    return 1

def getKeyState(coords, page, serial, action):
    if action == "audioswap":
        global icon
        icon = audioStatus()
        battery = batteryStatus()

        return {"caption": battery,
                "background": Image.open(icon),
                "fontSize": 13,
                "fontColor": "white",
                "actions": {}}

def keyPress(coords, page, serial):
    icon = audioStatus()
    output = subprocess.getoutput(r'pactl list sinks | grep -Eo "Dell" | head -1')

    if output == "Dell":
        subprocess.Popen('/home/jackson/.scripts/audioswap.sh -s', shell=True)
    else:
        subprocess.Popen('/home/jackson/.scripts/audioswap.sh -t', shell=True)
