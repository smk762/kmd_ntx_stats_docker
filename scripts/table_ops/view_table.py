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
#table = 'notarised'
table = 'nn_btc_tx'

cursor.execute("SELECT * FROM "+table+";")
#cursor.execute("SELECT * FROM "+table+" WHERE txid = '2cc68de3c286726fa5df46623266b8a7cc6c7b8d099621e2398956835da187c9';")

#cursor.execute("SELECT * FROM "+table+" WHERE chain = 'BTC' AND btc_validated = 'false';")

results = cursor.fetchall()
print(results)
print(len(results))

list = []
for item in results:
    list.append(item[0])
print(list)
cursor.close()

conn.close()


