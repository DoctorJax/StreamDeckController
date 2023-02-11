import subprocess
import os
from PIL import Image

icon = "./pages/imgs/example/white.jpg"

def audioStatus():
    output = subprocess.getoutput(r'pactl get-default-sink | grep -o "CORSAIR"')
    if output == "":
        icon = "./pages/imgs/earbuds.png"
    elif output == "CORSAIR":
        icon = "./pages/imgs/headphones.png"
    return icon

def batteryStatus():
    output = subprocess.getoutput(r'pactl get-default-sink | grep -o "CORSAIR"')
    if output == "":
        battery = ""
    elif output == "CORSAIR":
        battery = subprocess.getoutput(r"headsetcontrol -b | grep Battery | awk -F ' ' '{ print $2 }'")
        if battery == "Unavailable":
            battery = "Off"
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
    global icon
    icon = audioStatus()

    subprocess.Popen('/home/jackson/.scripts/audioswap.sh -t', shell=True)
