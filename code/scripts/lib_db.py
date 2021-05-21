import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def connect_db():
    conn = psycopg2.connect(
        host='localhost',
        user=os.getenv("DB_USER"),
        password=os.getenv("PASSWORD"),
        port = "7654",
        database='postgres'
    )
    return conn

CONN = connect_db()
CURSOR = CONN.cursor()