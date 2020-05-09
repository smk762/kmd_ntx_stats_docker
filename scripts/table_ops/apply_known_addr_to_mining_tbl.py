#!/usr/bin/env python3
import table_lib
from address_lib import known_addresses

conn = table_lib.connect_db()
cursor = conn.cursor()

for address in known_addresses:
    print("Updating "+address+" to "+str(known_addresses[address]))
    sql = "UPDATE mined SET name = '"+known_addresses[address]+"' WHERE address = '"+address+"';"
    cursor.execute(sql)
    conn.commit()


cursor.close()

conn.close()
