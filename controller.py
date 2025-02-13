from StreamDeck.DeviceManager import DeviceManager
from StreamDeck.ImageHelpers import PILHelper
from PIL import Image, ImageDraw, ImageFont
import subprocess
import webbrowser
import importlib
import threading
import platform
import keyboard
import random
import uuid
import json
import math
import time
import sys
import os

class button :
    def __init__(self, keyIndex, controller) :
        self.controller = controller
        self.keyIndex = keyIndex

        #Get the coords of the button. (Top left button is 0x0.)
        self.x = (keyIndex % controller.width)
        self.y = math.ceil((keyIndex+1) / controller.width)-1

        self.coords = f"{self.x}x{self.y}"

        self.caption = ""
        self.fontSize = 14
        self.fontColor = "white"
        self.activated = False
        self.font = controller.fontName
        self.fontAlignment = "center"
        #self.font = "C:\\Windows\\Fonts\\Arial.ttf"

        self.background = Image.new("RGB", (controller.buttonRes, controller.buttonRes))
    
    def setCaption(self, caption) :
        self.caption = str(caption)

    def setFont(self, font, size=None, color=None) :
        self.font = font

        if size :
            self.fontSize = size
        
        if color :
            self.fontColor = color

    def sendToDevice(self) :
        if not self.activated :
            size = 0
        else :
            size = round(self.controller.buttonRes / 6)

        try :
            image = PILHelper.create_scaled_image(self.controller.deck, self.background, margins=[size, size, size, size])
        except :
            return

        draw = ImageDraw.Draw(image)
        
        fontSize = self.fontSize
        if self.activated :
            fontSize = round(fontSize / 1.25)

        if not self.caption.strip() == "" :

            try :
                font = self.controller.getFont(self.font, fontSize) #Load font from memory
            except Exception as e :
                font = None
                self.caption = "NO\nFONT" #Font loading failed. Throw an error
                self.fontColor = "white"
        
            w, h= draw.textsize(self.caption, font=font)

            if self.fontAlignment == "center" :
                y = ((image.height - h) / 2)
            elif self.fontAlignment == "top" :
                if not self.activated : #Move text towards the center when in activated mode
                    y = h
                else :
                    y = h + (self.controller.buttonRes / 8) 
            elif self.fontAlignment == "bottom" :
                if not self.activated : #Move text towards the center when in activated mode
                    y = image.height - h
                else :
                    y = image.height - h - (self.controller.buttonRes / 8)

            x = image.width / 2

            if not self.controller.fontCenterFix :
                x -= (w/2)

            draw.text((round(x), round(y)), text=self.caption, font=font, anchor="ma", fill=self.fontColor, align="center", stroke_width=3, stroke_fill="black")

        nativeImage = PILHelper.to_native_format(self.controller.deck, image)

        with self.controller.deck :
            self.controller.deck.set_key_image(self.keyIndex, nativeImage)

        return image
    
    def loadImage(self, path) :
        self.background = Image.open(path)
    
    def coordsCaption(self) :
        self.caption = f"{self.keyIndex} - {self.coords}"

class controller :
    def __init__(self, deck, font) :
        self.deck = deck

        deck.open()
        deck.reset()

        self.keyCount = deck.key_count()
        self.height = deck.key_layout()[0]
        self.width = deck.key_layout()[1]
        self.serial = deck.get_serial_number()
        self.buttonRes = deck.key_image_format()["size"][0] #The resolution of a single button
        self.fontName = font
        self.fonts = {}

        self.fontCenterFix = False

        self.disableInput = False

        self.resetScreen()
    
    def getFontPath(self, fontName) :
        path = os.path.dirname(sys.argv[0]) #Path to this .py file
        path = os.path.join(path, "fonts", fontName)
        return path
    
    def getFont(self, fontName, size) :
        fontKey = f"{fontName}-{size}"

        if fontKey in self.fonts :
            return self.fonts[fontKey]
        
        font = ImageFont.truetype(self.getFontPath(fontName), round(size))
        self.fonts[fontKey] = font
        return font

    def resetScreen(self) :
        d = {}

        for key in range(self.keyCount) :
            btn = button(key, self)
            d[btn.coords] = btn
        
        self.screen = d
    
    def sendScreenToDevice(self) :
        keysImages = {}

        for key in self.screen :
            image = self.screen[key].sendToDevice()
            keysImages[key] = image
        
        return keysImages
    
    def setKeyCallback(self, func) :
        self.deck.set_key_callback(func)

    def screenshot(self, filename) :
        width = self.buttonRes * self.width
        height = self.buttonRes * self.height

        screenshot = Image.new("RGB", (width, height))
        keysImages = self.sendScreenToDevice() #Re-render every key

        for key in keysImages :
            coordsX = int(key.split("x")[0])
            coordsY = int(key.split("x")[1])

            pixelX = coordsX * self.buttonRes
            pixelY = coordsY * self.buttonRes

            screenshot.paste(keysImages[key], (pixelX, pixelY))
        
        screenshot.save(filename, quality=100)
    
    def coordsCaptions(self, clearScreen) :

        if clearScreen :
            self.resetScreen()

        for key in self.screen :
            if self.screen[key].caption == "" or clearScreen : 
                self.screen[key].coordsCaption()
    
    def randomColors(self) :
        self.resetScreen()

        for key in self.screen :
            self.screen[key].background = Image.new("RGB", (self.buttonRes, self.buttonRes), (random.randint(0,255), random.randint(0,255), random.randint(0,255)))

class pages :
    def __init__(self, controller) :
        self.pages = {}
        self.images = {}
        self.ticks = {}

        self.activePage = {}
        self.activePageName = ""

        self.tickingItems = {}

        self.controller = controller
        self.controller.setKeyCallback(self.clickHandler)

        for page in os.listdir("pages") : #Load all the .json files to memory
            if page.endswith(".json") :
                with open(os.path.join("pages", page), "r") as f :
                    self.pages[page] = json.loads(f.read()) 

        requiredTags = ["images", "ticks", "dimensions", "created", "buttons"]

        for page in self.pages : #Load all the used images to memory
            for tag in requiredTags :
                if not tag in self.pages[page] :
                    self.error("Invalid\njson", f"Tag '{tag}' not found in {page}")

                    return None
            
            for image in self.pages[page]["images"] :
                if not image in self.images :
                    path = os.path.join("pages", "imgs", image)

                    if os.path.isfile(path) :
                        self.images[image] = Image.open(path)
                    else :
                        #print(f"{image} not found!")
                        self.images[image] = Image.new("RGB", (self.controller.buttonRes, self.controller.buttonRes))
            
            for tick in self.pages[page]["ticks"] : #Imports all the ticking files
                if tick.endswith(".py") :
                    name = tick[:-3]
                id = "t" + uuid.uuid4().hex[:12]
                
                #exec(f"global {id}") #Trying to import the module using diffrent methods
                #exec(f"import pages.ticks.{name} as {id}")

                #module = __import__(f"pages.ticks.{name}")
                #print(module)
                #globals()[id] = module

                try :
                    module = importlib.import_module(f"pages.ticks.{name}")
                    globals()[id] = module

                    self.ticks[tick] = id
                except Exception as e :
                    print(e)
                    pass


    def error(self, screenError, logError) : #Throws the stream deck into an error state.
        self.controller.resetScreen()

        self.tickingItems = {}

        self.controller.screen["0x0"].caption = screenError
        self.controller.screen["0x0"].fontColor = "black"
        self.controller.screen["0x0"].background = Image.new("RGB", (self.controller.buttonRes, self.controller.buttonRes), (255, 255, 255))
        self.controller.screen["1x0"].caption = "See log\nfor details"
        self.controller.screen["0x1"].caption = "Exit"
        self.controller.sendScreenToDevice()

        self.activePage = {"buttons":{"1x0": {"actions": {"openTxt":"errorLog.txt"}}, "0x1": {"actions": {"exit":""}}}}
        self.activePageName = "**error**"

        print(f"[ERROR] {logError}")

        try :
            with open("errorLog.txt", "a") as f :
                f.write(f"{logError}\n")
        except :
            if not logError == "Could not write to log." :
                self.error("I/O\nError", "Could not write to log.")
    
    def switchToPage(self, page) :
        if self.activePageName == "**error**" : #Make sure you can't switch the page when in error state. Doing so would probably break something
            return False

        if not page in self.pages :
            self.error("Page\nmissing", f"Could not find '{page}'")
            return False

        j = self.pages[page]
        buttons = j["buttons"]

        self.controller.resetScreen()
        #self.controller.coordsCaptions()
        
        self.activePage = j
        self.activePageName = page

        self.tickingItems = {}

        dimensions = f"{self.controller.width}x{self.controller.height}" #Detect pages for other stream deck layouts
        if not dimensions == j["dimensions"] :
            self.error("Invalid\nlayout.", f"Page '{page}' is in an invalid layout size for this Stream Deck '{self.controller.serial}'.")
            return False

        #self.controller.disableInput = True

        for button in buttons :
            buttonJ = buttons[button]

            if not buttonJ["background"] in self.images :
                self.error("Missing\nimage.", f"Image '{buttonJ['background']}' was not found. Please add the image to the 'images' list of '{page}'")
                return False

            try :
                key = self.controller.screen[button]
            except KeyError :
                self.error("Invalid\ncoords", f"Invalid coords '{button}'.")
                return False

            key.setCaption(buttonJ["caption"])
            key.background = self.images[buttonJ["background"]]
            key.fontSize = buttonJ["fontSize"]
            key.fontColor = buttonJ["color"]

            try :
                key.fontAlignment = buttonJ["fontAlignment"]
            except KeyError :
                key.fontAlignment = "center"

            if "ticks" in buttonJ :
                #self.tickingItems[button] = "hello"
                t = {}

                for tick in buttonJ["ticks"] :
                    t[tick] = {"action": buttonJ["ticks"][tick], "lastTrigger": 0, "nextTrigger": 0}
                
                self.tickingItems[button] = t
        
        #print(self.tickingItems)

        #self.tick()
        self.controller.sendScreenToDevice()
    
    def triggerAction(self, coords, action, actionData) :
        print(coords, action, actionData)

        if action == "switchPage" :
            self.switchToPage(actionData)
        elif action == "exit" :
            self.controller.deck.reset()
            self.controller.deck.close()
            os._exit(1)
        elif action == "setBrightness" :
            self.controller.deck.set_brightness(int(actionData))
        elif action == "showCoords" :
            self.controller.coordsCaptions(actionData)
            self.controller.sendScreenToDevice()
        elif action == "runCommand" :
            subprocess.call(str(actionData), shell=True, stderr=subprocess.DEVNULL)
        elif action == "screenshot" :
            self.controller.screenshot(actionData)
        elif action == "openTxt" : #Should only be used on the error screen.
            system = platform.system().lower()

            if system == 'windows' or system == 'darwin' :
                os.system(f"start {actionData}") #Windows or Mac OS
            else :
                subprocess.call(('xdg-open', actionData)) #Linux
        elif action == "keyboardType" :
            keyboard.write(actionData)
        elif action == "keyboardShortcut" :
            keyboard.send(actionData.lower())
        elif action == "openURL" :
            webbrowser.open(actionData)
        elif action == "randomColors" :
            self.controller.randomColors()
            self.controller.sendScreenToDevice()

    
    def tickKeyPress(self, coords, tickModule, tick) :
        try :
            tickModule.keyPress(coords, self.activePageName, self.controller.serial)
        except Exception as e :
            self.error("keyPress\nError.", f"keypress() in module {tick}: {e}")

    def clickHandler(self, deck, keyIndex, state) :
        x = (keyIndex % self.controller.width)
        y = math.ceil((keyIndex+1) / self.controller.width)-1
        coords = f"{x}x{y}"

        if self.controller.disableInput : #Input disabled, do not continue
            return

        self.controller.screen[coords].activated = state #Triggers the click 'animation'.
        self.controller.screen[coords].sendToDevice()


        if not state : #Wait until the button is released
            try :
                button = self.activePage["buttons"][coords]

                if coords in self.tickingItems : #Triggers tick function on ticking buttons
                    try :
                        ticks = self.tickingItems[coords]
                    except KeyError :
                        return
                    
                    for tick in ticks :
                        tickID = self.ticks[tick]

                        tickModule = globals()[tickID]
                        
                        thread = threading.Thread(target=self.tickKeyPress, args=(coords, tickModule, tick))
                        thread.start()
                        
                        #self.tickKeyPress(coords, tickModule, tick)
                        
                
                for action in button["actions"] :
                    actionData = button["actions"][action]

                    try :
                        self.triggerAction(coords, action, actionData)
                    except Exception as e :
                        self.error("Could not\ntrigger.", f"Could not trigger action '{action}' with action data '{actionData}', error: {e}")
                        return False


            except KeyError :
                pass

    def threadedTick(self, ticks, tickID, tick, action, button) :
        tickModule = globals()[tickID]

        #print("starting", tick, self.activePageName)
        startingPage = self.activePageName

        try :
            newState = tickModule.getKeyState(button, self.activePageName, self.controller.serial, action)
        except Exception as e :
            self.error("Ticks\nerror", f"Error in '{tick}'. Button: '{button}' Page: '{self.activePageName}' Serial: '{self.controller.serial}' Action: '{action}' Error: '{e}'")
            return False

        if not self.activePageName == startingPage :
            #print("interrupted", tick, self.activePageName, startingPage)
            return False

        #print("finished", tick, self.activePageName)

        key = self.controller.screen[button]

        if "caption" in newState :
            key.caption = newState["caption"]
                    
        if "background" in newState :
            key.background = newState["background"]
                    
        if "fontColor" in newState :
            key.fontColor = newState["fontColor"]

        if "fontSize" in newState :
            key.fontSize = newState["fontSize"]

        if "doNotUpdate" in newState :
            doNotUpdate = newState["doNotUpdate"]
        else :
            doNotUpdate = False
                    
        if len(newState["actions"]) > 0 :
            for action in newState["actions"] :
                actionData = newState["actions"][action]
                self.triggerAction(button, action, actionData)
                self.controller.sendScreenToDevice()
        else :
            if not doNotUpdate :
                key.sendToDevice()
                    
        try :
            wait = tickModule.nextTickWait(button, self.activePageName, self.controller.serial)
        except Exception as e :
            self.error("nextTickWait\nerror", f"nextTickWait() in {tick}: {e}")
        ticks[tick]["nextTrigger"] = time.time() + wait

    def tick(self) :
        startingTime = time.time()
        threads = {}

        for button in self.tickingItems :
            try :
                ticks = self.tickingItems[button]
            except KeyError :
                return False
            for tick in ticks :
                try :
                    tickID = self.ticks[tick]
                except KeyError :
                    self.error("Ticks file\nnot found.", f"The ticks file '{tick}' was not found. Please add it to the top of '{self.activePageName}'.")
                    return False

                action = ticks[tick]["action"]
                nextTrigger = ticks[tick]["nextTrigger"]

                if time.time() > nextTrigger :
                    #self.threadedTick(ticks, tickID, tick, action, button)
                    thread = threading.Thread(target=self.threadedTick, args=(ticks, tickID, tick, action, button))
                    threads[button] = thread

                    thread.start()
        
        for thread in threads.values() :
            thread.join()

        if (time.time() - startingTime) > 1 :
            self.error("Tick took\ntoo long", f"Tick took over a second ({round(time.time() - startingTime, 2)}s) to finish. Avoid doing time-expensive tasks in getKeyState()")
        
        #print(f"tick finished! {round(time.time() - startingTime, 2)}s")
                    
    
        #self.controller.disableInput = False


# ------------------------ #
def helloWorldTest() :
    streamdecks = DeviceManager().enumerate()
    for index, deck in enumerate(streamdecks) :

        c = controller(deck)

        middleKey = c.screen["2x2"]
        middleKey.loadImage("test.png")
        middleKey.setCaption("Hello,\nworld!")
        middleKey.setFont("C:\\Windows\\Fonts\\Arial.ttf", size=15, color="red")

        c.sendScreenToDevice()

        while True :
            time.sleep(10)

# ------------------------ #
           
if __name__ == "__main__" and False : #Disabled
    streamdecks = DeviceManager().enumerate()

    for index, deck in enumerate(streamdecks) :
        c = controller(deck, "C:\\Windows\\Fonts\\Arial.ttf")

        p = pages(c)
        p.switchToPage("welcome.json")

        while True :
            time.sleep(.5)
            p.tick()
