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
table = 'notarised'

cursor.execute("SELECT * FROM "+table+" WHERE btc_validated='true';")

results = cursor.fetchall()
print(results)
print(len(results))

cursor.execute("SELECT * FROM notarised WHERE opret LIKE '%' || '06a75b02ee5825e84cf74' || '%';")
results = cursor.fetchall()
print(results)



cursor.close()

conn.close()


