#!/usr/bin/env python3
import table_lib

conn = table_lib.connect_db()
cursor = conn.cursor()

#table = 'balances'
#table = 'coin_social'
#table = 'funding_transactions'
#table = 'last_notarised'
#table = 'notarised_chain_season'
#table = 'nn_social'
#table = 'notarised_count_season'
#table = 'coins'
#table = 'notarised_btc'
#table = 'btc_address_deltas'
table = 'notarised'
#table = 'nn_ltc_tx'
#table = 'notarised_tenure'

#cursor.execute("SELECT * FROM "+table+";")
#cursor.execute("SELECT * FROM "+table+" WHERE txid = 'fe9492e6cab89023bdc4e28aee742515e8e8a75ba321617e9715818a4888bb1e';")

cursor.execute("SELECT * FROM "+table+" WHERE chain = 'PBC';")

#cursor.execute("SELECT * FROM "+table+" WHERE chain = 'BTC' AND btc_validated = 'false';")

results = cursor.fetchall()
print(results)
print(len(results))

results_list = []
for item in results:
    results_list.append(item[0])
print(results_list)
cursor.close()

conn.close()


