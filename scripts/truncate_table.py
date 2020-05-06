#!/usr/bin/env python3
import psycopg2

conn = psycopg2.connect(
  host='localhost',
  user='postgres',
  password='postgres',
  port = "7654",
  database='postgres'
)
cursor = conn.cursor()

table = 'mined_count'

cursor.execute("SELECT COUNT(*) FROM "+table+";")
print(cursor.fetchall())

cursor.execute("TRUNCATE "+table+";")
conn.commit()

cursor.execute("SELECT COUNT(*) FROM "+table+";")
print(cursor.fetchall())

cursor.close()

conn.close()

