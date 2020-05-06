#!/usr/bin/env python3
import time
import json
import logging
import logging.handlers
from address_lib import seasons_info
from coins_lib import third_party_coins, all_antara_coins
import table_lib

def get_notarised_counts(season):
    results = table_lib.select_from_table(cursor, "notarised", "chain, notaries",
              "block_time >= "+str(seasons_info[season]['start_time'])+" \
               AND block_time <= "+str(seasons_info[season]['end_time']))
    results_list = []
    time_stamp = int(time.time())
    for item in results:
        results_list.append({
                "chain":item[0],
                "notaries":item[1]
            })
    json_count = {}
    print("Aggregating "+str(len(results_list))+" rows from notarised table for "+season)
    for item in results_list:
        notaries = item['notaries']
        chain = item['chain']
        for notary in notaries:
            if notary in seasons_info[season]['notaries']:
                if notary not in json_count:
                    json_count.update({notary:{}})
                if chain not in json_count[notary]:
                    json_count[notary].update({chain:1})
                else:
                    count = json_count[notary][chain]+1
                    json_count[notary].update({chain:count})
    node_counts = {}
    other_coins = []
    for notary in json_count:
        node_counts.update({notary:{
                "btc_count":0,
                "antara_count":0,
                "third_party_count":0,
                "other_count":0,
                "total_ntx_count":0
            }})
        for chain in json_count[notary]:
            if chain == "KMD":
                count = node_counts[notary]["btc_count"]+json_count[notary][chain]
                node_counts[notary].update({"btc_count":count})
            elif chain in all_antara_coins:
                count = node_counts[notary]["antara_count"]+json_count[notary][chain]
                node_counts[notary].update({"antara_count":count})
            elif chain in third_party_coins:
                count = node_counts[notary]["third_party_count"]+json_count[notary][chain]
                node_counts[notary].update({"third_party_count":count})
            else:
                count = node_counts[notary]["other_count"]+json_count[notary][chain]
                node_counts[notary].update({"other_count":count})
                other_coins.append(chain)

            count = node_counts[notary]["total_ntx_count"]+json_count[notary][chain]
            node_counts[notary].update({"total_ntx_count":count})

        row_data = (notary, node_counts[notary]['btc_count'], node_counts[notary]['antara_count'], 
                    node_counts[notary]['third_party_count'], node_counts[notary]['other_count'], 
                    node_counts[notary]['total_ntx_count'], json.dumps(json_count[notary]), time_stamp, season)
        print("Adding counts for "+notary+" to notarised_count table")
        table_lib.add_row_to_notarised_count_tbl(conn, cursor, row_data)

logger = logging.getLogger()
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s', datefmt='%d-%b-%y %H:%M:%S')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

conn = table_lib.connect_db()
cursor = conn.cursor()

results_list = get_notarised_counts("Season_3")
#update_table(results_list)

cursor.close()
conn.close()