#!/usr/bin/env python3
import table_lib

conn = table_lib.connect_db()
cursor = conn.cursor()

tables = ['notarised', 'last_notarised' ,'notarised_tenure', 
          'notarised_chain_season' ,'notarised_chain_daily']

for table in tables:
    cursor.execute("SELECT COUNT(*) FROM "+table+";")
    print(cursor.fetchall())

    cursor.execute("DELETE FROM "+table+" WHERE chain = 'KMD';")
    conn.commit()

    cursor.execute("SELECT COUNT(*) FROM "+table+";")
    print(cursor.fetchall())

cursor.close()

conn.close()

