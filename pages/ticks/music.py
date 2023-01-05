import subprocess
from PIL import Image

def mpcStatus():
    icon = "/home/jackson/GitRepos/.StreamDeckController/pages/imgs/play.png"
    output = subprocess.getoutput(r'mpc | grep -ow "playing"')
    if output == "":
        icon = "/home/jackson/GitRepos/.StreamDeckController/pages/imgs/play.png"
    elif output == "playing":
        icon = "/home/jackson/GitRepos/.StreamDeckController/pages/imgs/pause.png"
    return icon

def nextTickWait(coords, page, serial):
    return 1

def getKeyState(coords, page, serial, action):
    if action == "music":
        global icon
        icon = mpcStatus()

        return {"caption":"",
                "background": Image.open(icon),
                "fontSize": 12,
                "fontColor": "white",
                "actions": {}}

def keyPress(coords, page, serial):
    global icon
    icon = mpcStatus()

    subprocess.Popen('mpc toggle', shell=True)
