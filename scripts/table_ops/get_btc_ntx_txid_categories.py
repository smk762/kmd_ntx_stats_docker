#!/usr/bin/env python3
import table_lib

conn = table_lib.connect_db()
cursor = conn.cursor()

table = 'nn_btc_tx'


cursor.execute(f"SELECT COUNT(*) FROM {table};")
print(cursor.fetchall())

cursor.execute(f"SELECT DISTINCT category FROM {table};")
cats = cursor.fetchall()

for cat in cats:
    cursor.execute(f"SELECT COUNT(*) FROM {table} where category='{cat[0]}';")
    count = cursor.fetchone()

    print(f"{cat[0]}: {count[0]}")

cursor.close()

conn.close()


