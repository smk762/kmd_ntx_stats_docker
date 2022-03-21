import os
import psycopg2
import datetime
import mysql.connector 
import json
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

ext_mydb = mysql.connector.connect(
  host=os.getenv("ext_hostname"),
  user=os.getenv("ext_username"),
  passwd=os.getenv("ext_password"),
  database=os.getenv("ext_db")
)
ext_cursor = ext_mydb.cursor()

