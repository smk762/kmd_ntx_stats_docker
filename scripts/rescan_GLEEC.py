#!/usr/bin/env python3
from models import notarised_row
from lib_notary import get_gleec_ntx_server, get_dpow_score_value
from lib_table_select import get_notarised_chain_rows

rows = get_notarised_chain_rows("GLEEC")

for row in rows:
    server = get_gleec_ntx_server(row[9])
    if server != row[12]:
        print(f"updating server to {server} for {row[9]}")
        gleec_row = notarised_row()
        gleec_row.chain = row[0]
        gleec_row.block_height = row[1]
        gleec_row.block_time = row[2]
        gleec_row.block_datetime = row[3]
        gleec_row.block_hash = row[4]
        gleec_row.notaries = row[5]
        gleec_row.notary_addresses = row[6]
        gleec_row.ac_ntx_blockhash = row[7]
        gleec_row.ac_ntx_height = row[8]
        gleec_row.txid = row[9]
        gleec_row.opret = row[10]
        gleec_row.season = row[11]
        gleec_row.server = server        
        gleec_row.btc_validated = row[14]
        gleec_row.score_value = get_dpow_score_value(gleec_row.season, gleec_row.server, "GLEEC", gleec_row.block_time)
        gleec_row.update()