#!/usr/bin/env python3

from models import notarised_row
from lib_notary import get_notarised_data
from lib_table_select import get_existing_notarised_txids

txids = get_existing_notarised_txids()

for txid in txids:
	row_data = get_notarised_data(txid)

	if row_data is not None: # ignore TXIDs that are not notarisations
	    chain = row_data[0]

	    if chain not in ['KMD', 'BTC']: # KMD -> BTC notarisations are requested via BTC blockchain APIs
	        row = notarised_row()
	        row.chain = chain
	        row.block_height = row_data[1]
	        row.block_time = row_data[2]
	        row.block_datetime = row_data[3]
	        row.block_hash = row_data[4]
	        row.notaries = row_data[5]
	        row.notary_addresses = row_data[6]
	        row.ac_ntx_blockhash = row_data[7]
	        row.ac_ntx_height = row_data[8]
	        row.txid = row_data[9]
	        row.opret = row_data[10]
	        row.season = row_data[11]
	        row.server = row_data[12]
	        row.scored = row_data[13]
	        row.btc_validated =  "N/A"
	        row.update()
