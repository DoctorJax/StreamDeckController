from time import localtime, strftime
import subprocess

formats = ["%I", "%M", "%S"]

def nextTickWait(coords, page, serial) :
    return 1 #Time until the next tick in seconds

def getKeyState(coords, page, serial, action) : #Runs every tick
    #print(coords, page, serial, action)

    if action == "hour" :
        return {"caption": strftime(formats[0], localtime()),
                "fontSize": 25,
                "fontColor": "white",
                "actions": {}}

    if action == "minute" :
        return {"caption": strftime(formats[1], localtime()),
                "fontSize": 25,
                "fontColor": "white",
                "actions": {}}

    if action == "second" :
        return {"caption": strftime(formats[2], localtime()),
                "fontSize": 25,
                "fontColor": "white",
                "actions": {}}

    if action == "date" :
        return {"caption": strftime("%b %d\n%A", localtime()),
                "fontSize": 15,
                "fontColor": "white",
                "actions": {}}

def keyPress(coords, page, serial) :
    subprocess.Popen('kitty --class DateTime --hold bash -c "watch -t -n1 date +%m-%d-%Y_%T" &', shell=True)
