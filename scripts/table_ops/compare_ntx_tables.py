#!/usr/bin/env python3
import table_lib

conn = table_lib.connect_db()
cursor = conn.cursor()

cursor.execute("SELECT txid FROM nn_btc_tx WHERE category = 'NTX' AND season = 'Season_4' AND notary = 'dragonhound_NA';")
results = cursor.fetchall()
nn_btc_tx_list = []
for item in results:
    nn_btc_tx_list.append(item[0])
nn_btc_tx_list = list(set(nn_btc_tx_list))
print(f"{len(nn_btc_tx_list)} txids in nn_btc_tx_list")

cursor.execute("SELECT btc_txid, notaries FROM notarised_btc WHERE season = 'Season_4'")
results = cursor.fetchall()
notarised_btc_list = []
for item in results:
    if "dragonhound_NA" in item[1]:
        notarised_btc_list.append(item[0])
notarised_btc_list = list(set(notarised_btc_list))
print(f"{len(notarised_btc_list)} txids in notarised_btc_list")

cursor.execute("SELECT txid, notaries FROM notarised WHERE chain = 'BTC' AND season = 'Season_4';")
results = cursor.fetchall()
notarised_list = []
for item in results:
    if "dragonhound_NA" in item[1]:
        notarised_list.append(item[0])
notarised_list = list(set(notarised_list))
print(f"{len(notarised_list)} txids in notarised_list")

for txid in notarised_list:
    if txid not in nn_btc_tx_list:
        print(f"http://stats.kmd.io/api/info/nn_btc_txid?txid={txid}")
        print(f"https://api.blockcypher.com/v1/btc/main/txs/{txid}?limit=800")

cursor.close()
conn.close()


