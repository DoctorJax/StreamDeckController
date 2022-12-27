from time import localtime, strftime

format = 2
formats = ["%I:%M", "%H:%M", "%I:%M:%S\n%m-%d"]

def nextTickWait(coords, page, serial) :
    return 1 #Time until the next tick in seconds

def getKeyState(coords, page, serial, action) : #Runs every tick
    #print(coords, page, serial, action)

    if action == "clock" :
        return {"caption": strftime(formats[format], localtime()),
                "fontSize": 13,
                "fontColor": "white",
                "actions": {}}

def keyPress(coords, page, serial) : #Cycle through time formats on keypress
    global format
    format += 1

    if format+1 > len(formats) :
        format = 0

#print("Hello, world!")
