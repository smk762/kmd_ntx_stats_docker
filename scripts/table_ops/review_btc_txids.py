#!/usr/bin/env python3
import table_lib

conn = table_lib.connect_db()
cursor = conn.cursor()

table = 'nn_btc_tx'

for category in ['NTX', "Split or Consolidate", "Sent", "Received"]:
    print("== "+category+" ==")
    cursor.execute("SELECT * FROM "+table+" WHERE category = '"+category+"';")
    results = cursor.fetchone()
    print(results)
    results = cursor.fetchall()
    print(len(results))

cursor.close()

conn.close()


