import subprocess
import os
from PIL import Image

icon = "/home/jackson/StreamDeckController/pages/imgs/example/white.jpg"

def mutedStatus():
    output = subprocess.getoutput(r'amixer get Capture | grep -o "\[on\]"')
    if output == "":
        icon = "/home/jackson/StreamDeckController/pages/imgs/white-micicon-mute.png"
    elif output == "[on]":
        icon = "/home/jackson/StreamDeckController/pages/imgs/white-micicon.png"
    return icon

def nextTickWait(coords, page, serial):
    return 1

def getKeyState(coords, page, serial, action):
    if action == "micmute":
        global icon
        icon = mutedStatus()

        return {"caption":"",
                "background": Image.open(icon),
                "fontSize": 12,
                "fontColor": "white",
                "actions": {}}

def keyPress(coords, page, serial):
    global icon
    icon = mutedStatus()

    subprocess.Popen('/home/jackson/.scripts/micmute.sh', shell=True)
