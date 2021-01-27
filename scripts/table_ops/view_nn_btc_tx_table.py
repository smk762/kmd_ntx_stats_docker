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

    

#cursor.execute("SELECT * FROM "+table+";")
cursor.execute("SELECT txid, block_hash, block_height, block_time, block_datetime, address, notary, season, category, input_index, input_sats, output_index, output_sats, num_inputs, num_outputs, fees FROM "+table+";")

#cursor.execute("SELECT * FROM "+table+" WHERE chain = 'BTC' AND btc_validated = 'false';")

results = cursor.fetchall()
#print(results)
print(len(results))

output = []
for item in results:
	row = {
		"txid":item[0],
		"block_hash":item[1],
		"block_height":item[2],
		"block_time":item[3],
		"block_datetime":item[4],
		"address":item[5],
		"notary":item[6],
		"season":item[7],
		"category":item[8],
		"input_index":item[9],
		"input_sats":item[10],
		"output_index":item[11],
		"output_sats":item[12],
		"num_inputs":item[13],
		"num_outputs":item[14],
		"fees":item[15]
	}
	print(row)
	output.append(row)
	

print(output)
cursor.close()

conn.close()


