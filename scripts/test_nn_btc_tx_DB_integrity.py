#!/usr/bin/env python3
from lib_notary import *
from lib_table_update import *
from lib_table_select import *
from lib_api import *

conn = connect_db()
cursor = conn.cursor()

def get_existing_nn_btc_txids(cursor, address=None, category=None, season=None):
    recorded_txids = []
    sql = f"SELECT DISTINCT txid from nn_btc_tx"
    conditions = []
    if category:
        conditions.append(f"category = '{category}'")
    if season:
        conditions.append(f"season = '{season}'")
    if address:
        conditions.append(f"address = '{address}'")

    if len(conditions) > 0:
        sql += " where "
        sql += " and ".join(conditions)    
    sql += ";"

    cursor.execute(sql)
    existing_txids = cursor.fetchall()

    for txid in existing_txids:
        recorded_txids.append(txid[0])
    return recorded_txids

def validate_ntx_addr():
    print(f"Validating NTX Address...")
    cursor.execute(f"SELECT category, notary, txid FROM nn_btc_tx WHERE address='{BTC_NTX_ADDR}';")
    ntx_addr_txids = cursor.fetchall()
    for row in ntx_addr_txids:
        category = row[0]
        notary = row[1]
        txid = row[2]
        if notary != "BTC_NTX_ADDR":
            print(f"BTC_NTX_ADDR {txid} IMPROPER NOTARY {notary}")
            cursor.execute(f"DELETE FROM nn_btc_tx WHERE txid='{txid}';")
            conn.commit()
            print(f"deleted {txid}")
        if category != "NTX":
            print(f"BTC_NTX_ADDR {txid} IMPROPER CATEGORY {category}")
            cursor.execute(f"DELETE FROM nn_btc_tx WHERE txid='{txid}';")
            conn.commit()
            print(f"deleted {txid}")


def validate_ntx_row_counts():
    print(f"Validating NTX Rows...")
    ntx_txids = get_existing_nn_btc_txids(cursor, None, "NTX")
    for txid in ntx_txids:
        cursor.execute(f"SELECT COUNT(*) FROM nn_btc_tx WHERE txid='{txid}';")
        txid_row_count = cursor.fetchall()[0][0]
        if txid_row_count != 14:
            print(f"ntx {txid} row count {txid_row_count}")
            cursor.execute(f"DELETE FROM nn_btc_tx WHERE txid='{txid}';")
            conn.commit()
            print(f"deleted {txid}")

def validate_split_rows():
    print(f"Validating Split Rows...")
    ntx_txids = get_existing_nn_btc_txids(cursor, None, "Split")
    for txid in ntx_txids:
        cursor.execute(f"SELECT COUNT(*) FROM nn_btc_tx WHERE txid='{txid}';")
        txid_row_count = cursor.fetchall()[0][0]
        if txid_row_count != 1:
            print(f"split {txid} row count {txid_row_count}")
            cursor.execute(f"DELETE FROM nn_btc_tx WHERE txid='{txid}';")
            conn.commit()
            print(f"deleted {txid}")
        else:
            cursor.execute(f"SELECT input_index, input_sats, output_index, output_sats, txid FROM nn_btc_tx WHERE txid='{txid}';")
            split_row = cursor.fetchall()[0]
            input_index = split_row[0]
            input_sats = split_row[1]
            output_index = split_row[2]
            output_sats = split_row[3]
            txid = split_row[4]
            for i in [input_index, input_sats, output_index, output_sats]:
                if i != -99:
                    print(f"Non -99 value for input/output index/sats in txid {txid}")
                    cursor.execute(f"DELETE FROM nn_btc_tx WHERE txid='{txid}';")
                    conn.commit()
                    print(f"deleted {txid}")

def validate_notaries_by_address(address, season):
    print(f"Validating Notary Address Rows for {address} {season} {NN_BTC_ADDRESSES_DICT[season][address]}...")
    cursor.execute(f"SELECT notary, txid FROM nn_btc_tx WHERE address='{address}';")
    addr_rows = cursor.fetchall()
    for row in addr_rows:
        notary = row[0]
        txid = row[1]
        if NN_BTC_ADDRESSES_DICT[season][address] != notary:
            print(f"{address} is {NN_BTC_ADDRESSES_DICT[season][address]}, not {notary}")
            sql = f"UPDATE nn_btc_tx SET notary = '{NN_BTC_ADDRESSES_DICT[season][address]}' WHERE address = '{address}' and txid = '{txid}';"
            cursor.execute(sql)
            conn.commit()
            print(f"Updated {txid} {notary} {address} {season}")




    # NTX has 13 vins, 1 vout
    # no tx has rows with same vin/vout combo
    # no tx has different categories

    pass

validate_ntx_row_counts()
validate_split_rows()
validate_ntx_addr()
for season in NN_BTC_ADDRESSES_DICT:
    for address in NN_BTC_ADDRESSES_DICT[season]:
        validate_notaries_by_address(address, season)