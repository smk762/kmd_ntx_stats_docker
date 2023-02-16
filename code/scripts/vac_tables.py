#!/usr/bin/env python3
import lib_db

conn = lib_db.connect_db()
cursor = conn.cursor()
conn.set_session(autocommit=True)

table_list = lib_db.get_table_names(cursor)

for table in table_list:
    try:
        sql = f"VACUUM FULL {table};"
        cursor.execute(sql)
    except:
        pass

cursor.close()
conn.close()

