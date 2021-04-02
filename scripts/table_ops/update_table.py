#!/usr/bin/env python3
import table_lib

conn = table_lib.connect_db()
cursor = conn.cursor()

sql = "UPDATE notarised SET server = 'Main' WHERE season = 'Season_5_Testnet';"
cursor.execute(sql)
conn.commit()


cursor.close()

conn.close()
