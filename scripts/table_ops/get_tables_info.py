
#!/usr/bin/env python3
import table_lib

conn = table_lib.connect_db()
cursor = conn.cursor()

table_list = table_lib.get_table_names(cursor)

for table in table_list:
    rowcount = table_lib.get_count_from_table(cursor, table, '*')
    print(table+" rows: "+str(rowcount))


cursor.close()

conn.close()

