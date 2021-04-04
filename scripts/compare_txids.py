#!/usr/bin/env python3
import csv
import json
import math
import time
import requests
from lib_const import CONN, CURSOR, RPC

CURSOR.execute("SELECT txid, ac_ntx_height, chain FROM notarised;")

results = CURSOR.fetchall()
print(f"{len(results)} txids in [notarised] table")

missing_txid_dict = {}
smk_KMD_block_list = []
smk_txid_list = []
decker_txid_list = []
decker_KMD_block_list = []

for item in results:
    smk_txid_list.append(item[0])

    if item[2] == "BTC":
        smk_KMD_block_list.append(item[1])


with open('s4-stats-txes-time.csv', 'r') as csv_file:

    reader = list(csv.reader(csv_file))
    row_count = len(reader)

    print(f"{row_count} [decker] records to scan...")

    i = 0
    for row in reader:
        txid = row[0]
        #notaries = row[1]
        coin = row[2]
        block = row[3]
        #timestamp = row[4]

        if coin == "KMD":
            decker_KMD_block_list.append(int(block))

        else:
            decker_txid_list.append(txid)

missing_txids = list(set(decker_txid_list).difference(set(smk_txid_list)))
print(f"{len(missing_txids)} missing txids (KMD/BTC not included)")

if len(missing_txids) > 0:
    print(f"{len(missing_txids)} missing txids to verify")
    with open("missing_txids.json", "w") as f:
        json.dump(list(missing_txids), f)

decker_blockhashes = []
for block in decker_KMD_block_list:
    blockhash = RPC["KMD"].getblock(str(block),1)["hash"]
    #extract ntx hash via decode_opret?
    # https://kmd.explorer.dexstats.info/block/05c38b7dad993b9692f54c1b26841911d7afbdc8222a123bc80ae4da2595ace3 [block 2271355]
    # contains https://kmd.explorer.dexstats.info/tx/668dba6696f397503d7a702a25632cbefe76587cfbf8f124cbfa613907d4a553 [notarisation]
    # leading to http://116.203.120.91:8762/api/tools/decode_opreturn/?OP_RETURN=e833fc96683a72cbb4684d91d514f48f464a69dfeaa03d86fe942caafaaff9026ca822006a4b32df2a29f7f56ab77a38dfbc75f97210a6d93a3ef2f148044e8662ed13424b4d4400
    # linking to https://kmd.explorer.dexstats.info/block/02f9affaaa2c94fe863da0eadf694a468ff414d5914d68b4cb723a6896fc33e8 [block 2271340]
    time.sleep(0.002)
    decker_blockhashes.append(blockhash)


smk_notarised = []

cols = ["chain", "block_height", "block_time",
        "txid", "opret", "server",
        "score_value", ]

CURSOR.execute(f"SELECT {', '.join(cols)} FROM notarised WHERE season ='Season_4';")

results = CURSOR.fetchall()
print(f"{len(results)} txids in [notarised] table")

smk_blockhashes = []
for item in results:
    row = {}
    for i in range(len(cols)):
        row.update({cols[i]:str(item[i])})
        if cols[i] == 'ac_ntx_blockhash':
            smk_blockhashes.append(cols[i])
    smk_notarised.append(row)

missing_blockhashes = list(set(decker_blockhashes).difference(set(smk_blockhashes)))
print(f"{len(missing_blockhashes)} missing KMD blockhashes")

if len(missing_blockhashes) > 0:
    with open("missing_blockhashes.json", "w") as f:
        json.dump(list(missing_blockhashes), f)

with open("smk_notarised.json", "w") as f:
    json.dump(list(smk_notarised), f)

CONN.close()
