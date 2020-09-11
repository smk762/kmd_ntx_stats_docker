#!/usr/bin/env python3
import table_lib

conn = table_lib.connect_db()
cursor = conn.cursor()

table = 'nn_btc_tx'

cursor.execute("SELECT * FROM "+table+";")
results = cursor.fetchall()
print(str(len(results))+" rows")

cursor.execute("SELECT DISTINCT category FROM "+table+";")
results = cursor.fetchall()
print(results)

cursor.execute("SELECT DISTINCT txid FROM "+table+" WHERE address = '1Lets1xxxx1use1xxxxxxxxxxxy2EaMkJ';")
results = cursor.fetchall()
print(str(len(results))+" SPAM txids")

cursor.execute("SELECT DISTINCT txid FROM "+table+" WHERE category = 'NTX';")
results = cursor.fetchall()
print(str(len(results))+" NTX txids")

cursor.execute("SELECT DISTINCT txid FROM "+table+" WHERE category = 'Split or Consolidate';")
results = cursor.fetchall()
print(str(len(results))+" Splits")

cursor.execute("SELECT DISTINCT txid FROM "+table+" WHERE category = 'Sent';")
results = cursor.fetchall()
print(str(len(results))+" Sent")

cursor.execute("SELECT DISTINCT txid FROM "+table+" WHERE category = 'Received';")
results = cursor.fetchall()
print(str(len(results))+" Received")


cursor.close()

conn.close()


