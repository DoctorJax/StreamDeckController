import subprocess
from PIL import Image

def mutedStatus():
    icon = "/home/jackson/GitRepos/.StreamDeckController/pages/imgs/white-micicon.png"
    output = subprocess.getoutput(r'amixer get Capture | grep -o "\[on\]"')
    if output == "":
        icon = "/home/jackson/GitRepos/.StreamDeckController/pages/imgs/white-micicon-mute.png"
    elif output == "[on]":
        icon = "/home/jackson/GitRepos/.StreamDeckController/pages/imgs/white-micicon.png"
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
