#!/usr/bin/env python3
import time
import random
import datetime
from datetime import datetime as dt

import lib_epochs
from lib_rpc import *
from lib_const import *
from lib_table_select import *
from lib_crypto import get_opret_ticker, lil_endian
from lib_helper import *
from models import *
from lib_threads import *


@print_runtime
def update_notarised_table(season, rescan=False):
    start_block = SEASONS_INFO[season]["start_block"]
    end_block = SEASONS_INFO[season]["end_block"]

    TIP = int(RPC["KMD"].getblockcount())
    
    if not rescan:
        start_block = TIP - 24 * 60 * 3
        logger.info(f"Processing notarisations for {season}, blocks {start_block} - {end_block} (last 3 days)")
        unrecorded_KMD_txids = get_unrecorded_KMD_txids(TIP, season, start_block, end_block)
        unrecorded_KMD_txids.sort()
        update_KMD_notarisations(unrecorded_KMD_txids)

    else:
        windows = []

        for i in range(start_block, end_block, RESCAN_CHUNK_SIZE):
            windows.append((i, i + RESCAN_CHUNK_SIZE))

        if OTHER_SERVER.find("stats") == -1:
            windows.reverse()
        
        logger.info(f"Processing notarisations for {season}, blocks {start_block} - {end_block}")
        
        i = 0
        while len(windows) > 0:
            i += 1
            window = random.choice(windows)

            logger.info(f"Processing notarisations for blocks in window {window[0]} - {window[1]} ({i}/{len(windows)})")
            unrecorded_KMD_txids = get_unrecorded_KMD_txids(TIP, season, window[0], window[1])
            random.shuffle(unrecorded_KMD_txids)
            update_KMD_notarisations(unrecorded_KMD_txids)
            windows.remove(window)


@print_runtime
def update_notarised_chain_daily_table(season, rescan=False):

    season_start_dt = dt.fromtimestamp(SEASONS_INFO[season]["start_time"])
    season_end_dt = dt.fromtimestamp(SEASONS_INFO[season]["end_time"])
    start = season_start_dt.date()
    end = datetime.date.today()

    if time.time() > SEASONS_INFO[season]["end_time"]:
        end = season_end_dt.date()

    if not rescan:
        logger.info("Starting "+season+" scan from 3 days ago...")
        start = end - datetime.timedelta(days=3)

    logger.info(f"Updating [notarised_chain_daily] for {season}")
    logger.info(f"Scanning {start} to {end}")

    while start <= end:
        logger.info(f"Updating [notarised_chain_daily] for {start}")
        update_daily_chain_ntx(season, start)
        start += datetime.timedelta(days=1)


@print_runtime
def update_notarised_count_daily_table(season, rescan=False):

    season_start_dt = dt.fromtimestamp(SEASONS_INFO[season]["start_time"])
    season_end_dt = dt.fromtimestamp(SEASONS_INFO[season]["end_time"])
    start = season_start_dt.date()
    end = datetime.date.today()

    if time.time() > SEASONS_INFO[season]["end_time"]:
        end = season_end_dt.date()

    if not rescan:
        logger.info("Starting "+season+" scan from 3 days ago...")
        start = end - datetime.timedelta(days=3)

    logger.info(f"Updating [notarised_count_daily] for {season}")
    logger.info(f"Scanning {start} to {end}")

    while start <= end:
        update_daily_count_ntx(season, start)
        start += datetime.timedelta(days=1)


def update_daily_count_ntx(season, day):
    chains_aggr_resp = get_notarised_chain_date_aggregates(season, day)
    chain_ntx_count_dict = get_chain_ntx_count_dict(season, day)
    notary_ntx_count_dict = get_notary_ntx_count_dict(season, day)
    notary_counts, notary_ntx_pct = get_notary_count_categorized(
                                        notary_ntx_count_dict,
                                        chain_ntx_count_dict
                                    )

    # calculate notary ntx percentage for chains and add row to db table.
    for notary in notary_counts:
        row = notarised_count_daily_row()
        row.notary = notary
        row.btc_count = notary_counts[notary]['btc_count']
        row.antara_count = notary_counts[notary]['antara_count']
        row.third_party_count = notary_counts[notary]['third_party_count']
        row.other_count = notary_counts[notary]['other_count']
        row.total_ntx_count = notary_counts[notary]['total_ntx_count']
        row.chain_ntx_counts = json.dumps(notary_ntx_count_dict[notary])
        row.chain_ntx_pct = json.dumps(notary_ntx_pct[notary])
        row.season = season
        row.notarised_date = day
        row.update()


@print_runtime
def update_notarised_chain_season_table(season):
    ac_block_heights = get_ac_block_info()

    for item in get_chain_ntx_season_aggregates(season):
        chain = item[0]
        block_height = item[1]

        cols = 'block_hash, txid, block_time, opret, ac_ntx_blockhash, ac_ntx_height'
        conditions = f"block_height={block_height} AND chain='{chain}'"
        last_ntx_result = select_from_table('notarised', cols, conditions)[0]
        ac_ntx_height = last_ntx_result[5]

        ac_block_height = 0
        ntx_lag = "-"

        if chain in ac_block_heights:
            ac_block_height = ac_block_heights[chain]['height']
            ntx_lag = ac_block_height - ac_ntx_height

        row = notarised_chain_season_row()
        row.chain = chain
        row.block_height = block_height
        row.ntx_count = item[3]
        row.kmd_ntx_blockhash = last_ntx_result[0]
        row.kmd_ntx_txid = last_ntx_result[1]
        row.kmd_ntx_blocktime = last_ntx_result[2]
        row.opret = last_ntx_result[3]
        row.ac_ntx_blockhash = last_ntx_result[4]
        row.ac_ntx_height = ac_ntx_height
        row.ac_block_height = ac_block_height
        row.ntx_lag = ntx_lag
        row.season = season
        row.update()


@print_runtime
def update_notarised_count_season_table(season):

    season_ntx_dict = get_season_ntx_dict(season)
    if season in SEASONS_INFO:
        thread_list = []
        for notary in NOTARY_PUBKEYS[season]:
            thread_list.append(
                update_notary_ntx_count_season_thread(
                    season_ntx_dict, season, notary
                )
            )

        for thread in thread_list:
            time.sleep(0.2)
            thread.start()


@print_runtime
def update_KMD_notarisations(unrecorded_KMD_txids):
    logger.info(f"Updating KMD {len(unrecorded_KMD_txids)} notarisations...")

    start = time.time()
    num_unrecorded_KMD_txids = len(unrecorded_KMD_txids)
    
    i = 0
    for txid in unrecorded_KMD_txids:
        i += 1

        row_data = get_notarised_data(txid)
        if row_data is not None: # ignore TXIDs that are not notarisations
            ntx_row = notarised_row()
            ntx_row.chain = row_data[0]
            ntx_row.block_height = row_data[1]
            ntx_row.block_time = row_data[2]
            ntx_row.block_datetime = row_data[3]
            ntx_row.block_hash = row_data[4]
            ntx_row.notaries = row_data[5]
            ntx_row.notary_addresses = row_data[6]
            ntx_row.ac_ntx_blockhash = row_data[7]
            ntx_row.ac_ntx_height = row_data[8]
            ntx_row.txid = row_data[9]
            ntx_row.opret = row_data[10]
            ntx_row.update()

            runtime = int(time.time()-start)
            pct = round(safe_div(i,num_unrecorded_KMD_txids),3)*100
            est_end = int(safe_div(100,pct))*runtime
            logger.info(f"{pct}% :{i}/{num_unrecorded_KMD_txids} records added to db [{runtime}/{est_end} sec]")

    logger.info("Notarised blocks updated!")


@print_runtime
def get_unrecorded_KMD_txids(tip, season, start_block=None, end_block=None):
    
    if not start_block:
        start_block = SEASONS_INFO[season]["start_block"]
    if not end_block:
        end_block = SEASONS_INFO[season]["end_block"]

    if end_block <= tip:
        tip = end_block

    all_txids = []

    logger.info(f"Getting unrecorded notarisations for {season}, blocks {start_block} - {end_block}")

    while tip - start_block > RESCAN_CHUNK_SIZE:
        logger.info("Getting notarization TXIDs from block chain data for blocks")
        logger.info(f"{start_block} to {start_block + RESCAN_CHUNK_SIZE}...")
               
        all_txids += get_ntx_txids(NTX_ADDR, start_block, start_block + RESCAN_CHUNK_SIZE)
        start_block += RESCAN_CHUNK_SIZE

    all_txids += get_ntx_txids(NTX_ADDR, start_block, tip)
    recorded_txids = get_existing_notarised_txids()
    unrecorded_txids = list(set(all_txids) - set(recorded_txids))
    logger.info(f"Scanned txids: {len(all_txids)}")
    logger.info(f"Recorded txids: {len(recorded_txids)}")
    logger.info(f"Unrecorded txids: {len(unrecorded_txids)}")
    return unrecorded_txids


@print_runtime
def get_season_ntx_dict(season):
    season_ntx_dict = prepopulate_season_ntx_dict(season)

    i = 0
    for notary in notaries:
        i += 1
        logger.info(f"[season_totals] {i}/{len(notaries)}: {notary}")
        chain_totals = get_official_ntx_results(season, ["server", "epoch", "chain", "score_value"], None, None, None, notary)
        for item in chain_totals:
            server = item[0]
            epoch = item[1]
            chain = item[2]
            score_value = float(item[3])
            server_epoch_chain_count = item[4]
            server_epoch_chain_score = item[5]

            season_ntx_dict["notaries"][notary]["servers"][server]["epochs"][epoch]["chains"][chain]["notary_server_epoch_chain_ntx_count"] += server_epoch_chain_count
            season_ntx_dict["notaries"][notary]["servers"][server]["epochs"][epoch]["chains"][chain]["notary_server_epoch_chain_ntx_score"] += server_epoch_chain_score

            # Notary Server Epoch Score and Count Totals
            season_ntx_dict["notaries"][notary]["servers"][server]["epochs"][epoch]["notary_server_epoch_ntx_count"] += server_epoch_chain_count
            season_ntx_dict["notaries"][notary]["servers"][server]["epochs"][epoch]["notary_server_epoch_ntx_score"] += server_epoch_chain_score
            season_ntx_dict["notaries"][notary]["servers"][server]["epochs"][epoch]["score_per_ntx"] = score_value

            # Global Epoch Chain Score and Count Totals
            season_ntx_dict["servers"][server]["epochs"][epoch]["chains"][chain]["epoch_chain_ntx_count"] += server_epoch_chain_count
            season_ntx_dict["servers"][server]["epochs"][epoch]["chains"][chain]["epoch_chain_ntx_score"] += server_epoch_chain_score

            # Global Epoch Score and Count Totals
            season_ntx_dict["servers"][server]["epochs"][epoch]["epoch_ntx_count"] += server_epoch_chain_count
            season_ntx_dict["servers"][server]["epochs"][epoch]["epoch_ntx_score"] += server_epoch_chain_score

            # Global Chain Epoch Score and Count Totals
            season_ntx_dict["chains"][chain]["epochs"][epoch]["chain_epoch_ntx_count"] += server_epoch_chain_count
            season_ntx_dict["chains"][chain]["epochs"][epoch]["chain_epoch_ntx_score"] += server_epoch_chain_score
            season_ntx_dict["chains"][chain]["epochs"][epoch]["score_per_ntx"] = score_value

            # Notary Server Score and Count Totals
            if epoch not in ["Unofficial", "LTC", "BTC"]:
                season_ntx_dict["notaries"][notary]["servers"][server]["notary_server_ntx_count"] += server_epoch_chain_count
                season_ntx_dict["notaries"][notary]["servers"][server]["notary_server_ntx_score"] += server_epoch_chain_score

                # Notary Chain Score and Count Totals
                season_ntx_dict["notaries"][notary]["chains"][chain]["notary_chain_ntx_count"] += server_epoch_chain_count
                season_ntx_dict["notaries"][notary]["chains"][chain]["notary_chain_ntx_score"] += server_epoch_chain_score

                # Notary Score and Count Totals
                season_ntx_dict["notaries"][notary]["notary_ntx_count"] += server_epoch_chain_count
                season_ntx_dict["notaries"][notary]["notary_ntx_score"] += server_epoch_chain_score

                # Global Chain Score and Count Totals
                season_ntx_dict["chains"][chain]["chain_ntx_count"] += server_epoch_chain_count
                season_ntx_dict["chains"][chain]["chain_ntx_score"] += server_epoch_chain_score

                # Global Server Score and Count Totals
                season_ntx_dict["servers"][server]["server_ntx_count"] += server_epoch_chain_count
                season_ntx_dict["servers"][server]["server_ntx_score"] += server_epoch_chain_score

                # Global Season Score and Count Totals
                season_ntx_dict["season_ntx_count"] += server_epoch_chain_count
                season_ntx_dict["season_ntx_score"] += server_epoch_chain_score

    for notary in season_ntx_dict["notaries"]:

        # Notary Percentage of Global Count/Score
        season_ntx_dict["notaries"][notary]["notary_ntx_count_pct"] = round(
            safe_div(
                season_ntx_dict["notaries"][notary]["notary_ntx_count"],
                season_ntx_dict["season_ntx_count"]
            )*100,3
        )*13

        season_ntx_dict["notaries"][notary]["notary_ntx_score_pct"] = round(
            safe_div(
                season_ntx_dict["notaries"][notary]["notary_ntx_score"],
                season_ntx_dict["season_ntx_score"]
            )*100,3
        )

        season_ntx_dict["notaries"][notary]["notary_ntx_score"] = float(
            season_ntx_dict["notaries"][notary]["notary_ntx_score"])

        for chain in season_ntx_dict["notaries"][notary]["chains"]:

            # Notary Chain Percentage of Global Chain Count/Score
            season_ntx_dict["notaries"][notary]["chains"][chain]["notary_chain_ntx_count_pct"] = round(
                safe_div(
                    season_ntx_dict["notaries"][notary]["chains"][chain]["notary_chain_ntx_count"],
                    season_ntx_dict["chains"][chain]["chain_ntx_count"]
                )*100,3
            )*13

            season_ntx_dict["notaries"][notary]["chains"][chain]["notary_chain_ntx_score_pct"] = round(
                safe_div(
                    season_ntx_dict["notaries"][notary]["chains"][chain]["notary_chain_ntx_score"],
                    season_ntx_dict["chains"][chain]["chain_ntx_score"]
                )*100,3
            )

            season_ntx_dict["notaries"][notary]["chains"][chain]["notary_chain_ntx_score"] = float(
                season_ntx_dict["notaries"][notary]["chains"][chain]["notary_chain_ntx_score"]
            )

        for server in season_ntx_dict["notaries"][notary]["servers"]:

            # Notary Server Percentage of Global Server Count/Score
            season_ntx_dict["notaries"][notary]["servers"][server]["notary_server_ntx_count_pct"] = round(
                safe_div(
                    season_ntx_dict["notaries"][notary]["servers"][server]["notary_server_ntx_count"],
                    season_ntx_dict["servers"][server]["server_ntx_count"]
                )*100,3
            )*13

            season_ntx_dict["notaries"][notary]["servers"][server]["notary_server_ntx_score_pct"] = round(
                safe_div(
                    season_ntx_dict["notaries"][notary]["servers"][server]["notary_server_ntx_score"],
                    season_ntx_dict["servers"][server]["server_ntx_score"]
                )*100,3
            )

            season_ntx_dict["notaries"][notary]["servers"][server]["notary_server_ntx_score"] = float(
                season_ntx_dict["notaries"][notary]["servers"][server]["notary_server_ntx_score"]
            )

            for epoch in season_ntx_dict["notaries"][notary]["servers"][server]["epochs"]:

                # Notary Epoch Percentage of Global Epoch Count/Score
                season_ntx_dict["notaries"][notary]["servers"][server]["epochs"][epoch]["notary_server_epoch_ntx_count_pct"] = round(
                    safe_div(
                        season_ntx_dict["notaries"][notary]["servers"][server]["epochs"][epoch]["notary_server_epoch_ntx_count"],
                        season_ntx_dict["servers"][server]["epochs"][epoch]["epoch_ntx_count"]
                    )*100,3
                )*13

                season_ntx_dict["notaries"][notary]["servers"][server]["epochs"][epoch]["notary_server_epoch_ntx_score_pct"] = round(
                    safe_div(
                        season_ntx_dict["notaries"][notary]["servers"][server]["epochs"][epoch]["notary_server_epoch_ntx_score"],
                        season_ntx_dict["servers"][server]["epochs"][epoch]["epoch_ntx_score"]
                    )*100,3
                )

                season_ntx_dict["notaries"][notary]["servers"][server]["epochs"][epoch]["notary_server_epoch_ntx_score"] = float(
                    season_ntx_dict["notaries"][notary]["servers"][server]["epochs"][epoch]["notary_server_epoch_ntx_score"]
                )


                for chain in season_ntx_dict["notaries"][notary]["servers"][server]["epochs"][epoch]["chains"]:

                    # Notary Epoch Chain Percentage of Global Epoch Count/Score
                    season_ntx_dict["notaries"][notary]["servers"][server]["epochs"][epoch]["chains"][chain]["notary_server_epoch_chain_ntx_count_pct"] = round(
                        safe_div(
                            season_ntx_dict["notaries"][notary]["servers"][server]["epochs"][epoch]["chains"][chain]["notary_server_epoch_chain_ntx_count"],
                            season_ntx_dict["servers"][server]["epochs"][epoch]["chains"][chain]["epoch_chain_ntx_count"]
                        )*100,3
                    )*13

                    season_ntx_dict["notaries"][notary]["servers"][server]["epochs"][epoch]["chains"][chain]["notary_server_epoch_chain_ntx_score_pct"] = round(
                        safe_div(
                            season_ntx_dict["notaries"][notary]["servers"][server]["epochs"][epoch]["chains"][chain]["notary_server_epoch_chain_ntx_score"],
                            season_ntx_dict["servers"][server]["epochs"][epoch]["chains"][chain]["epoch_chain_ntx_score"]
                        )*100,3
                    )

                    season_ntx_dict["notaries"][notary]["servers"][server]["epochs"][epoch]["chains"][chain]["notary_server_epoch_chain_ntx_score"] = float(
                        season_ntx_dict["notaries"][notary]["servers"][server]["epochs"][epoch]["chains"][chain]["notary_server_epoch_chain_ntx_score"]
                    )

    for chain in season_ntx_dict["chains"]:

        season_ntx_dict["chains"][chain]["chain_ntx_count_pct"] = round(
            safe_div(
                season_ntx_dict["chains"][chain]["chain_ntx_count"],
                season_ntx_dict["season_ntx_count"]
            )*100,3
        )

        season_ntx_dict["chains"][chain]["chain_ntx_score_pct"] = round(
            safe_div(
                season_ntx_dict["chains"][chain]["chain_ntx_score"],season_ntx_dict["season_ntx_score"]
            )*100,3
        )

        season_ntx_dict["chains"][chain]["chain_ntx_score"] = float(
            season_ntx_dict["chains"][chain]["chain_ntx_score"]
        )

        for epoch in season_ntx_dict["chains"][chain]["epochs"]:

            season_ntx_dict["chains"][chain]["epochs"][epoch]["chain_epoch_ntx_count_pct"] = round(
                safe_div(
                    season_ntx_dict["chains"][chain]["epochs"][epoch]["chain_epoch_ntx_count"],
                    season_ntx_dict["season_ntx_count"]
                )*100,3
            )

            season_ntx_dict["chains"][chain]["epochs"][epoch]["chain_epoch_ntx_score_pct"] = round(
                safe_div(
                    season_ntx_dict["chains"][chain]["epochs"][epoch]["chain_epoch_ntx_score"],
                    season_ntx_dict["season_ntx_score"]
                )*100,3
            )

            season_ntx_dict["chains"][chain]["epochs"][epoch]["chain_epoch_ntx_score"] = float(
                season_ntx_dict["chains"][chain]["epochs"][epoch]["chain_epoch_ntx_score"]
            )

    for server in season_ntx_dict["servers"]:

        season_ntx_dict["servers"][server]["server_ntx_count_pct"] = round(
            safe_div(
                season_ntx_dict["servers"][server]["server_ntx_count"],
                season_ntx_dict["season_ntx_count"]
            )*100,3

        )

        season_ntx_dict["servers"][server]["server_ntx_score_pct"] = round(
            safe_div(
                season_ntx_dict["servers"][server]["server_ntx_score"],
                season_ntx_dict["season_ntx_score"]
            )*100,3
        )

        season_ntx_dict["servers"][server]["server_ntx_count"] = float(
            season_ntx_dict["servers"][server]["server_ntx_count"]
        )

    season_ntx_dict["season_ntx_score"] = float(season_ntx_dict["season_ntx_score"])
    return season_ntx_dict


def get_notarised_data(txid):
    try:
        raw_tx = RPC["KMD"].getrawtransaction(txid,1)
        block_hash = raw_tx['blockhash']
        dest_addrs = raw_tx["vout"][0]['scriptPubKey']['addresses']
        if 'blocktime' in raw_tx:
            if len(dest_addrs) > 0:
                if NTX_ADDR in dest_addrs:

                    block_time = raw_tx['blocktime']
                    block_datetime = dt.utcfromtimestamp(block_time)
                    this_block_height = raw_tx['height']

                    if len(raw_tx['vin']) > 1:
                        notary_list, address_list = get_notary_address_lists(raw_tx['vin'])
                        opret = raw_tx['vout'][1]['scriptPubKey']['asm']
                        if opret.find("OP_RETURN") != -1:
                            scriptPubKey_asm = opret.replace("OP_RETURN ","")
                            ac_ntx_blockhash = lil_endian(scriptPubKey_asm[:64])
                            ac_ntx_height = int(lil_endian(scriptPubKey_asm[64:72]),16) 
                            chain = get_opret_ticker(scriptPubKey_asm)
                            chain = decode_opret_coin(chain)
                            # extra_data = get_extra_ntx_data(scriptPubKey_asm)

                            # (some s1 op_returns seem to be decoding differently/wrong.
                            #  This ignores them)

                            if chain.upper() == chain:
                                row_data = (chain, this_block_height, block_time, block_datetime,
                                            block_hash, notary_list, address_list, ac_ntx_blockhash, ac_ntx_height,
                                            txid, opret, "N/A")
                                return row_data
    except Exception as e:
        alerts.send_telegram(f"[{__name__}] [get_notarised_data] TXID: {txid}. Error: {e}")

    return None



# TODO: this data not used or recorded anwhere, but keeping this here for future.
def get_extra_ntx_data(chain, scriptPubKey_asm):
    if chain == "KMD":
        btc_txid = lil_endian(scriptPubKey_asm[72:136])
    elif chain not in noMoM:
        # not sure about this bit, need another source to validate the data
        try:
            start = 72+len(chain)*2+4
            end = 72+len(chain)*2+4+64
            MoM_hash = lil_endian(scriptPubKey_asm[start:end])
            MoM_depth = int(lil_endian(scriptPubKey_asm[end:]),16)
        except Exception as e:
            logger.debug(e)
    return 


@print_runtime
def prepopulate_season_ntx_dict(season):
    season_ntx_dict = get_default_season_ntx_dict()
    notaries = get_season_notaries(season)
    servers = get_notarised_servers(season)
    epochs = get_notarised_epochs(season)
    chains = get_notarised_chains(season)
    server_epochs = lib_epochs.get_server_epochs(season)

    server_epoch_chains = lib_epochs.get_server_epoch_chains(season, server_epochs)

    for chain in chains:
        season_ntx_dict["chains"].update(
            get_default_season_ntx_chains_dict(chain)
        )
        for epoch in epochs:
            season_ntx_dict["chains"][chain]["epochs"].update(
                get_default_season_ntx_chain_epochs_dict(epoch)
            )
    print("Chains Done")

    for server in servers:
        season_ntx_dict["servers"].update(
            get_default_season_ntx_server_dict(server)
        )
        for epoch in server_epochs[server]:
            season_ntx_dict["servers"][server]["epochs"].update(
                get_default_season_ntx_server_epochs_dict(epoch)
            )
            for chain in server_epoch_chains[server][epoch]:
                season_ntx_dict["servers"][server]["epochs"][epoch]["chains"].update(
                    get_default_season_ntx_server_epoch_chains_dict(chain)
                )
    print("Servers Done")

    for notary in notaries:
        season_ntx_dict["notaries"].update(
            get_default_season_ntx_notaries_dict(notary)
        )

        for server in servers:
            season_ntx_dict["notaries"][notary]["servers"].update(
                get_default_season_ntx_notary_servers_dict(server)
            )
            for epoch in server_epochs[server]:
                season_ntx_dict["notaries"][notary]["servers"][server]["epochs"].update(
                    get_default_season_ntx_notary_server_epochs_dict(epoch)
                )
                for chain in server_epoch_chains[server][epoch]:
                    season_ntx_dict["notaries"][notary]["servers"][server]["epochs"][epoch]["chains"].update(
                        get_default_season_ntx_notary_server_epoch_chains_dict(chain)
                    )
                    season_ntx_dict["notaries"][notary]["chains"].update(
                        get_default_season_ntx_notary_chains_dict(chain)
                    )

    print("Notaries Done")
    return season_ntx_dict

@print_runtime
def update_last_notarised_table(season):

    chains = get_notarised_chains(season)
    season_last_ntx = get_season_last_ntx(season)
    notaries = get_season_notaries(season)
    for chain in chains:

        for notary in notaries:
            if notary not in season_last_ntx:
                season_last_ntx.update({
                    notary:{}
                })
            if chain not in season_last_ntx[notary]:
                season_last_ntx[notary].update({chain:0})

            sql = "SELECT MAX(block_height) \
                   FROM notarised \
                   WHERE season = '"+str(season)+"' \
                   AND chain = '"+str(chain)+"' \
                   AND notaries @> "+"'{\""+notary+"\"}'";

            CURSOR.execute(sql)
            resp = CURSOR.fetchone()
            block_height = resp[0]
            if block_height:
                if block_height > season_last_ntx[notary][chain]:
                    sql = "SELECT block_time, txid \
                           FROM notarised \
                           WHERE chain='"+str(chain)+"' \
                           AND block_height="+str(block_height)+";"

                    CURSOR.execute(sql)
                    x = CURSOR.fetchone()
                    block_time = x[0]
                    txid = x[1]
                    row = last_notarised_row()
                    row.notary = notary
                    row.chain = chain
                    row.txid = txid
                    row.block_height = block_height
                    row.block_time = block_time
                    row.season = season
                    row.update()
            else:
                row = last_notarised_row()
                row.notary = notary
                row.chain = chain
                row.txid = "N/A"
                row.block_height = 0
                row.block_time = 0
                row.season = season
                row.update()


def update_daily_chain_ntx(season, day):
    logger.info(f"Getting daily ntx chain counts for {day}")
    chains_aggr_resp = get_notarised_chain_date_aggregates(season, day)
    for item in chains_aggr_resp:
        row = notarised_chain_daily_row()
        row.season = season
        row.chain = item[0]
        row.ntx_count = item[3]
        row.notarised_date = str(day)
        row.update()


@print_runtime
def clean_up_notarised_table(season):
    sql = f"SELECT chain, block_height, block_time, block_datetime, \
            block_hash, notaries, notary_addresses, ac_ntx_blockhash, \
            ac_ntx_height, txid, opret, season,\
            server, epoch, score_value, scored \
            FROM notarised"
    where = []
    if season:
        where.append(f"season = '{season}'")

    if len(where) > 0:
        sql += " WHERE "
        sql += " AND ".join(where)
    sql += " ORDER BY block_time asc;"

    CURSOR.execute(sql)
    results = CURSOR.fetchall()
    for item in results:
        notary_addresses = item[6]
        notary_addresses.sort()
        notaries = item[5]
        notaries.sort()
        row = notarised_row()
        row.chain = item[0]
        row.block_height = item[1]
        row.block_time = item[2]
        row.block_datetime = item[3]
        row.block_hash = item[4]
        row.notaries = notaries
        row.notary_addresses = notary_addresses
        row.ac_ntx_blockhash = item[7]
        row.ac_ntx_height = item[8]
        row.txid = item[9]
        row.opret = item[10]
        row.season = item[11]
        row.server = item[12]
        row.epoch = item[13]
        row.score_value = item[14]
        row.scored = item[15]
        row.update()


def import_ntx(season, server, chain):
    existing_notarised_txids = get_existing_notarised_txids(chain, season, server)
    logger.info(f"existing_notarised_txids: {len(existing_notarised_txids)}")

    import_txids_url = get_ntxid_list_url(season, server, chain, False)
    import_txids = requests.get(import_txids_url).json()["results"]
    logger.info(f"import_txids: {len(import_txids)}")

    new_txids = list(set(import_txids)-set(existing_notarised_txids))
    logger.info(f"new_txids: {len(new_txids)}")

    logger.info(f"Processing ETA: {0.03*len(new_txids)} sec")
    time.sleep(0.02)
    
    j = 0
    coins_list = get_all_coins()

    for txid in new_txids:
        time.sleep(0.02)
        txid_url = get_notarised_txid_url(txid, False)
        r = requests.get(txid_url)        
        j += 1
        logger.info(f">>> Importing {txid} {j}/{len(new_txids)}")

        txid_info_resp = r.json()["results"]

        for txid_info in txid_info_resp:
            ntx_row = notarised_row()
            ntx_row.chain = txid_info["chain"]
            ntx_row.block_height = txid_info["block_height"]
            ntx_row.block_time = txid_info["block_time"]
            ntx_row.block_datetime = txid_info["block_datetime"]
            ntx_row.block_hash = txid_info["block_hash"]
            ntx_row.notaries = txid_info["notaries"]
            ntx_row.ac_ntx_blockhash = txid_info["ac_ntx_blockhash"]
            ntx_row.ac_ntx_height = txid_info["ac_ntx_height"]
            ntx_row.txid = txid_info["txid"]
            ntx_row.opret = txid_info["opret"]
            ntx_row.epoch = txid_info["epoch"]
            ntx_row.season = txid_info["season"]
            ntx_row.server = txid_info["server"]

            if len(txid_info["notary_addresses"]) == 0:

                if ntx_row.chain == "BTC":
                    url = get_notary_btc_txid_url(txid, True)
                    local_info = requests.get(url).json()["results"]
                    ntx_row.notary_addresses = get_local_addresses(local_info)

                elif ntx_row.chain == "LTC":
                    url = get_notary_ltc_txid_url(txid, True)
                    local_info = requests.get(url).json()["results"]
                    ntx_row.notary_addresses = get_local_addresses(local_info)

                else:
                    row_data = get_notarised_data(txid, coins_list)
                    ntx_row.notary_addresses = row_data[6]
                    
            else:
                ntx_row.notary_addresses = txid_info["notary_addresses"]
                ntx_row.season = txid_info["season"]

            ntx_row.update()


def get_new_nn_btc_txids(existing_txids, notary_address, page_break=None, stop_block=None):
    before_block=None
    stop_block = 634774
    page = 1
    exit_loop = False
    api_txids = []
    new_txids = []
    
    if not page_break:
        page_break = API_PAGE_BREAK
    
    if not stop_block:
        stop_block = 634774

    while True:
        # To avoid API limits when running on cron, we dont want to go back too many pages. Set this to 99 when back filling, otherwise 2 pages should be enough.
        if page > page_break:
            break
        logger.info(f"Getting TXIDs from API Page {page}...")
        resp = get_btc_address_txids(notary_address, before_block)
        if "error" in resp:
            logger.info(f"Error in resp: {resp}")
            exit_loop = api_sleep_or_exit(resp, exit=True)
        else:
            page += 1
            if 'txrefs' in resp:
                tx_list = resp['txrefs']
                before_block = tx_list[-1]['block_height']

                for tx in tx_list:
                    api_txids.append(tx['tx_hash'])
                    if tx['tx_hash'] not in new_txids and tx['tx_hash'] not in existing_txids:
                        new_txids.append(tx['tx_hash'])
                        logger.info(f"appended tx {tx}")

                # exit loop if earlier than s4
                if before_block < stop_block:
                    logger.info("No more for s4!")
                    exit_loop = True
            else:
                # exit loop if no more tx for address at api
                logger.info("No more for address!")
                exit_loop = True

        if exit_loop:
            logger.info("exiting address txid loop!")
            break

    num_api_txids = list(set((api_txids)))
    logger.info(f"{len(num_api_txids)} DISTINCT TXIDs counted from API")

    return new_txids


def get_new_notary_txids(notary_address, chain, season):

    existing_txids = []
    if chain == "BTC":
        existing_txids = get_existing_nn_btc_txids(None, None, season, NN_BTC_ADDRESSES_DICT[season][notary_address])
        url = f"{OTHER_SERVER}/api/info/btc_txid_list/?notary={NN_BTC_ADDRESSES_DICT[season][notary_address]}&season={season}"
        logger.info(f"{len(existing_txids)} existing txids in local DB detected for {NN_BTC_ADDRESSES_DICT[season][notary_address]} {notary_address} {season}")
           
    elif chain == "LTC":
        existing_txids = get_existing_nn_ltc_txids(None, None, season, NN_LTC_ADDRESSES_DICT[season][notary_address])
        url = f"{OTHER_SERVER}/api/info/ltc_txid_list/?notary={NN_LTC_ADDRESSES_DICT[season][notary_address]}&season={season}"
        logger.info(f"{len(existing_txids)} existing txids in local DB detected for {NN_LTC_ADDRESSES_DICT[season][notary_address]} {notary_address} {season}")
     
    logger.info(url)
    r = requests.get(url)
    resp = r.json()
    txids = resp['results']

    new_txids = []
    for txid in txids:
        if txid not in existing_txids:
            new_txids.append(txid)
    new_txids = list(set(new_txids))

    if chain == "BTC":
        logger.info(f"{len(new_txids)} extra txids detected for {NN_BTC_ADDRESSES_DICT[season][notary_address]} {notary_address} {season}")
    
    if chain == "LTC":
        logger.info(f"{len(new_txids)} extra txids detected for {NN_LTC_ADDRESSES_DICT[season][notary_address]} {notary_address} {season}")

    return new_txids


def get_new_nn_ltc_txids(existing_txids, notary_address):
    before_block=None
    page = 1
    exit_loop = False
    api_txids = []
    new_txids = []
    while True:
        # To avoid API limits when running on cron, we dont want to go back too many pages. Set this to 99 when back filling, otherwise 2 pages should be enough.
        if page > API_PAGE_BREAK:
            break
        logger.info(f"Getting TXIDs from API Page {page}...")
        resp = get_ltc_address_txids(notary_address, before_block)
        if "error" in resp:
            logger.info(f"Error in resp: {resp}")
            exit_loop = api_sleep_or_exit(resp, exit=True)
        else:
            page += 1
            if 'txrefs' in resp:
                tx_list = resp['txrefs']
                before_block = tx_list[-1]['block_height']

                for tx in tx_list:
                    api_txids.append(tx['tx_hash'])
                    if tx['tx_hash'] not in new_txids and tx['tx_hash'] not in existing_txids:
                        new_txids.append(tx['tx_hash'])
                        logger.info(f"appended tx {tx}")

                # exit loop if earlier than s4
                if before_block < 634774:
                    logger.info("No more for s4!")
                    exit_loop = True
            else:
                # exit loop if no more tx for address at api
                logger.info("No more for address!")
                exit_loop = True

        if exit_loop:
            logger.info("exiting address txid loop!")
            break

    num_api_txids = list(set((api_txids)))
    logger.info(f"{len(num_api_txids)} DISTINCT TXIDs counted from API")

    return new_txids


def import_nn_ltc_txids(season):
    i = 0
    num_addr = len(NOTARY_LTC_ADDRESSES[season])

    for notary_address in NOTARY_LTC_ADDRESSES[season]:
        j = 0
        i += 1
        txid_list = get_new_notary_txids(notary_address, "LTC", season)
        num_txid = len(txid_list)
        logger.info(f">>> Categorising {notary_address} for {season} {i}/{num_addr}")
        logger.info(f"Processing ETA: {0.02*len(txid_list)} sec")

        for txid in txid_list:
            j += 1
            logger.info(f">>> Categorising {txid} for {j}/{num_txid}")
            txid_url = f"{OTHER_SERVER}/api/info/notary_ltc_txid/?txid={txid}"
            time.sleep(0.02)
            r = requests.get(txid_url)

            try:
                resp = r.json()
                tx_resp = resp["results"]

                for row in tx_resp:
                    txid_data = ltc_tx_row()
                    txid_data.txid = txid
                    txid_data.block_hash = row["block_hash"]
                    txid_data.block_height = row["block_height"]
                    txid_data.block_time = row["block_time"]
                    txid_data.block_datetime = row["block_datetime"]
                    txid_data.address = row["address"]
                    txid_data.notary = row["notary"]
                    txid_data.category = row["category"]
                    txid_data.season = row["season"]
                    txid_data.input_index = row["input_index"]
                    txid_data.input_sats = row["input_sats"]
                    txid_data.output_index = row["output_index"]
                    txid_data.output_sats = row["output_sats"]
                    txid_data.fees = row["fees"]
                    txid_data.num_inputs = row["num_inputs"]
                    txid_data.num_outputs = row["num_outputs"]
                    txid_data.update()
                    
            except Exception as e:
                logger.error(e)
                logger.error(f"Something wrong with API? {txid_url}")


def import_nn_btc_txids(season):
    i = 0
    num_addr = len(NOTARY_BTC_ADDRESSES[season])
    addresses = list(NOTARY_BTC_ADDRESSES[season])
    while len(addresses) > 0:
        notary_address = random.choice(addresses)
        i += 1
        logger.info(f">>> Categorising {notary_address} for {season} {i}/{num_addr}")
        txid_list = get_new_notary_txids(notary_address, "BTC", season)
        logger.info(f"Processing ETA: {0.02*len(txid_list)} sec")

        j = 0
        num_txid = len(txid_list)
        for txid in txid_list:
            j += 1
            logger.info(f">>> Categorising {txid} for {j}/{num_txid}")
            txid_url = get_notary_btc_txid_url(txid, False)
            time.sleep(0.02)
            r = requests.get(txid_url)
            try:
                resp = r.json()
                tx_resp = resp["results"]
                for row in tx_resp:
                    txid_data = tx_row()
                    txid_data.txid = txid
                    txid_data.block_hash = row["block_hash"]
                    txid_data.block_height = row["block_height"]
                    txid_data.block_time = row["block_time"]
                    txid_data.block_datetime = row["block_datetime"]
                    txid_data.address = row["address"]
                    txid_data.notary = row["notary"]
                    txid_data.category = row["category"]
                    txid_data.season = row["season"]
                    txid_data.input_index = row["input_index"]
                    txid_data.input_sats = row["input_sats"]
                    txid_data.output_index = row["output_index"]
                    txid_data.output_sats = row["output_sats"]
                    txid_data.fees = row["fees"]
                    txid_data.num_inputs = row["num_inputs"]
                    txid_data.num_outputs = row["num_outputs"]
                    txid_data.update()
            except Exception as e:
                logger.error(e)
                logger.error(f"Something wrong with API? {txid_url}")
        addresses.remove(notary_address)



def get_chain_ntx_count_dict(season, day):
    # get daily ntx total for each chain
    chain_ntx_count_dict = {}
    chains_aggr_resp = get_notarised_chain_date_aggregates(season, day)

    for item in chains_aggr_resp:
        chain = item[0]
        max_block = item[1]
        max_blocktime = item[2]
        ntx_count = item[3]
        chain_ntx_count_dict.update({chain:ntx_count})
    return chain_ntx_count_dict


def get_notary_ntx_count_dict(season, day):
    notary_ntx_count_dict = {}
    notarised_on_day = get_notarised_for_day(season, day)

    for item in notarised_on_day:
        notaries = item[1]
        chain = item[0]
        for notary in notaries:
            if notary not in notary_ntx_count_dict:
                notary_ntx_count_dict.update({notary:{}})
            if chain not in notary_ntx_count_dict[notary]:
                notary_ntx_count_dict[notary].update({chain:1})
            else:
                count = notary_ntx_count_dict[notary][chain]+1
                notary_ntx_count_dict[notary].update({chain:count})

    return notary_ntx_count_dict


def get_notary_count_categorized(notary_ntx_count_dict, chain_ntx_count_dict):

    season_main_coins = requests.get(
                        get_dpow_server_coins_url(season, 'Main')
                    ).json()["results"]

    season_3P_coins = requests.get(
                        get_dpow_server_coins_url(season, 'Third_Party')
                    ).json()["results"]

    # iterate over notary chain counts to calculate scoring category counts.
    notary_counts = {}
    notary_ntx_pct = {}

    for notary in notary_ntx_count_dict:
        notary_ntx_pct.update({notary:{}})
        notary_counts.update({notary:{
                "btc_count":0,
                "antara_count":0,
                "third_party_count":0,
                "other_count":0,
                "total_ntx_count":0
            }})

        for chain in notary_ntx_count_dict[notary]:
            if chain == "KMD":
                count = notary_counts[notary]["btc_count"] + notary_ntx_count_dict[notary][chain]
                notary_counts[notary].update({"btc_count":count})
            elif chain in season_main_coins:
                count = notary_counts[notary]["antara_count"] + notary_ntx_count_dict[notary][chain]
                notary_counts[notary].update({"antara_count":count})
            elif chain in season_3P_coins:
                count = notary_counts[notary]["third_party_count"] + notary_ntx_count_dict[notary][chain]
                notary_counts[notary].update({"third_party_count":count})
            else:
                count = notary_counts[notary]["other_count"] + notary_ntx_count_dict[notary][chain]
                notary_counts[notary].update({"other_count":count})

            count = notary_counts[notary]["total_ntx_count"] + notary_ntx_count_dict[notary][chain]
            notary_counts[notary].update({"total_ntx_count":count})

            pct = round(notary_ntx_count_dict[notary][chain] / chain_ntx_count_dict[chain] * 100, 2)
            notary_ntx_pct[notary].update({chain:pct})

    return notary_counts, notary_ntx_pct
