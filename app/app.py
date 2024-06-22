import multiprocessing
import threading
import time
import pprint

from image_getter import GetSystemPictures
from helpers import Focus
import extraction as extraction

pp = pprint.PrettyPrinter(indent=1, depth=8, width=200)

# Function to be called periodically
def enqueue(data, pool):
    # print(f"Enqueueing system: {data[2]}")
    pool.apply_async(process_data, args=(data,))

# Function that will process the data (executed by worker threads)
def process_data(data):
    star_picture, planet_pictures, system_id = data
    print(f"Processing system: {system_id}")
    info = extraction.ExtractSystemInfo(star_picture, planet_pictures, system_id)
    print(f"Completed system: {system_id}")
    # pp.pprint(info)
    return info

# Timer function to call enqueue(data)
def start_scanner(pool):
    def inner():
        Focus("roblox")
        time.sleep(0.2)

        # start_time = time.time()
        # scan_count = 50
        # for system_id in range(1, scan_count):
        #     star_picture, planet_pictures = GetSystemPictures(system_id)
        #     enqueue((star_picture, planet_pictures, system_id), pool)
        # end_time = time.time()
        # print(f"Took {end_time - start_time} seconds to scan {scan_count} systems")

        system_id = 34
        star_picture, planet_pictures = GetSystemPictures(system_id)
        enqueue((star_picture, planet_pictures, system_id), pool)

        Focus("code")
    thread = threading.Thread(target=inner)
    thread.daemon = True  # This ensures the thread will exit when the main program exits
    thread.start()

def main():
    # Create a pool of worker threads
    pool = multiprocessing.Pool(processes=4)  # Adjust the number of processes as needed

    # Start the periodic enqueueing of starmap pictures
    start_scanner(pool)

    # Keep the main thread alive to allow the background thread to run
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Stopping...")
        pool.terminate()
        pool.join()

if __name__ == '__main__':
    main()