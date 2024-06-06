#!/usr/bin/env python3
import os
import json
from psycopg2.extras import execute_values
from datetime import datetime as dt
from lib_const import *
from lib_update_ntx import *

#### KMD SUPPLY TABLE

def update_kmd_supply_row(row_data):
    CONN = connect_db()
    CURSOR = CONN.cursor()
    try:
        sql = f"INSERT INTO kmd_supply (block_height, block_time, total_supply, delta) VALUES (%s, %s, %s, %s);"
        CURSOR.execute(sql, row_data)
        CONN.commit()
    except Exception as e:
        logger.error(f"Exception in [update_kmd_supply_row]: {e}")
        logger.error(f"[update_kmd_supply_row] sql: {sql}")
        logger.error(f"[update_kmd_supply_row] row_data: {row_data}")
        CONN.rollback()

#### ADRESSES TABLE

def update_addresses_row(row_data):
    CONN = connect_db()
    CURSOR = CONN.cursor()
    try:
        sql = f"INSERT INTO addresses \
                    (season, server, notary, notary_id, \
                    address, pubkey, coin) \
                VALUES (%s, %s, %s, %s, %s, %s, %s) \
                ON CONFLICT ON CONSTRAINT unique_season_coin_address \
                DO UPDATE SET \
                    server='{row_data[1]}', notary='{row_data[2]}', \
                    notary_id='{row_data[3]}', address='{row_data[4]}', \
                    pubkey='{row_data[5]}', coin='{row_data[6]}';"
        CURSOR.execute(sql, row_data)
        CONN.commit()
    except Exception as e:
        logger.error(f"Exception in [update_addresses_row]: {e}")
        logger.error(f"[update_addresses_row] sql: {sql}")
        logger.error(f"[update_addresses_row] row_data: {row_data}")
        CONN.rollback()


def delete_addresses_row(season, coin, address):
    CONN = connect_db()
    CURSOR = CONN.cursor()
    CURSOR.execute(f"DELETE FROM addresses WHERE \
        season = '{season}', \
        coin = '{coin}', \
        address = '{address}' \
        ;")
    CONN.commit()


#### BALANCES TABLE

def update_balances_row(row_data):
    CONN = connect_db()
    CURSOR = CONN.cursor()
    try:
        sql = f"INSERT INTO balances \
                (season, server, notary, \
                address, coin, balance, update_time) \
            VALUES (%s, %s, %s, %s, %s, %s, %s) \
            ON CONFLICT ON CONSTRAINT unique_coin_address_season_balance DO UPDATE SET \
                balance={row_data[5]}, \
                server='{row_data[1]}', \
                update_time={row_data[6]};"
        CURSOR.execute(sql, row_data)
        CONN.commit()
    except Exception as e:
        logger.error(f"Exception in [update_balances_row]: {e}")
        logger.error(f"[update_balances_row] sql: {sql}")
        logger.error(f"[update_balances_row] row_data: {row_data}")
        CONN.rollback()


def delete_balances_row(coin, address, season):
    CONN = connect_db()
    CURSOR = CONN.cursor()
    try:
        sql = f"DELETE FROM balances WHERE coin='{coin}' and address='{address}' and season={season};"
        CURSOR.execute(sql)
        CONN.commit()
    except Exception as e:
        logger.error(f"Exception in [delete_balances_row]: {e}")
        CONN.rollback()


def update_rewards_row(row_data):
    CONN = connect_db()
    CURSOR = CONN.cursor()
    try:
        sql = "INSERT INTO rewards \
            (address, notary, utxo_count, eligible_utxo_count, \
            oldest_utxo_block, balance, rewards, update_time) \
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s) \
            ON CONFLICT ON CONSTRAINT unique_reward_address DO UPDATE SET \
            notary='"+str(row_data[1])+"', utxo_count="+str(row_data[2])+", \
            eligible_utxo_count="+str(row_data[3])+", oldest_utxo_block="+str(row_data[4])+", \
            balance="+str(row_data[5])+", rewards="+str(row_data[6])+", \
            update_time="+str(row_data[7])+";"
        CURSOR.execute(sql, row_data)
        CONN.commit()
        return 1
    except Exception as e:
        if str(e).find('Duplicate') == -1:
            logger.debug(e)
            logger.debug(row_data)
        CONN.rollback()
        return 0


def delist_coin(coin):
    CONN = connect_db()
    CURSOR = CONN.cursor()
    try:
        if coin in ["PIRATE", "TOKEL"]: return
        sql = f"DELETE FROM coins WHERE coin = '{coin}';"
        CURSOR.execute(sql)
        CONN.commit()
        #print(sql)
        return 1
    except Exception as e:
        logger.debug(e)
        CONN.rollback()
        return 0


def update_coins_row(row_data):
    CONN = connect_db()
    CURSOR = CONN.cursor()
    try:
        sql = "INSERT INTO coins \
            (coin, coins_info, electrums, electrums_ssl, electrums_wss, explorers, lightwallets, dpow, dpow_tenure, dpow_active, mm2_compatible) \
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) \
            ON CONFLICT ON CONSTRAINT unique_coin_coin DO UPDATE SET \
            coins_info='"+str(row_data[1])+"', \
            electrums='"+str(row_data[2])+"', \
            electrums_ssl='"+str(row_data[3])+"', \
            electrums_wsl='"+str(row_data[4])+"', \
            explorers='"+str(row_data[5])+"', \
            lightwallets='"+str(row_data[6])+"', \
            dpow='"+str(row_data[7])+"', \
            dpow_tenure='"+str(row_data[8])+"', \
            dpow_active='"+str(row_data[9])+"', \
            mm2_compatible='"+str(row_data[10])+"';"
        CURSOR.execute(sql, row_data)
        CONN.commit()
        return 1
    except Exception as e:
        logger.debug(e)
        if str(e).find('Duplicate') == -1:
            logger.debug(row_data)
        CONN.rollback()
        return 0


def update_mined_row(row_data):
    CONN = connect_db()
    CURSOR = CONN.cursor()
    try:
        sql = "INSERT INTO mined \
            (block_height, block_time, block_datetime, \
             value, address, name, txid, diff, season, btc_price, usd_price, category) \
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) \
            ON CONFLICT ON CONSTRAINT unique_block DO UPDATE SET \
            block_time='"+str(row_data[1])+"', \
            block_datetime='"+str(row_data[2])+"', \
            value="+str(row_data[3])+", \
            address='"+str(row_data[4])+"', \
            name='"+str(row_data[5])+"', \
            txid='"+str(row_data[6])+"', \
            diff='"+str(row_data[7])+"', \
            season='"+str(row_data[8])+"', \
            btc_price='"+str(row_data[9])+"', \
            usd_price='"+str(row_data[10])+"', \
            category='"+str(row_data[11])+"';"
        CURSOR.execute(sql, row_data)
        CONN.commit()
    except Exception as e:
        logger.debug(e)
        if str(e).find('Duplicate') == -1:
            logger.debug(row_data)
        CONN.rollback()


def update_season_mined_count_row(row_data):
    CONN = connect_db()
    CURSOR = CONN.cursor()
    try:
        sql = f"INSERT INTO mined_count_season \
            (name, season, address, blocks_mined, sum_value_mined, \
            max_value_mined, max_value_txid, last_mined_blocktime, last_mined_block, \
            timestamp) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) \
            ON CONFLICT ON CONSTRAINT unique_name_season_mined DO UPDATE SET \
            address='{row_data[2]}', blocks_mined={row_data[3]}, sum_value_mined={row_data[4]}, \
            max_value_mined={row_data[5]}, max_value_txid='{row_data[6]}', last_mined_blocktime={row_data[7]}, \
            last_mined_block={row_data[8]}, timestamp={row_data[9]};"
        CURSOR.execute(sql, row_data)
        CONN.commit()
        return 1
    except Exception as e:
        if str(e).find('Duplicate') == -1:
            logger.debug(e)
            logger.debug(row_data)
        CONN.rollback()
        return 0


def update_daily_mined_count_row(row_data):
    CONN = connect_db()
    CURSOR = CONN.cursor()
    try:
        sql = f"INSERT INTO mined_count_daily \
                    (notary, blocks_mined, sum_value_mined, \
                    mined_date, btc_price, usd_price,timestamp) \
                    VALUES (%s, %s, %s, %s, %s, %s, %s) \
                ON CONFLICT ON CONSTRAINT unique_notary_daily_mined DO UPDATE SET \
                    blocks_mined={row_data[1]}, \
                    sum_value_mined='{row_data[2]}',\
                    mined_date='{row_data[3]}',\
                    btc_price={row_data[4]},\
                    usd_price={row_data[5]};"
        CURSOR.execute(sql, row_data)
        CONN.commit()
        return 1
    except Exception as e:
        if str(e).find('Duplicate') == -1:
            logger.debug(e)
            logger.debug(row_data)
        CONN.rollback()
        return 0


def update_table(table, update_str, condition):
    CONN = connect_db()
    CURSOR = CONN.cursor()
    try:
        sql = "UPDATE "+table+" \
               SET "+update_str+" WHERE "+condition+";"

        CURSOR.execute(sql)
        CONN.commit()
        return 1
    except Exception as e:
        logger.debug(e)
        logger.debug(sql)
        CONN.rollback()
        return 0


def update_sync_tbl(row_data):
    CONN = connect_db()
    CURSOR = CONN.cursor()
    try:
        sql = "INSERT INTO coin_sync \
            (coin, block_height, sync_hash, explorer_hash) \
            VALUES (%s, %s, %s, %s) \
            ON CONFLICT ON CONSTRAINT unique_coin_sync DO UPDATE SET \
            block_height='"+str(row_data[1])+"', \
            sync_hash='"+str(row_data[2])+"', \
            explorer_hash='"+str(row_data[3])+"';"
        CURSOR.execute(sql, row_data)
        CONN.commit()
        return 1
    except Exception as e:
        if str(e).find('Duplicate') == -1:
            logger.debug(e)
            logger.debug(row_data)
        CONN.rollback()
        return 0


def update_nn_social_row(row_data):
    CONN = connect_db()
    CURSOR = CONN.cursor()
    try:
        sql = "INSERT INTO  nn_social \
            (notary, twitter, youtube, email, discord, \
            telegram, github, keybase, \
            website, icon, season) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) \
            ON CONFLICT ON CONSTRAINT unique_notary_season_social DO UPDATE SET \
            twitter='"+str(row_data[1])+"', youtube='"+str(row_data[2])+"', \
            email='"+str(row_data[3])+"', discord='"+str(row_data[4])+"', \
            telegram='"+str(row_data[5])+"', github='"+str(row_data[6])+"', \
            keybase='"+str(row_data[7])+"', website='"+str(row_data[8])+"', \
            icon='"+str(row_data[9])+"', season='"+str(row_data[10])+"';"
        CURSOR.execute(sql, row_data)
        CONN.commit()
        return 1
    except Exception as e:
        if str(e).find('Duplicate') == -1:
            logger.debug(e)
            logger.debug(row_data)
        CONN.rollback()
        return 0


def update_coin_social_row(row_data):
    CONN = connect_db()
    CURSOR = CONN.cursor()
    try:
        sql = f"INSERT INTO  coin_social \
            (coin, discord, email, explorers, github, icon, linkedin, \
             mining_pools, reddit, telegram, twitter, youtube, website, season) \
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) \
            ON CONFLICT ON CONSTRAINT unique_coin_season_social \
            DO UPDATE SET \
                discord='{row_data[1]}', email='{row_data[2]}', \
                explorers=ARRAY{row_data[3]}::VARCHAR[], github='{row_data[4]}', \
                icon='{row_data[5]}', linkedin='{row_data[6]}', \
                mining_pools=ARRAY{row_data[7]}::VARCHAR[], reddit='{row_data[8]}', \
                telegram='{row_data[9]}', twitter='{row_data[10]}', \
                youtube='{row_data[11]}', website='{row_data[12]}', \
                season='{row_data[13]}';"
        #print(sql)
        CURSOR.execute(sql, row_data)
        CONN.commit()
        print("commited")
        return 1
    except Exception as e:
        if str(e).find('Duplicate') == -1:
            logger.debug(e)
            logger.debug(row_data)
        CONN.rollback()
        return 0


def update_btc_address_deltas_tbl(row_data):
    CONN = connect_db()
    CURSOR = CONN.cursor()
    try:
        sql = "INSERT INTO  btc_address_deltas \
            (notary, address, category, txid, block_time, \
             total_in, total_out, fees, vin_addr, vout_addr, season) \
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"
        CURSOR.execute(sql, row_data)
        CONN.commit()
        return 1
    except Exception as e:
        if str(e).find('Duplicate') == -1:
            logger.debug(e)
            logger.debug(row_data)
        CONN.rollback()
        return 0


def update_funding_row(row_data):
    CONN = connect_db()
    CURSOR = CONN.cursor()
    try:
        sql = "INSERT INTO  funding_transactions \
            (coin, txid, vout, amount, \
            block_hash, block_height, block_time, \
            category, fee, address, notary, season) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) \
            ON CONFLICT ON CONSTRAINT unique_category_vout_txid_funding DO UPDATE SET \
            coin='"+str(row_data[0])+"', \
            amount='"+str(row_data[3])+"', \
            block_hash='"+str(row_data[4])+"', \
            block_height='"+str(row_data[5])+"', \
            block_time='"+str(row_data[6])+"', \
            fee='"+str(row_data[8])+"', \
            address='"+str(row_data[9])+"', \
            notary='"+str(row_data[10])+"', \
            season='"+str(row_data[11])+"';"
        CURSOR.execute(sql, row_data)
        CONN.commit()
        return 1
    except Exception as e:
        if str(e).find('Duplicate') == -1:
            logger.debug(e)
            logger.debug(row_data)
        CONN.rollback()
        return 0

def ts_col_to_dt_col(ts_col, dt_col, table):
    CONN = connect_db()
    CURSOR = CONN.cursor()
    sql = "UPDATE "+table+" SET "+dt_col+"=to_timestamp("+ts_col+");"
    CURSOR.execute(sql)
    CONN.commit()


def delete_nn_btc_tx_transaction(txid):
    CONN = connect_db()
    CURSOR = CONN.cursor()
    CURSOR.execute(f"DELETE FROM nn_btc_tx WHERE txid='{txid}';")
    CONN.commit()


def update_nn_btc_tx_row(row_data):
    CONN = connect_db()
    CURSOR = CONN.cursor()
    sql = "INSERT INTO nn_btc_tx (txid, block_hash, block_height, \
                                block_time, block_datetime, \
                                address, notary, season, category, \
                                input_index, input_sats, \
                                output_index, output_sats, fees, num_inputs, num_outputs) \
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) \
        ON CONFLICT ON CONSTRAINT unique_btc_nn_txid DO UPDATE SET \
        notary='"+str(row_data[6])+"', category='"+str(row_data[8])+"', \
        season='"+str(row_data[7])+"';"
    try:
        CURSOR.execute(sql, row_data)
        CONN.commit()
    except Exception as e:
        logger.debug(e)
        if str(e).find('duplicate') == -1:
            logger.debug(row_data)
        CONN.rollback()


def update_nn_btc_tx_notary_from_addr(notary, addr):
    CONN = connect_db()
    CURSOR = CONN.cursor()
    sql = f"UPDATE nn_btc_tx SET notary='{notary}' WHERE address='{addr}';"
    try:
        CURSOR.execute(sql)
        CONN.commit()
        logger.info(f"{addr} tagged as {notary} in DB")
    except Exception as e:
        logger.debug(e)
        CONN.rollback()

def update_nn_btc_tx_notary_category_from_addr(notary, category, addr):
    CONN = connect_db()
    CURSOR = CONN.cursor()
    sql = f"UPDATE nn_btc_tx SET notary='{notary}', category='{category}' WHERE address='{addr}';"
    try:
        CURSOR.execute(sql)
        CONN.commit()
        logger.info(f"{addr} tagged as {notary} in DB")
    except Exception as e:
        logger.debug(e)
        CONN.rollback()

def update_nn_btc_tx_category_from_txid(category, txid):
    CONN = connect_db()
    CURSOR = CONN.cursor()
    sql = f"UPDATE nn_btc_tx SET category='{category}' WHERE txid='{txid}';"
    try:
        CURSOR.execute(sql)
        CONN.commit()
        logger.info(f"{txid} tagged as {category} in DB")
    except Exception as e:
        logger.debug(e)
        CONN.rollback()

def update_nn_btc_tx_outindex_from_txid(outindex, txid):
    CONN = connect_db()
    CURSOR = CONN.cursor()
    sql = f"UPDATE nn_btc_tx SET output_index='{outindex}' WHERE txid='{txid}';"
    try:
        CURSOR.execute(sql)
        CONN.commit()
        logger.info(f"{txid} tagged as {outindex} in DB")
    except Exception as e:
        logger.debug(e)
        CONN.rollback()


def delete_nn_btc_tx_row(txid, notary):
    CONN = connect_db()
    CURSOR = CONN.cursor()
    sql = "DELETE FROM nn_btc_tx WHERE txid='"+str(txid)+"' and notary='"+str(notary)+"';"
    try:
        CURSOR.execute(sql)
        CONN.commit()
    except Exception as e:
        logger.debug(e)
        CONN.rollback()


def update_nn_ltc_tx_notary_from_addr(notary, addr):
    CONN = connect_db()
    CURSOR = CONN.cursor()
    sql = f"UPDATE nn_ltc_tx SET notary='{notary}' WHERE address='{addr}';"
    try:
        CURSOR.execute(sql)
        CONN.commit()
        logger.info(f"{addr} tagged as {notary} in DB")
    except Exception as e:
        logger.debug(e)
        CONN.rollback()


def update_nn_ltc_tx_row(row_data):
    CONN = connect_db()
    CURSOR = CONN.cursor()
    sql = "INSERT INTO nn_ltc_tx (txid, block_hash, block_height, \
                                block_time, block_datetime, \
                                address, notary, season, category, \
                                input_index, input_sats, \
                                output_index, output_sats, fees, num_inputs, \
                                num_outputs) \
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) \
        ON CONFLICT ON CONSTRAINT unique_ltc_nn_txid DO UPDATE SET \
        notary='"+str(row_data[6])+"', category='"+str(row_data[8])+"', \
        season='"+str(row_data[7])+"';"
    try:
        CURSOR.execute(sql, row_data)
        CONN.commit()
    except Exception as e:
        logger.debug(e)
        if str(e).find('duplicate') == -1:
            logger.debug(row_data)
        CONN.rollback()


def update_scoring_epoch_row(row_data):
    CONN = connect_db()
    CURSOR = CONN.cursor()
    sql = f"INSERT INTO scoring_epochs \
                (season, server, epoch, epoch_start, epoch_end, \
                start_event, end_event, epoch_coins, score_per_ntx) \
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) \
        ON CONFLICT ON CONSTRAINT unique_scoring_epoch DO UPDATE SET \
            epoch_start={row_data[3]}, \
            epoch_end={row_data[4]}, \
            start_event='{row_data[5]}', \
            end_event='{row_data[6]}', \
            epoch_coins=ARRAY{row_data[7]}, \
            score_per_ntx={row_data[8]};"
    try:
        CURSOR.execute(sql, row_data)
        CONN.commit()
    except Exception as e:
        logger.debug(e)
        if str(e).find('duplicate') == -1:
            logger.debug(row_data)
        CONN.rollback()


def update_notary_vote_row(row_data):
    CONN = connect_db()
    CURSOR = CONN.cursor()
    sql = f"INSERT INTO notary_vote \
                (txid, block_hash, block_time, \
                lock_time, block_height, votes, \
                candidate, candidate_address, \
                mined_by, difficulty, notes, year, valid) \
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) \
        ON CONFLICT ON CONSTRAINT unique_vote_txid_candidate DO UPDATE SET \
            txid='{row_data[0]}', \
            block_hash='{row_data[1]}', \
            block_time={row_data[2]}, \
            lock_time={row_data[3]}, \
            block_height={row_data[4]}, \
            votes={row_data[5]}, \
            candidate='{row_data[6]}', \
            candidate_address='{row_data[7]}', \
            mined_by='{row_data[8]}', \
            difficulty='{row_data[9]}', \
            notes='{row_data[10]}', \
            year='{row_data[11]}', \
            valid='{row_data[12]}';"
    try:
        CURSOR.execute(sql, row_data)
        CONN.commit()
        print("Notary Vote Row updated")
    except Exception as e:
        logger.debug(e)
        if str(e).find('duplicate') == -1:
            logger.debug(row_data)
        CONN.rollback()


def update_swaps_row(row_data):
    CONN = connect_db()
    CURSOR = CONN.cursor()
    try:
        sql = f"INSERT INTO swaps \
                (uuid, started_at, taker_coin, taker_amount, \
                 taker_gui, taker_version, taker_pubkey, maker_coin, \
                 maker_amount, maker_gui, maker_version, maker_pubkey, timestamp) \
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) \
                ON CONFLICT ON CONSTRAINT unique_swap \
                DO UPDATE SET \
                 started_at='{row_data[1]}', taker_coin='{row_data[2]}', \
                 taker_amount={row_data[3]}, taker_gui='{row_data[4]}', \
                 taker_version='{row_data[5]}', taker_pubkey='{row_data[6]}', \
                 maker_coin='{row_data[7]}', maker_amount={row_data[8]}, \
                 maker_gui='{row_data[9]}', maker_version='{row_data[10]}', \
                 maker_pubkey='{row_data[11]}', timestamp={row_data[12]};"
        CURSOR.execute(sql, row_data)
        CONN.commit()
    except Exception as e:
        logger.error(f"Exception in [update_swaps_row]: {e}")
        logger.error(f"[update_swaps_row] sql: {sql}")
        logger.error(f"[update_swaps_row] row_data: {row_data}")
        # input()
        CONN.rollback()


def update_swaps_failed_row(row_data):
    CONN = connect_db()
    CURSOR = CONN.cursor()
    taker_err_msg = row_data[5]
    maker_err_msg = row_data[12]
    if row_data[5]:
        taker_err_msg = row_data[5].replace("'","")
    if row_data[12]:
        maker_err_msg = row_data[12].replace("'","")
    try:
        sql = f"INSERT INTO swaps_failed \
                (uuid, started_at, taker_coin, taker_amount, \
                 taker_error_type, taker_error_msg, \
                 taker_gui, taker_version, taker_pubkey, maker_coin, \
                 maker_amount, maker_error_type, maker_error_msg, \
                 maker_gui, maker_version, maker_pubkey, timestamp) \
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) \
                ON CONFLICT ON CONSTRAINT unique_swaps_failed \
                DO UPDATE SET \
                 started_at='{row_data[1]}', taker_coin='{row_data[2]}', \
                 taker_amount={row_data[3]}, taker_error_type='{row_data[4]}', \
                 taker_error_msg='{taker_err_msg}', taker_gui='{row_data[6]}', \
                 taker_version='{row_data[7]}', taker_pubkey='{row_data[8]}', \
                 maker_coin='{row_data[9]}', maker_amount={row_data[10]}, \
                 maker_error_type='{row_data[11]}', maker_error_msg='{maker_err_msg}', \
                 maker_gui='{row_data[13]}', maker_version='{row_data[14]}', \
                 maker_pubkey='{row_data[15]}', timestamp={row_data[16]};"
        CURSOR.execute(sql, row_data)
        CONN.commit()
    except Exception as e:
        logger.error(f"Exception in [update_swaps_failed_row]: {e}")
        logger.error(f"[update_swaps_failed_row] sql: {sql}")
        logger.error(f"[update_swaps_failed_row] row_data: {row_data}")
        CONN.rollback()


def delete_rewards_tx_transaction(txid):
    CONN = connect_db()
    CURSOR = CONN.cursor()
    CURSOR.execute(f"DELETE FROM rewards_tx WHERE \
        txid = '{txid}';")
    CONN.commit()


def update_rewards_tx_row(row_data):
    CONN = connect_db()
    CURSOR = CONN.cursor()
    sql = f"INSERT INTO rewards_tx (txid, block_hash, block_height,\
                    block_time, block_datetime,\
                    address, rewards_value,\
                    sum_of_inputs, sum_of_outputs,\
                    btc_price, usd_price) \
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) \
            ON CONFLICT ON CONSTRAINT unique_rewards_nn_txid DO UPDATE SET \
                btc_price={row_data[9]}, usd_price={row_data[10]};"

    try:
        CURSOR.execute(sql, row_data)
        CONN.commit()
    except Exception as e:
        logger.debug(e)
        if str(e).find('duplicate') == -1:
            logger.debug(row_data)
        CONN.rollback()

def update_notary_candidates_row(row_data):
    CONN = connect_db()
    CURSOR = CONN.cursor()
    sql = f"INSERT INTO notary_candidates (year, season, name,\
                       proposal_url) \
                VALUES (%s, %s, %s, %s)\
                ON CONFLICT ON CONSTRAINT unique_name_year_candidate \
                DO UPDATE SET proposal_url='{row_data[3]}';"
    try:
        CURSOR.execute(sql, row_data)
        CONN.commit()
    except Exception as e:
        logger.error(f"Exception in [update_notary_candidates_row]: {e}")
        logger.error(f"[update_notary_candidates_row] sql: {sql}")
        logger.error(f"[update_notary_candidates_row] row_data: {row_data}")
        CONN.rollback()

# Price update


def update_table_prices(table, date_field, day, btc_price, usd_price, timestamp=False):
    CONN = connect_db()
    CURSOR = CONN.cursor()
    if timestamp:
        date = dt.strptime(day, "%d-%m-%Y")
        start = int(dt.timestamp(date))
        end = start + 86400

        sql = f"UPDATE {table} SET btc_price={btc_price}, usd_price={usd_price} WHERE {date_field}>={start} AND {date_field}<{end} ;"
    else:
        date = dt.strptime(day, "%d-%m-%Y")
        sql = f"UPDATE {table} SET btc_price={btc_price}, usd_price={usd_price} WHERE {date_field}='{date}';"
    try:
        CURSOR.execute(sql)
        CONN.commit()
        logger.info(f"{table} {day} price: ${usd_price}")
    except Exception as e:
        logger.debug(e)
        CONN.rollback()
