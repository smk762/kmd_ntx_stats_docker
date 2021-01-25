#!/usr/bin/env python3
import table_lib

conn = table_lib.connect_db()
cursor = conn.cursor()

table_list = table_lib.get_table_names(cursor)

for table in table_list:
    constraints = table_lib.get_constraints_from_table(cursor, table)
    print(table+" constraints:\n "+str(constraints)+"\n\n")


cursor.close()

conn.close()

