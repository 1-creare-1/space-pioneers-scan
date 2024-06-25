# https://console.aiven.io/account/a4c11fc8218d/project/sp-universe-map/services/sp-universe-db-01/overview
import multiprocessing
import threading
import time
import pprint
import psycopg2
import logging
import atexit
from keyboard import is_pressed

from image_getter import GetSystemPictures
from helpers import Focus
import extraction as extraction
import db

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(processName)s - %(levelname)s - %(message)s')

pp = pprint.PrettyPrinter(indent=1, depth=8, width=200)
db_conn = None

# Function to be called periodically
def enqueue(data, pool):
    # logging.debug(f"Enqueueing system: {data[2]}")
    try:
        pool.apply_async(process_data, args=(data,), callback=task_complete, error_callback=task_error)
    except Exception as e:
        logging.error(f"Error submitting task: {e}")

# Callback function for successful task completion
def task_complete(info):
    # logging.debug(f"Task completed successfully with result: {result}")
    ...

# Callback function for task errors
def task_error(error):
    # logging.error(f"Task encountered an error: {error}")
    ...

# Function that will process the data (executed by worker processes)
def process_data(data):
    # logging.debug(f"Processing data: {data}")
    # db_cursor, db_conn = init_db()
    star_picture, planet_pictures, system_id = data
    logging.debug(f"Processing system: {system_id}")
    info = extraction.ExtractSystemInfo(star_picture, planet_pictures, system_id)

    global db_conn
    cursor = db_conn.cursor()

    try:
        db.add_star(cursor, (
            int(info["id"]),  # id
            info["name"],  # name
            info["type"],  # star type
            int(info["mass"] * 1),  # mass
            int(info["planet_count"]),  # planet count
        ))

        for planet in info['planets']:
            colors = []
            for color in planet["colors"]:
                colors.append(color)
                colors.append(color)
                colors.append(color)

            db.add_planet(cursor, (
                int(planet["id"]),  # planet id
                int(info["id"]),  # star id
                planet["name"],  # name
                int(planet["radius"] * 1),  # radius
                int(planet["surface_gravity"] * 1),  # surface gravity
                planet["tectonics"].value,  # tectonics
                planet["atmosphere"].value,  # atmosphere
                planet["oceans"].value,  # oceans
                planet["life"],  # life
                int(planet["moons"]),  # moons
                colors,  # colors
            ))

        db_conn.commit()
        logging.debug(f"Completed system: {system_id}")
    except psycopg2.Error as e:
        logging.error(f"Database error: {e}")
        db_conn.rollback()
    except Exception as e:
        logging.error(f"Processing error: {e}")
    finally:
        cursor.close()
    # return info
    # return 'success'
    return None

# Timer function to call enqueue(data)
def start_scanner(pool):
    def inner():
        start_time = time.time()
        # start = 5001
        # end = 5100
        start = 1
        end = 5100
        run = True
        system_id = start
        if run:
            Focus("roblox")
            time.sleep(0.2)
        toggle_pressed_last_frame = False
        while system_id <= end:
            if is_pressed('pause'):
                if not toggle_pressed_last_frame:
                    run = not run
                    if run:
                        logging.log(0, "Macro Resumed")
                        run = True
                        Focus("roblox")
                        time.sleep(0.2)
                    else:
                        logging.log(0, "Macro Paused")
                toggle_pressed_last_frame = True
            else:
                toggle_pressed_last_frame = False

            if run == False:
                time.sleep(0.01)
                continue

            star_picture, planet_pictures = GetSystemPictures(system_id)
            enqueue((star_picture, planet_pictures, system_id), pool)

            system_id += 1

        end_time = time.time()
        print(f"Took {end_time - start_time} seconds to scan {end - start + 1} systems")

        # system_id = 5027
        # star_picture, planet_pictures = GetSystemPictures(system_id)
        # enqueue((star_picture, planet_pictures, system_id), pool)

        Focus("code")
    thread = threading.Thread(target=inner)
    thread.daemon = True  # This ensures the thread will exit when the main program exits
    thread.start()

def close_db_connection():
    global db_conn
    if db_conn:
        db_conn.close()
        db_conn = None

def init_worker(db_path):
    global db_conn
    db_conn = db.get_conn(db_path)
    atexit.register(close_db_connection)



def main():
    logging.debug("Initializing multiprocessing pool")
    # Create a pool of worker processes
    db_path = db.get_db_url()
    pool = multiprocessing.Pool(processes=12, initializer=init_worker, initargs=(db_path,))

    # Start the periodic enqueueing of starmap pictures
    start_scanner(pool)

    # Keep the main thread alive to allow the background processes to run
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logging.debug("Stopping...")
        pool.terminate()
        pool.join()

if __name__ == '__main__':
    init_db_conn = db.get_conn()
    init_db_cursor = init_db_conn.cursor()
    db.create_schema(init_db_cursor)
    init_db_conn.commit()
    init_db_conn.close()

    main()