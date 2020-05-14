#!/usr/bin/env python3
import table_lib

conn = table_lib.connect_db()
cursor = conn.cursor()

#table = 'balances'
table = 'notarised'

cursor.execute("SELECT COUNT(*) FROM "+table+";")
print(cursor.fetchall())


cursor.execute("DELETE FROM "+table+" WHERE chain = 'low_vin';")
conn.commit()

cursor.execute("DELETE FROM "+table+" WHERE chain = 'not_dest';")
conn.commit()

cursor.execute("DELETE FROM "+table+" WHERE chain = 'not_opret';")
conn.commit()

cursor.execute("DELETE FROM "+table+" WHERE NOT UPPER(chain) = chain;")
conn.commit()


cursor.execute("SELECT COUNT(*) FROM "+table+";")
print(cursor.fetchall())

cursor.close()

conn.close()

