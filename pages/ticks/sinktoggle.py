import subprocess
import os
from PIL import Image

icon = "/home/jackson/StreamDeckController/pages/imgs/example/white.jpg"

def audioStatus():
    output = subprocess.getoutput(r'pactl get-default-sink | grep -o "CORSAIR"')
    if output == "":
        icon = "/home/jackson/StreamDeckController/pages/imgs/earbuds.png"
    elif output == "CORSAIR":
        icon = "/home/jackson/StreamDeckController/pages/imgs/headphones.png"
    return icon

def nextTickWait(coords, page, serial):
    return 1

def getKeyState(coords, page, serial, action):
    if action == "audioswap":
        global icon
        icon = audioStatus()

        return {"caption":"",
                "background": Image.open(icon),
                "fontSize": 12,
                "fontColor": "white",
                "actions": {}}

def keyPress(coords, page, serial):
    global icon
    icon = audioStatus()

    subprocess.Popen('/home/jackson/.scripts/audioswap.sh -t', shell=True)
