import time

from image_getter import GetSystemPictures
from helpers import Focus
import extraction as extraction


Focus("roblox")
time.sleep(0.2)

start_time = time.time()
for system_id in range(1, 10):
    star_picture, planet_pictures = GetSystemPictures(system_id)
    info = extraction.ExtractSystemInfo(star_picture, planet_pictures, system_id)
end_time = time.time()
print(f"Took {end_time - start_time} seconds to scan 10 planets")

# system_id = 9
# star_picture, planet_pictures = GetSystemPictures(system_id)
# enqueue((star_picture, planet_pictures, system_id), pool)

Focus("code")