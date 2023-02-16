#!/usr/bin/env python3
import os
import psycopg2
import datetime
import mysql.connector 
import json
from dotenv import load_dotenv

load_dotenv()

def connect_db():
    try:
        conn = psycopg2.connect(
            host=os.getenv("POSTGRES_HOST"),
            user=os.getenv("POSTGRES_USER"),
            password=os.getenv("POSTGRES_PASSWORD"),
            port = "5432",
            database='postgres'
        )
    except:
        conn = psycopg2.connect(
            host='localhost',
            user=os.getenv("POSTGRES_USER"),
            password=os.getenv("POSTGRES_PASSWORD"),
            port = "7654",
            database='postgres'
        )

    return conn

CONN = connect_db()
CURSOR = CONN.cursor()


def get_table_names(cursor):
    sql = "SELECT tablename FROM pg_catalog.pg_tables \
           WHERE schemaname != 'pg_catalog' \
           AND schemaname != 'information_schema';"
    cursor.execute(sql)
    tables = cursor.fetchall()
    tables_list = []
    for table in tables:
        tables_list.append(table[0])
    return tables_list


try:
    ext_mydb = mysql.connector.connect(
      host=os.getenv("ext_hostname"),
      user=os.getenv("ext_username"),
      passwd=os.getenv("ext_password"),
      database=os.getenv("ext_db")
    )
    ext_cursor = ext_mydb.cursor()
except:
    pass

