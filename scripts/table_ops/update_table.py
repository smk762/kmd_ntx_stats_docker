#!/usr/bin/env python3
import table_lib

conn = table_lib.connect_db()
cursor = conn.cursor()

sql = "UPDATE mined SET season = 'Season_3' WHERE address = 'Season_4';"
cursor.execute(sql)
conn.commit()


cursor.close()

conn.close()
