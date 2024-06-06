#!/usr/bin/env python3
from lib_const import *
from decorators import *
from lib_dpow_const import SEASONS_INFO
from lib_query_ntx import select_from_notarised_tbl_where
from lib_update_ntx import delete_from_notarised_tbl_where, update_ntx_row
import lib_helper as helper
import lib_ntx


def archive_past_seasons(current_seasons=["Season_7"]):
    for season in SEASONS_INFO:
        print(season)
        if season not in current_seasons:
            print(season)
            data = select_from_notarised_tbl_where(season=season)
            for i in data:
                txid = i[1]
                coin = i[2]
                block_hash = i[3]
                block_time = i[4]
                block_datetime = i[5]
                block_height = i[6]
                notaries = i[7]                
                ac_ntx_blockhash = i[8]
                ac_ntx_height = i[9]
                opret = i[10]
                season = i[11]
                notary_addresses = i[12]
                scored = i[13]
                server = i[14]
                score_value = i[15]                
                epoch = i[16]

                row_data = (coin, block_height, 
                    block_time, block_datetime, block_hash, 
                    notaries, notary_addresses,
                    ac_ntx_blockhash, ac_ntx_height, txid,
                    opret, season, server, scored,
                    score_value, epoch)
                update_ntx_row(row_data, table='notarised_archive', unique='unique_txid_archive')
            delete_from_notarised_tbl_where(season=season)

            
            
    
if __name__ == '__main__':
    current_seasons = ["Season_7"]
    archive_past_seasons(current_seasons)
