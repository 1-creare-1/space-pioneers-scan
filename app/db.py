import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def get_db_url():
    return os.environ["POSTGRES_URL"]

def get_conn(url=None):
    if url == None:
        url = get_db_url()
    return psycopg2.connect(url)

# def init(url):
#     # conn = psycopg2.connect({
#     #     'dbname': os.environ['POSTGRES_NAME'],
#     #     'user': os.environ['POSTGRES_USER'],
#     #     'password': os.environ['POSTGRES_PASSWORD'],
#     #     'port': os.environ['POSTGRES_PORT'],
#     #     'host': os.environ['POSTGRES_HOST']
#     # })
#     conn = psycopg2.connect(url)

#     cursor = conn.cursor()
#     return cursor, conn

# Define Database Schema
def create_schema(cursor):
    cursor.execute('''
    -- Create stars table
    CREATE TABLE IF NOT EXISTS stars (
        id INT UNIQUE PRIMARY KEY,  -- Unique identifier for the star
        name TEXT NOT NULL,  -- Name of the star
        type TEXT NOT NULL,  -- Type of the star (assuming string type)
        mass INT NOT NULL,  -- Mass of the star (100x real mass)
        planet_count INT DEFAULT 0  -- Number of planets orbiting the star, default 0
    );

    CREATE TABLE IF NOT EXISTS planets (
        id INT NOT NULL,  -- identifier for the planet
        star_id INT REFERENCES stars(id) ON DELETE CASCADE,  -- Reference to the star it orbits
        name TEXT NOT NULL,  -- Name of the planet
        radius INT,  -- (100x real value) Radius of the planet
        surface_gravity INT,  -- (100x real value) Surface gravity of the planet
        tectonics INT,  -- Tectonics (references enum in python)
        atmosphere INT,  -- Atmosphere (references enum in python)
        oceans INT,  -- Oceans (references enum in python)
        life BOOLEAN,  -- Presence of life (true/false)
        moons INT,  -- Number of moons
        colors INT[],  -- List of colors (array of groups of 3 0-255 values)
                   
        PRIMARY KEY (id, star_id)  -- Composite primary key
    );

    -- Unique constraint to ensure planet uniqueness by id and star_id combination
    CREATE UNIQUE INDEX IF NOT EXISTS planet_unique_idx ON planets (id, star_id);
    ''')

def add_star(cursor, data):
    """Insert a new star into the database."""
    sql = """
        INSERT INTO stars (id, name, type, mass, planet_count)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (id) DO UPDATE
        SET name = EXCLUDED.name,
            type = EXCLUDED.type,
            mass = EXCLUDED.mass,
            planet_count = EXCLUDED.planet_count
    """
    cursor.execute(sql, data)

def add_planet(cursor, data):
    """Insert or update a planet for a specific star."""
    sql = """
        INSERT INTO planets (id, star_id, name, radius, surface_gravity, tectonics, atmosphere, oceans, life, moons, colors)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (id, star_id) DO UPDATE
        SET name = EXCLUDED.name,
            radius = EXCLUDED.radius,
            surface_gravity = EXCLUDED.surface_gravity,
            tectonics = EXCLUDED.tectonics,
            atmosphere = EXCLUDED.atmosphere,
            oceans = EXCLUDED.oceans,
            life = EXCLUDED.life,
            moons = EXCLUDED.moons,
            colors = EXCLUDED.colors
    """
    cursor.execute(sql, data)

# Star: (id, name, star_type, mass, planet_count)
# Planet: (planet_id, star_id, name, radius, surface_gravity, tectonics, atmosphere, oceans, life, moons, colors)
# def add_system(star, planets):
#     try:
#         # Add star and planets
#         add_star(db_cursor, star)
#         for planet in planets:
#             add_planet(db_cursor, planet)

#         # Commit the transaction
#         db_conn.commit()

#     except psycopg2.Error as e:
#         print(f"Error: {e}")
#         db_conn.rollback()