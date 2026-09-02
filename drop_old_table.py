"""Drop old appareils table so it gets recreated with new schema."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from database.connection import get_connection

conn = get_connection()
conn.autocommit = True
cursor = conn.cursor()
cursor.execute("IF EXISTS (SELECT * FROM sys.tables WHERE name = 'appareils') DROP TABLE appareils")
print("Table 'appareils' dropped (will be recreated on next run)")
cursor.close()
conn.close()
