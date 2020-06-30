#!/usr/bin/env python3
import table_lib

conn = table_lib.connect_db()
cursor = conn.cursor()

table_list = table_lib.get_table_names(cursor)

for table in table_list:

  cursor.execute("SELECT COUNT(*) FROM "+table+";")
  print(cursor.fetchall())

  cursor.execute("DROP "+table+";")
  conn.commit()

  cursor.execute("SELECT COUNT(*) FROM "+table+";")
  print(cursor.fetchall())

cursor.close()

conn.close()

