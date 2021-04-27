#!/usr/bin/env python3
import table_lib

conn = table_lib.connect_db()
cursor = conn.cursor()

sql = "UPDATE notarised SET chain = 'GLEEC-OLD' WHERE chain = 'GLEEC' and server = 'Third_Party';"
cursor.execute(sql)
conn.commit()


cursor.close()

conn.close()
