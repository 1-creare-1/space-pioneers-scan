import starmap_types
from PIL import ImageGrab, Image
import win32gui
import re
import pprint
import enum
import pyautogui
import pydirectinput
from pytesseract import pytesseract 
import pyperclip
import time

pp = pprint.PrettyPrinter(indent=1, depth=8, width=200)

# Defining paths to tesseract.exe 
# and the image we would be using 
path_to_tesseract = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


COORDS_BOX_LOCATION = (450, 180)
FIRST_PLANET_LOCATION = (735, 858)
PLANET_X_OFFSET = 100 # maybe 200?
PLANET_SELECTION_INDICATOR_Y_OFFSET = 51 # ypos: 807
PLANET_IMAGE_SIZE = (80,80)

def hotkey(*argv):
    for arg in argv:
        pydirectinput.keyDown(arg)
    time.sleep(0.01)
    for arg in argv:
        pydirectinput.keyUp(arg)

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

def GetScreencapture(window_name: str)->Image:
    hwid = Focus(window_name)[0]   
    bbox = win32gui.GetWindowRect(hwid)
    img = ImageGrab.grab(bbox)
    return img


def ExtractText(img: Image):  
    # Providing the tesseract executable 
    # location to pytesseract library 
    pytesseract.tesseract_cmd = path_to_tesseract 
    
    # Passing the image object to image_to_string() function 
    # This function will extract the text from the image 
    text = pytesseract.image_to_string(img)
    
    # Displaying the extracted text 
    # print(text[:-1])
    # return text[:-1]
    return text

def ExtractValue(text: str, key: str):
    # index = text.find(key)
    match = re.search(f"{key}.*?\n", text)
    if match == None:
        print(f"ERROR: Couldn't find \"{key}\" in text")
        return None
    span = match.span()
    return text[span[0]+len(key):span[1]-1]


def StripToNumber(text: str):
    # TODO: Fix me parsing bad
    if text == None:
        return None
    text = re.sub("[^0-9.]", "", text)
    dot = re.search("\.", text)
    if dot:
        text = re.sub("\.", "", text[dot.span()[1]:-1])
    return float(text)

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
    for v in enum:
        # print(f"Comparing {v.name.lower()} with {text}")
        if v.name.lower() == text:
            return v
        
    print(f"Couldn't find {text} in {enum}")
    return None

def QueryPlanet(index: int):
    # TODO: Click planet
    # img = Image.open("./image.png")

    planet_pos = add_tupples(FIRST_PLANET_LOCATION, (PLANET_X_OFFSET * index, 0))
    selection_point = add_tupples(planet_pos, (0, PLANET_SELECTION_INDICATOR_Y_OFFSET))

    pydirectinput.click(planet_pos[0], planet_pos[1], 2)

    img = GetScreencapture("roblox")

    # Check if theres a planet here
    px = img.getpixel(selection_point)
    print(px)
    brightness = (px[0] + px[1] + px[2]) / 3 / 255
    print(selection_point)
    print(brightness)
    img.save(f"planet {index}.png")
    if brightness < 0.2:
        return None
    
    # Find planet colors
    left = planet_pos[0] - PLANET_IMAGE_SIZE[0] / 2
    right = planet_pos[0] + PLANET_IMAGE_SIZE[0] / 2
    top = planet_pos[1] - PLANET_IMAGE_SIZE[1] / 2
    bottom = planet_pos[1] + PLANET_IMAGE_SIZE[1] / 2
    planet_img = img.crop((left, top, right, bottom))
    # planet_img.show()
    colors = get_dominant_colors(planet_img, 16, 4)

    txt = ExtractText(img)

    return {
        "id": index,
        "colors": colors,

        "radius": StripToNumber(ExtractValue(txt, "Radius: ")),
        "surface_gravity": StripToNumber(ExtractValue(txt, "Surface Gravity: ")),
        "tectonics": StripToEnum(ExtractValue(txt, "Tectonics: "), starmap_types.Tectonics),
        "atmosphere": StripToEnum(ExtractValue(txt, "Atmosphere: "), starmap_types.Atmosphere),
        "oceans": StripToBool(ExtractValue(txt, "Has Life: ")),
        "life": True,
        "Moons": StripToNumber(ExtractValue(txt, "Moons: ")),
    }



def GetSystemInformation(system_id: int):
    pydirectinput.click(COORDS_BOX_LOCATION[0], COORDS_BOX_LOCATION[1], 2)
    hotkey('ctrl', 'a')
    pyperclip.copy(system_id)
    hotkey('ctrl', 'v')
    pydirectinput.press("return")
    # TODO: Enter system id
    # img = Image.open("./image.png")
    img = GetScreencapture("roblox")
    txt = ExtractText(img)
    # print(txt)
    # img.show()

    system = {
        "planets": [],
        "id": system_id,

        "type": ExtractValue(txt, "Spectral Type: "),
        "mass": StripToNumber(ExtractValue(txt, "Mass: ")),
        "planet_count": StripToNumber(ExtractValue(txt, "Planets: ")),
    }

    planet_id = 0
    while True:
        planet = QueryPlanet(planet_id)
        if planet == None:
            break
        system["planets"].append(planet)
        planet_id += 1

    return system


Focus("roblox")
info = GetSystemInformation(9)
pp.pprint(info)
Focus("code")