import psycopg2
import os
from dotenv import load_dotenv
from tabulate import tabulate

load_dotenv()


conn = psycopg2.connect(os.environ["POSTGRES_URL"])
cursor = conn.cursor()

QUERY_ALL_PLANETS = '''
SELECT p.id, p.star_id, p.name, p.radius, p.surface_gravity, p.tectonics, p.atmosphere, p.oceans, p.life, p.moons--, p.colors
FROM Planets p
JOIN stars s ON p.star_id = s.id
--WHERE s.id = 1;
'''

QUERY_GOOD_PLANETS = '''
SELECT p.id, p.star_id, p.name, p.radius, p.surface_gravity, p.tectonics, p.atmosphere, p.oceans, p.life, p.moons--, p.colors
FROM Planets p
JOIN stars s ON p.star_id = s.id
WHERE p.surface_gravity >= 120 AND p.life = True AND p.id = 1 AND p.atmosphere = 1 AND p.moons > 0;
'''

COUNT = 'SELECT count(*) AS count FROM Stars;'

DELETE_DB = '''
DROP TABLE
   Planets,
   Stars
'''

try:
    cursor.execute(COUNT)
    conn.commit()
except psycopg2.Error as e:
    print(f"Failed to execute query {e}")
    conn.rollback()
except Exception as e:
    print(f"Error: {e}")

try:
    rows = cursor.fetchall()
    colnames = [desc[0] for desc in cursor.description]
    print(tabulate(rows, headers=colnames, tablefmt='grid'))
except Exception as e:
    print(f"Failed to fetch rows: {e}")

conn.close()
cursor.close()