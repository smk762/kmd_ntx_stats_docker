#!/usr/bin/env python3
import table_lib

conn = table_lib.connect_db()
cursor = conn.cursor()
for chain in ["LTC","BTC","KMD"]:
    sql = f"UPDATE notarised SET epoch = '{chain}', server = '{chain}' WHERE chain = '{chain}';"
    print(sql)
    cursor.execute(sql)
    conn.commit()


cursor.close()

conn.close()
