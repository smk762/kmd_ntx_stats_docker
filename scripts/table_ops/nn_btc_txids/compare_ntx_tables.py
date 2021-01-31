#!/usr/bin/env python3
import table_lib

conn = table_lib.connect_db()
cursor = conn.cursor()

cursor.execute("SELECT txid FROM nn_btc_tx WHERE categry = 'NTX';")
results = cursor.fetchall()
nn_btc_tx_list = []
for item in results:
    nn_btc_tx_list.append(item[0])
nn_btc_tx_list = list(set(nn_btc_tx_list))
print(f"{len(nn_btc_tx_list)} txids in nn_btc_tx_list")

cursor.execute("SELECT btc_txid FROM notarised_btc;")
results = cursor.fetchall()
notarised_btc_list = []
for item in results:
    notarised_btc_list.append(item[0])
notarised_btc_list = list(set(notarised_btc_list))
print(f"{len(notarised_btc_list)} txids in ")

cursor.execute("SELECT txid FROM notarised WHERE chain = 'BTC';")
results = cursor.fetchall()
notarised_list = []
for item in results:
    notarised_list.append(item[0])
notarised_list = list(set(notarised_list))
print(f"{len(notarised_list)} txids in ")

cursor.close()
conn.close()


