#!/usr/bin/env python3
import table_lib

conn = table_lib.connect_db()
cursor = conn.cursor()

#table = 'balances'
table = 'mined_count_daily'


cursor.execute("SELECT COUNT(*) FROM "+table+";")
print(cursor.fetchall())

cursor.execute("TRUNCATE "+table+";")
conn.commit()

cursor.execute("SELECT COUNT(*) FROM "+table+";")
print(cursor.fetchall())

cursor.close()

conn.close()

