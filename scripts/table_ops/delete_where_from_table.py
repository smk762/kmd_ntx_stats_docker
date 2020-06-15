#!/usr/bin/env python3
import table_lib

conn = table_lib.connect_db()
cursor = conn.cursor()

#table = 'balances'
table = 'notarised'
#table = 'mined'
#table = 'mined_count_season'

cursor.execute("SELECT COUNT(*) FROM "+table+";")
print(cursor.fetchall())

cursor.execute("DELETE FROM "+table+" WHERE season = 'Season_4';")
conn.commit()

cursor.execute("SELECT COUNT(*) FROM "+table+";")
print(cursor.fetchall())

cursor.close()

conn.close()

