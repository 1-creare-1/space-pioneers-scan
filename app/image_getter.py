import pydirectinput
import pyperclip
from helpers import add_tupples, click, GetScreenshot, hotkey
from positions import *

pydirectinput.PAUSE = 0

def GetPlanetPicture(index: int):
    planet_pos = add_tupples(FIRST_PLANET_LOCATION, (PLANET_X_OFFSET * index, 0))
    selection_point = add_tupples(planet_pos, (0, -PLANET_SELECTION_INDICATOR_Y_OFFSET))

    # Only select planet if its not already selected
    if index != 0:
        click(planet_pos)

    img = GetScreenshot()

    # Check if theres a planet here
    px = img.getpixel(selection_point)
    brightness = (px[0] + px[1] + px[2]) / 3 / 255
    if brightness < 0.2:
        return None

    return img

def GetSystemPictures(system_id: int):
    # Select this system
    click(COORDS_BOX_LOCATION, 3)
    pyperclip.copy(system_id)
    hotkey('ctrl', 'v')
    pydirectinput.press("return")

    star_picture = GetScreenshot().crop(STAR_INFO_CROP)
    planet_pictures = []
    i = 0
    while True:
        planet_picture = GetPlanetPicture(i)
        if planet_picture:
            planet_pictures.append(planet_picture)
        else:
            break
        i += 1
    
    return star_picture, planet_pictures