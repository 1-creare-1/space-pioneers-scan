import starmap_types
from PIL import Image
import PIL.ImageOps
import re
from pytesseract import pytesseract 
import time
import numpy as np
from positions import *
from helpers import *

# Defining paths to tesseract.exe 
# and the image we would be using 
path_to_tesseract = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
# Providing the tesseract executable 
# location to pytesseract library 
pytesseract.tesseract_cmd = path_to_tesseract 

def ExtractText(img: Image, crop_zones=None):  
    img = PIL.ImageOps.invert(img)
    # Text should be black and background should be white
    # data = np.array(img)
    # converted = np.where(data > 60, 0, 255)
    # img = Image.fromarray(converted.astype('uint8'))

   # img.save(f"Text Extraction {round(time.time()*100)}.png")
    
    # Passing the image object to image_to_string() function 
    # This function will extract the text from the image
    if crop_zones == None:
        config = "--oem 3 -c tessedit_char_whitelist=\"0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ&: \""
        user_patterns = "./patterns.txt"
        a = "--user-patterns {user_patterns}"
        # config = f"--oem 2 --user-patterns user-patterns"
        try:
            text = pytesseract.image_to_string(img, config=config, timeout=1)
        except Exception as e:
            logging.warn(e)
    else:
        for zone in crop_zones:
            ...

    # Display extracted text
    # print("-- EXTRACTION BELOW --")
    # print(text)
    # print("-- END EXTRACTION --")
    return text


def ExtractPlanetInfo(img: Image, index: int):
    planet_pos = add_tupples(FIRST_PLANET_LOCATION, (PLANET_X_OFFSET * index, 0))
    selection_point = add_tupples(planet_pos, (0, -PLANET_SELECTION_INDICATOR_Y_OFFSET))

    # Find planet colors
    left = planet_pos[0] - PLANET_IMAGE_SIZE[0] / 2
    right = planet_pos[0] + PLANET_IMAGE_SIZE[0] / 2
    top = planet_pos[1] - PLANET_IMAGE_SIZE[1] / 2
    bottom = planet_pos[1] + PLANET_IMAGE_SIZE[1] / 2
    planet_img = img.crop((left, top, right, bottom))
    # planet_img.save(f"planet {index}.png")
    # planet_img.show()
    colors = get_dominant_colors(planet_img, 16, 4)

    planet_crop_zones = [
        #(left, top, right, bottom), char list, oem (default 3)
        ((0,   0,323,32), "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ "), # Planet Name
        ((100,34,323,54), "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ&"), # Radius
        ((0,0,323,32), "0123456789x"), # Gravity
        ((0,0,323,32), "0123456789", 10), # Tectonics
        ((0,0,323,32), "0123456789."), # Atmosphere
        ((0,0,323,32), "0123456789."), # Oceans
        ((0,0,323,32), "0123456789."), # Life
        ((0,0,323,32), "0123456789", 10), # Moons
    ]

    planet_info_img = img.crop(PLANET_INFO_CROP)
    txt = ExtractText(planet_info_img)
    # planet_info_img.save(f"planet {index} info.png")

    return {
        "id": index+1,
        "colors": colors,

        "name": re.findall(r".*?\n", txt)[0].replace("\n", ""),
        "radius": StripToNumber(ExtractValue(txt, "Radius")),
        "surface_gravity": StripToNumber(ExtractValue(txt, "Surface Gravity")),
        "tectonics": StripToEnum(ExtractValue(txt, "Tectonics"), starmap_types.Tectonics),
        "atmosphere": StripToEnum(ExtractValue(txt, "Atmosphere"), starmap_types.Atmosphere),
        "oceans": StripToEnum(ExtractValue(txt, "Oceans"), starmap_types.Ocean),
        "life": StripToBool(ExtractValue(txt, "Has Life")),
        "moons": StripToNumber(ExtractValue(txt, "Moons")),
    }


def ExtractSystemInfo(star_img: Image, planet_imgs, system_id: int):
    star_crop_zones = [
        #(left, top, right, bottom), char list, oem (default 3)
        ((0,   0,323,32), "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ "), # Star Name
        ((100,34,323,54), "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ&"), # Spectral Type
        ((0,0,323,32), "0123456789x"), # Mass
        ((0,0,323,32), "0123456789", 10), # Planets
        ((0,0,323,32), "0123456789."), # Distance
    ]
        
    txt = ExtractText(star_img)
    # star_img.save(f"star info.png")

    system = {
        "planets": [],
        "id": system_id,

        "name": re.findall(r".*?\n", txt)[0].replace("\n", ""),
        "type": ExtractValue(txt, "Spectral Type"),
        "mass": StripToNumber(ExtractValue(txt, "Mass")),
        "planet_count": StripToNumber(ExtractValue(txt, "Planets")),
    }

    for i, planet_img in enumerate(planet_imgs):
        system["planets"].append(ExtractPlanetInfo(planet_img, i))
    
    return system