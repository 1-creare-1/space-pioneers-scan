from PIL import ImageGrab, Image
import win32gui
import re
import enum
import pydirectinput
import time
from fuzzywuzzy import fuzz

pydirectinput.PAUSE = 0

def hotkey(*argv):
    for arg in argv:
        pydirectinput.keyDown(arg)
    time.sleep(0.01)
    for arg in argv:
        pydirectinput.keyUp(arg)

def click(pos, clicks=1):
    pydirectinput.moveTo(pos[0], pos[1])
    # pydirectinput.click(planet_pos[0], planet_pos[1])
    pydirectinput.moveTo(pos[0], pos[1]+1)
    pydirectinput.click(pos[0], pos[1], clicks, 0.01)

def add_tupples(a, b):
    if len(a) != len(b):
        print("Can't do tupples of diff sizes")

    new = []
    i = 0
    for v1 in a:
        new.append(v1 + b[i])
        i += 1
    return tuple(new)

def get_dominant_colors(img, palette_size=16, num_colors=10):
    # Reduce colors (uses k-means internally)
    paletted = img.convert('P', palette=Image.ADAPTIVE, colors=palette_size)
    # Find the color that occurs most often
    palette = paletted.getpalette()
    color_counts = sorted(paletted.getcolors(), reverse=True)

    dominant_colors = []
    for i in range(num_colors):
      palette_index = color_counts[i][1]
      dominant_colors.append(palette[palette_index*3:palette_index*3+3])

    return dominant_colors

def GetWindowHandle(window_name: str):
    toplist, winlist = [], []
    def enum_cb(hwnd, results):
        winlist.append((hwnd, win32gui.GetWindowText(hwnd)))
    win32gui.EnumWindows(enum_cb, toplist)

    # just grab the hwnd for first window matching firefox
    window = [(hwnd, title) for hwnd, title in winlist if window_name in title.lower()][0]
    return window

def Focus(window_name: str):
    window = GetWindowHandle(window_name)
    win32gui.SetForegroundWindow(window[0])
    return window

def GetScreenshot()->Image:
    hwid = Focus("roblox")[0]   
    bbox = win32gui.GetWindowRect(hwid)
    img = ImageGrab.grab(bbox)
    return img


def ExtractValue(text: str, key: str):
    # index = text.find(key)
    match = re.search(f"{key}.*?\n", text)
    if match == None:
        print(f"ERROR: Couldn't find \"{key}\" in text")
        return None
    span = match.span()
    return text[span[0]+len(key):span[1]-1]


def StripToNumber(raw_text: str):
    # TODO: Fix me parsing bad
    if raw_text == None:
        return None
    text = re.sub(r"[^0-9.]", "", raw_text)
    dot = re.search(r"\.", text)
    if dot:
        dot_char = dot.span()[1]
        text = text[0:dot_char] + re.sub(r"\.", "", text[dot_char:])

    try:
        return float(text)
    except Exception as e:
        print(f"Couldn't parse {text} (raw: {raw_text}) as float with error: {e}")
    return None

def StripToBool(text: str):
    if text == None:
        return None
    text = re.sub("[^a-z]", "", text.lower())
    if "yes" in text:
        return True
    elif "no" in text:
        return False
    return None

def StripToEnum(text: str, enum: enum.Enum):
    if text == None:
        return None
    text = re.sub("[^a-z]", "", text.lower())
    best_match = None
    best_accuracy = -1
    for v in enum:
        # print(f"Comparing {v.name.lower()} with {text}")
        accuracy = fuzz.ratio(v.name.lower(), text)
        if accuracy == 100:
            return v
        if accuracy > best_accuracy:
            best_accuracy = accuracy
            best_match = v
    
    if best_match != None and accuracy > 50:
        print(f"Couldn't find {text} in {enum} Falling back to {best_match} with accuracy of {best_accuracy}")
        return best_match
    
    print(f"Couldn't find {text} in {enum}")
    return None