#!/usr/bin/env python3
import time
import random
import datetime
from datetime import datetime as dt

import lib_api as api
import lib_rpc as rpc
import lib_urls as urls
import lib_query as query
import lib_helper as helper
import lib_crypto as crypto
import lib_validate as validate
from decorators import print_runtime
from lib_const import *
from models import *


# Notarised table
class notarised():
    def __init__(self, season, rescan=False):
        self.season = season
        self.rescan = rescan
        self.start_block = SEASONS_INFO[self.season]["start_block"]
        self.chain_tip = int(RPC["KMD"].getblockcount())
        self.existing_txids = query.get_existing_notarised_txids()

        # Set end block for season
        if "post_season_end_block" in SEASONS_INFO[self.season]:
            self.end_block = SEASONS_INFO[self.season]["post_season_end_block"]
        else:
            self.end_block = SEASONS_INFO[self.season]["end_block"]

        if not self.rescan:
            # scan last hour's worth of blocks by default
            self.start_block = self.chain_tip - 24 * 60

        if self.end_block <= self.chain_tip:
            self.chain_tip = self.end_block



    @print_runtime
    def update_table(self):
        logger.info(f"Processing notarisations for {self.season}, blocks {self.start_block} - {self.end_block}")
        if not self.rescan:
            unrecorded_KMD_txids = self.get_missing_txids_list(self.start_block, self.end_block)
            self.update_notarisations(unrecorded_KMD_txids)

        else:
            logger.info(f"Recanning notarisations for {self.season}, blocks {self.start_block} - {self.end_block}")
            windows = [(i, i + RESCAN_CHUNK_SIZE) for i in range(self.start_block, self.end_block, RESCAN_CHUNK_SIZE)]
            if OTHER_SERVER.find("stats") == -1:
                windows.reverse()
            i = 0
            while len(windows) > 0:
                i += 1
                window = random.choice(windows)
                logger.info(f"Processing notarisations for blocks in window {window[0]} - {window[1]} ({i} done, {len(windows)} remaining...)")
                unrecorded_KMD_txids = self.get_missing_txids_list(window[0], window[1])
                self.update_notarisations(unrecorded_KMD_txids)
                windows.remove(window)
                self.existing_txids += unrecorded_KMD_txids
                time.sleep(0.1)


    @print_runtime
    def get_missing_txids_list(self, start, end):
        logger.info(f"Getting unrecorded notarisation TXIDs for {self.season}, blocks {start} - {end}")

        all_txids = []
        while self.chain_tip - start > RESCAN_CHUNK_SIZE:
            logger.info(f"Adding {start} to {start + RESCAN_CHUNK_SIZE} ntx address txids...")
            all_txids += rpc.get_ntx_txids(start, start + RESCAN_CHUNK_SIZE)
            start += RESCAN_CHUNK_SIZE
            time.sleep(0.1)

        all_txids += rpc.get_ntx_txids(start, self.chain_tip)

        new_txids = list(set(all_txids) - set(self.existing_txids))
        logger.info(f"New TXIDs: {len(new_txids)}")
        random.shuffle(new_txids)
        return new_txids


    @print_runtime
    def update_notarisations(self, unrecorded_KMD_txids):
        logger.info(f"Updating KMD {len(unrecorded_KMD_txids)} notarisations...")
        for txid in unrecorded_KMD_txids:
            row_data = self.get_ntx_data(txid)
            if row_data is not None: # ignore TXIDs that are not notarisations
                ntx_row = self.get_rpc_row(row_data)
                ntx_row.update()


    def get_rpc_row(self, row_data):
        ntx_row = notarised_row()
        ntx_row.season = self.season
        ntx_row.coin = row_data[0]
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
        return ntx_row


    def get_import_row(self, txid_info):
        ntx_row = notarised_row()
        ntx_row.coin = txid_info["coin"]
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

            if ntx_row.coin == "BTC":
                url = urls.get_notary_btc_txid_url(ntx_row.txid, True)
                local_info = requests.get(url).json()["results"]
                ntx_row.notary_addresses = get_local_addresses(local_info)

            elif ntx_row.coin == "LTC":
                url = urls.get_notary_ltc_txid_url(ntx_row.txid, True)
                local_info = requests.get(url).json()["results"]
                ntx_row.notary_addresses = helper.get_local_addresses(local_info)

        else:
            ntx_row.notary_addresses = txid_info["notary_addresses"]
            ntx_row.season = txid_info["season"]
        return ntx_row


    def get_ntx_data(self, txid):
        try:
            raw_tx = RPC["KMD"].getrawtransaction(txid,1)
            if 'blocktime' in raw_tx:
                block_hash = raw_tx['blockhash']
                dest_addrs = raw_tx["vout"][0]['scriptPubKey']['addresses']
                if len(dest_addrs) > 0:
                    if NTX_ADDR in dest_addrs:

                        block_time = raw_tx['blocktime']
                        block_datetime = dt.utcfromtimestamp(block_time)
                        this_block_height = raw_tx['height']

                        if len(raw_tx['vin']) > 1:
                            notary_list, address_list = helper.get_notary_address_lists(raw_tx['vin'])
                            opret = raw_tx['vout'][1]['scriptPubKey']['asm']
                            if opret.find("OP_RETURN") != -1:
                                scriptPubKey_asm = opret.replace("OP_RETURN ","")
                                ac_ntx_blockhash = crypto.lil_endian(scriptPubKey_asm[:64])
                                ac_ntx_height = int(crypto.lil_endian(scriptPubKey_asm[64:72]),16)

                                coin = crypto.get_opret_ticker(scriptPubKey_asm)
                                # extra_data = get_extra_ntx_data(scriptPubKey_asm)

                                # Gets rid of extra data by matching to known coins
                                # TODO: This could potentially misidentify - be vigilant.
                                for x in KNOWN_COINS:
                                    if len(x) > 2 and x not in EXCLUDE_DECODE_OPRET_COINS:
                                        if coin.endswith(x):
                                            coin = x

                                # (some s1 op_returns seem to be decoding differently/wrong.
                                #  This ignores them)
                                if coin.upper() == coin:
                                    row_data = (coin, this_block_height, block_time, block_datetime,
                                                block_hash, notary_list, address_list, ac_ntx_blockhash,
                                                ac_ntx_height, txid, opret, "N/A")
                                    return row_data

        except Exception as e:
            alerts.send_telegram(f"[{__name__}] [get_ntx_data] TXID: {txid}. Error: {e}")

        return None


    @print_runtime
    def clean_up(self):
        ''' Re-processes existing data to let model validation enforce validation '''

        results = query.get_notarised_data_for_season(self.season)
        for item in results:
            notary_addresses = item[6]
            notary_addresses.sort()
            notaries = item[5]
            notaries.sort()
            row = notarised_row()
            row.coin = item[0]
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


    @print_runtime
    def import_ntx(self, server, coin):

        url = urls.get_ntxid_list_url(self.season, server, coin, False)
        r = requests.get(url)
        if r.status_code == 429:
            time.sleep(0.5)
            return
        import_txids = r.json()["results"]

        new_txids = list(set(import_txids)-set(self.existing_txids))
        logger.info(f"NTX TXIDs to import: {len(new_txids)}")
        logger.info(f"Processing ETA: {0.03*len(new_txids)} sec")

        for txid in new_txids:
            time.sleep(0.2)
            txid_url = urls.get_notarised_txid_url(txid, False)
            r = requests.get(txid_url)
            try:
                for txid_info in r.json()["results"]:
                    ntx_row = self.get_import_row(txid_info)
                    ntx_row.update()
            except Exception as e:
                logger.error(f"Error importing {txid}: {e} | r.text: {r.text}")


# Daily Notarised tables
class ntx_daily_stats():
    def __init__(self, season, rescan=False):
        self.season = season
        self.rescan = rescan
        if "Main" in SEASONS_INFO[self.season]["servers"]:
            self.dpow_main_coins = SEASONS_INFO[self.season]["servers"]["Main"]["coins"]
        if "Third_Party" in SEASONS_INFO[self.season]["servers"]:
            self.dpow_3p_coins = SEASONS_INFO[self.season]["servers"]["Third_Party"]["coins"]

    def update_daily_ntx_tables(self):
        season_start_dt = dt.utcfromtimestamp(SEASONS_INFO[self.season]["start_time"])
        season_end_dt = dt.utcfromtimestamp(SEASONS_INFO[self.season]["end_time"])
        start = season_start_dt.date()
        end = datetime.date.today()

        if time.time() > SEASONS_INFO[self.season]["end_time"]:
            end = season_end_dt.date()

        if not self.rescan:
            logger.info(f"Starting {self.season} scan from 3 days ago...")
            start = end - datetime.timedelta(days=3)

        logger.info(f"Updating [notarised_coin_daily] for {self.season}")
        logger.info(f"Scanning {start} to {end}")

        while start <= end:
            logger.info(f"Updating [notarised_coin_daily] for {start}")
            self.day = start
            self.coins_aggr_resp = query.get_notarised_coin_date_aggregates(self.season, self.day)
            self.coin_ntx_count_dict = self.get_coin_ntx_count_dict_for_day()
            self.notary_ntx_count_dict = self.get_notary_ntx_count_dict_for_day()
            self.notary_counts, self.notary_ntx_pct = self.get_daily_ntx_count_pct()
            self.update_daily_coin_ntx()
            self.update_daily_count_ntx()
            start += datetime.timedelta(days=1)


    def update_daily_coin_ntx(self):
        logger.info(f"Getting daily ntx coin counts for {self.day}")
        for item in self.coins_aggr_resp:
            row = notarised_coin_daily_row()
            row.season = self.season
            row.coin = item[0]
            row.ntx_count = item[3]
            row.notarised_date = str(self.day)
            row.update()


    def update_daily_count_ntx(self):

        # calculate notary ntx percentage for coins and add row to db table.
        for notary in self.notary_counts:
            ntx_count_daily_row = notarised_count_daily_row()
            ntx_count_daily_row.notary = notary
            ntx_count_daily_row.master_server_count = self.notary_counts[notary]['master_server_count']
            ntx_count_daily_row.main_server_count = self.notary_counts[notary]['main_server_count']
            ntx_count_daily_row.third_party_server_count = self.notary_counts[notary]['third_party_server_count']
            ntx_count_daily_row.other_server_count = self.notary_counts[notary]['other_server_count']
            ntx_count_daily_row.total_ntx_count = self.notary_counts[notary]['total_ntx_count']
            ntx_count_daily_row.coin_ntx_counts = json.dumps(self.notary_ntx_count_dict[notary])
            ntx_count_daily_row.coin_ntx_pct = json.dumps(self.notary_ntx_pct[notary])
            ntx_count_daily_row.season = self.season
            ntx_count_daily_row.notarised_date = self.day
            ntx_count_daily_row.update()


    def get_daily_ntx_count_pct(self):

        # iterate over notary coin counts to calculate scoring category counts.
        notary_counts = {}
        notary_ntx_pct = {}

        for notary in self.notary_ntx_count_dict:
            notary_ntx_pct.update({notary:{}})
            notary_counts.update({notary:{
                    "master_server_count":0,
                    "main_server_count":0,
                    "third_party_server_count":0,
                    "other_server_count":0,
                    "total_ntx_count":0
                }})

            for coin in self.notary_ntx_count_dict[notary]:
                if coin == "KMD":
                    count = notary_counts[notary]["master_server_count"] + self.notary_ntx_count_dict[notary][coin]
                    notary_counts[notary].update({"master_server_count":count})
                elif coin in self.dpow_main_coins:
                    count = notary_counts[notary]["main_server_count"] + self.notary_ntx_count_dict[notary][coin]
                    notary_counts[notary].update({"main_server_count":count})
                elif coin in self.dpow_3p_coins:
                    count = notary_counts[notary]["third_party_server_count"] + self.notary_ntx_count_dict[notary][coin]
                    notary_counts[notary].update({"third_party_server_count":count})
                else:
                    count = notary_counts[notary]["other_server_count"] + self.notary_ntx_count_dict[notary][coin]
                    notary_counts[notary].update({"other_server_count":count})

                count = notary_counts[notary]["total_ntx_count"] + self.notary_ntx_count_dict[notary][coin]
                notary_counts[notary].update({"total_ntx_count":count})

                pct = round(self.notary_ntx_count_dict[notary][coin] / self.coin_ntx_count_dict[coin] * 100, 2)
                notary_ntx_pct[notary].update({coin:pct})

        return notary_counts, notary_ntx_pct


    def get_coin_ntx_count_dict_for_day(self):
        # get daily ntx total for each coin
        coin_ntx_count_dict = {}

        for item in self.coins_aggr_resp:
            coin = item[0]
            max_block = item[1]
            max_blocktime = item[2]
            ntx_count = item[3]
            coin_ntx_count_dict.update({coin:ntx_count})

        return coin_ntx_count_dict


    def get_notary_ntx_count_dict_for_day(self):
        notary_ntx_count_dict = {}
        notarised_on_day = query.get_notarised_for_day(self.season, self.day)

        for item in notarised_on_day:
            notaries = item[1]
            coin = item[0]
            for notary in notaries:
                if notary not in notary_ntx_count_dict:
                    notary_ntx_count_dict.update({notary:{}})
                if coin not in notary_ntx_count_dict[notary]:
                    notary_ntx_count_dict[notary].update({coin:1})
                else:
                    count = notary_ntx_count_dict[notary][coin]+1
                    notary_ntx_count_dict[notary].update({coin:count})

        return notary_ntx_count_dict


# Season Notarised tables
class ntx_season_stats():
    def __init__(self, season):
        self.season = season
        self.season_ntx_dict = {
            "ntx_count":0,
            "ntx_score":0,
            "coins":{},
            "notaries":{},
            "servers":{}
        }

        # {'KMD': {'KMD': 0.0325}, 'LTC': {'LTC': 0}, 'Main': {'Epoch_0': 0.03781739, 'Epoch_1': 0.03953636, 'Epoch_2': 0.03781739}, 'Third_Party': {'Epoch_0': 0.01628333, 'Epoch_1': 0.01395714, 'Epoch_2': 0.0122125, 'Epoch_3': 0.01395714, 'Epoch_4': 0.0122125}}

    @print_runtime
    def update_ntx_season_stats_tables(self):
        if self.season in SEASONS_INFO:
            self.build_season_ntx_dict()
            for coin in self.season_coins:
                row = self.get_coin_row(coin)
                row.update()

            for notary in self.season_notaries:
                row = self.get_notary_row(notary)
                row.update()

            for server in self.season_servers:
                row = self.get_server_row(server)
                row.update()


    def get_coin_row(self, coin):
        row = coin_ntx_season_row()
        row.season = self.season
        row.coin = coin
        row.coin_data = json.dumps(self.season_ntx_dict["coins"][coin])
        row.timestamp = time.time()

        return row


    def get_notary_row(self, notary):
        row = notary_ntx_season_row()
        row.season = self.season
        row.notary = notary
        row.notary_data = json.dumps(self.season_ntx_dict["notaries"][notary])
        row.timestamp = time.time()

        return row


    def get_server_row(self, server):
        row = server_ntx_season_row()
        row.season = self.season
        row.server = server
        row.server_data = json.dumps(self.season_ntx_dict["servers"][server])
        row.timestamp = time.time()

        return row


    def get_default_ntx_item_dict(self, item):
        return {
            item: {
                "ntx_count":0,
                "ntx_score":0,
                "pct_of_season_ntx_count":0,
                "pct_of_season_ntx_score":0,
            }
        }


    def prepopulate(self):
        self.season_coins = helper.get_season_coins(self.season)
        self.season_servers = list(set(helper.get_season_servers(self.season)).difference({"Unofficial", "LTC", "BTC", "None"}))
        self.season_notaries = helper.get_season_notaries(self.season)
        self.epoch_scores_dict = validate.get_epoch_scores_dict(self.season)

        # Prefill Coins Dicts
        for coin in self.season_coins:
            self.season_ntx_dict["coins"].update(self.get_default_ntx_item_dict(coin))
            self.season_ntx_dict["coins"][coin].update({"servers": {}})
            self.season_ntx_dict["coins"][coin].update({"notaries": {}})

            for server in self.season_servers:
                if coin in helper.get_season_coins(self.season, server):
                    self.season_ntx_dict["coins"][coin]["servers"].update(self.get_default_ntx_item_dict(server))
                    self.season_ntx_dict["coins"][coin]["servers"][server].update({"epochs": {}})
                    self.season_ntx_dict["coins"][coin]["servers"][server].update({"notaries": {}})

                    server_epochs = list(set(get_season_server_epochs(self.season, server)).difference({"Unofficial", "None"}))

                    for epoch in server_epochs:
                        if coin in helper.get_season_coins(self.season, server, epoch):
                            self.season_ntx_dict["coins"][coin]["servers"][server]["epochs"].update(self.get_default_ntx_item_dict(epoch))
                            self.season_ntx_dict["coins"][coin]["servers"][server]["epochs"][epoch].update({"notaries": {}})
                            self.season_ntx_dict["coins"][coin]["servers"][server]["epochs"][epoch]["score_per_ntx"] = float(self.epoch_scores_dict[server][epoch])

                            for notary in self.season_notaries:
                                self.season_ntx_dict["coins"][coin]["servers"][server]["epochs"][epoch]["notaries"].update(self.get_default_ntx_item_dict(notary))

                    for notary in self.season_notaries:
                        self.season_ntx_dict["coins"][coin]["servers"][server]["notaries"].update(self.get_default_ntx_item_dict(notary))

            for notary in self.season_notaries:
                self.season_ntx_dict["coins"][coin]["notaries"].update(self.get_default_ntx_item_dict(notary))


        # Prefill Notary Dicts
        for notary in self.season_notaries:
            self.season_ntx_dict["notaries"].update(self.get_default_ntx_item_dict(notary))
            self.season_ntx_dict["notaries"][notary].update({"coins": {}})
            self.season_ntx_dict["notaries"][notary].update({"servers": {}})

            for server in self.season_servers:
                self.season_ntx_dict["notaries"][notary]["servers"].update(self.get_default_ntx_item_dict(server))
                self.season_ntx_dict["notaries"][notary]["servers"][server].update({"coins": {}})
                self.season_ntx_dict["notaries"][notary]["servers"][server].update({"epochs": {}})

                server_epochs = list(set(get_season_server_epochs(self.season, server)).difference({"Unofficial", "None"}))

                for epoch in server_epochs:
                    self.season_ntx_dict["notaries"][notary]["servers"][server]["epochs"].update(self.get_default_ntx_item_dict(epoch))
                    self.season_ntx_dict["notaries"][notary]["servers"][server]["epochs"][epoch].update({"coins": {}})
                    self.season_ntx_dict["notaries"][notary]["servers"][server]["epochs"][epoch]["score_per_ntx"] = float(self.epoch_scores_dict[server][epoch])

                    for coin in helper.get_season_coins(self.season, server, epoch):
                        self.season_ntx_dict["notaries"][notary]["servers"][server]["epochs"][epoch]["coins"].update(self.get_default_ntx_item_dict(coin))

                for coin in helper.get_season_coins(self.season, server):
                    self.season_ntx_dict["notaries"][notary]["servers"][server]["coins"].update(self.get_default_ntx_item_dict(coin))

            for coin in self.season_coins:
                self.season_ntx_dict["notaries"][notary]["coins"].update(self.get_default_ntx_item_dict(coin))


        # Prefill Server Dicts
        for server in self.season_servers:
            self.season_ntx_dict["servers"].update(self.get_default_ntx_item_dict(server))
            self.season_ntx_dict["servers"][server].update({"coins": {}})
            self.season_ntx_dict["servers"][server].update({"epochs": {}})
            self.season_ntx_dict["servers"][server].update({"notaries": {}})

            for coin in helper.get_season_coins(self.season, server):
                self.season_ntx_dict["servers"][server]["coins"].update(self.get_default_ntx_item_dict(coin))
                self.season_ntx_dict["servers"][server]["coins"][coin].update({"notaries": {}})

                for notary in self.season_notaries:
                    self.season_ntx_dict["servers"][server]["coins"][coin]["notaries"].update(self.get_default_ntx_item_dict(notary))

            server_epochs = list(set(get_season_server_epochs(self.season, server)).difference({"Unofficial", "None"}))
            for epoch in server_epochs:

                epoch_coins = helper.get_season_coins(self.season, server, epoch)
                self.season_ntx_dict["servers"][server]["epochs"].update(self.get_default_ntx_item_dict(epoch))
                self.season_ntx_dict["servers"][server]["epochs"][epoch].update({"coins": {}})
                self.season_ntx_dict["servers"][server]["epochs"][epoch].update({"notaries": {}})
                self.season_ntx_dict["servers"][server]["epochs"][epoch]["score_per_ntx"] = float(self.epoch_scores_dict[server][epoch])

                for coin in epoch_coins:
                    self.season_ntx_dict["servers"][server]["epochs"][epoch]["coins"].update(self.get_default_ntx_item_dict(coin))
                    self.season_ntx_dict["servers"][server]["epochs"][epoch]["coins"][coin].update({"notaries": {}})

                    for notary in self.season_notaries:
                        self.season_ntx_dict["servers"][server]["epochs"][epoch]["coins"][coin]["notaries"].update(self.get_default_ntx_item_dict(notary))

                for notary in self.season_notaries:
                    self.season_ntx_dict["servers"][server]["epochs"][epoch]["notaries"].update(self.get_default_ntx_item_dict(notary))

            for notary in self.season_notaries:
                self.season_ntx_dict["servers"][server]["notaries"].update(self.get_default_ntx_item_dict(notary))

        return self.season_ntx_dict


    def add_scores_counts(self):

        i = 0
        for notary in self.season_notaries:

            i += 1
            logger.info(f"[season_totals] {self.season} {i}/{len(SEASONS_INFO[self.season]['notaries'])}: {notary}")
            official_ntx_results = query.get_official_ntx_results(self.season, ["server", "epoch", "coin"], None, None, None, notary)

            for item in official_ntx_results:
                server = item[0]
                epoch = item[1]
                coin = item[2]
                server_epoch_coin_count = item[3]
                server_epoch_coin_score = item[4]
                print(item)

                if len({server, epoch}.intersection({"Unofficial", "LTC", "BTC", "None"})) == 0:

                    if coin != 'KMD' or (coin == server and server == epoch):
                        # Global Season Score and Count Totals
                        self.season_ntx_dict["ntx_count"] += server_epoch_coin_count
                        self.season_ntx_dict["ntx_score"] += float(server_epoch_coin_score)

                        # Global Coin Score and Count Totals
                        self.season_ntx_dict["coins"][coin]["ntx_count"] += server_epoch_coin_count
                        self.season_ntx_dict["coins"][coin]["ntx_score"] += float(server_epoch_coin_score)

                        # Global Coin Notary Score and Count Totals
                        self.season_ntx_dict["coins"][coin]["notaries"][notary]["ntx_count"] += server_epoch_coin_count
                        self.season_ntx_dict["coins"][coin]["notaries"][notary]["ntx_score"] += float(server_epoch_coin_score)

                        # Global Coin Server Score and Count Totals
                        self.season_ntx_dict["coins"][coin]["servers"][server]["ntx_count"] += server_epoch_coin_count
                        self.season_ntx_dict["coins"][coin]["servers"][server]["ntx_score"] += float(server_epoch_coin_score)

                        # Global Coin Server Notary Score and Count Totals
                        self.season_ntx_dict["coins"][coin]["servers"][server]["notaries"][notary]["ntx_count"] += server_epoch_coin_count
                        self.season_ntx_dict["coins"][coin]["servers"][server]["notaries"][notary]["ntx_score"] += float(server_epoch_coin_score)

                        logger.info(f"{coin} {self.season} {server} {epoch}")
                        # Global Coin Server Epoch Score and Count Totals
                        self.season_ntx_dict["coins"][coin]["servers"][server]["epochs"][epoch]["ntx_count"] += server_epoch_coin_count
                        self.season_ntx_dict["coins"][coin]["servers"][server]["epochs"][epoch]["ntx_score"] += float(server_epoch_coin_score)

                        # Global Coin Server Epoch Notary Score and Count Totals
                        self.season_ntx_dict["coins"][coin]["servers"][server]["epochs"][epoch]["notaries"][notary]["ntx_count"] += server_epoch_coin_count
                        self.season_ntx_dict["coins"][coin]["servers"][server]["epochs"][epoch]["notaries"][notary]["ntx_score"] += float(server_epoch_coin_score)


                        # Global Notary Score and Count Totals
                        self.season_ntx_dict["notaries"][notary]["ntx_count"] += server_epoch_coin_count
                        self.season_ntx_dict["notaries"][notary]["ntx_score"] += float(server_epoch_coin_score)

                        # Notary Coin Score and Count Totals
                        self.season_ntx_dict["notaries"][notary]["coins"][coin]["ntx_count"] += server_epoch_coin_count
                        self.season_ntx_dict["notaries"][notary]["coins"][coin]["ntx_score"] += float(server_epoch_coin_score)

                        # Notary Server Score and Count Totals
                        self.season_ntx_dict["notaries"][notary]["servers"][server]["ntx_count"] += server_epoch_coin_count
                        self.season_ntx_dict["notaries"][notary]["servers"][server]["ntx_score"] += float(server_epoch_coin_score)

                        # Notary Server Coin Score and Count Totals
                        self.season_ntx_dict["notaries"][notary]["servers"][server]["coins"][coin]["ntx_count"] += server_epoch_coin_count
                        self.season_ntx_dict["notaries"][notary]["servers"][server]["coins"][coin]["ntx_score"] += float(server_epoch_coin_score)

                        # Notary Server Epoch Score and Count Totals
                        self.season_ntx_dict["notaries"][notary]["servers"][server]["epochs"][epoch]["ntx_count"] += server_epoch_coin_count
                        self.season_ntx_dict["notaries"][notary]["servers"][server]["epochs"][epoch]["ntx_score"] += float(server_epoch_coin_score)

                        # Notary Server Epoch Coin Score and Count Totals
                        self.season_ntx_dict["notaries"][notary]["servers"][server]["epochs"][epoch]["coins"][coin]["ntx_count"] += server_epoch_coin_count
                        self.season_ntx_dict["notaries"][notary]["servers"][server]["epochs"][epoch]["coins"][coin]["ntx_score"] += float(server_epoch_coin_score)


                        # Global Server Score and Count Totals
                        self.season_ntx_dict["servers"][server]["ntx_count"] += server_epoch_coin_count
                        self.season_ntx_dict["servers"][server]["ntx_score"] += float(server_epoch_coin_score)

                        # Global Server Epoch Coin Score and Count Totals
                        self.season_ntx_dict["servers"][server]["coins"][coin]["ntx_count"] += server_epoch_coin_count
                        self.season_ntx_dict["servers"][server]["coins"][coin]["ntx_score"] += float(server_epoch_coin_score)

                        # Global Server Notary Score and Count Totals
                        self.season_ntx_dict["servers"][server]["coins"][coin]["notaries"][notary]["ntx_count"] += server_epoch_coin_count
                        self.season_ntx_dict["servers"][server]["coins"][coin]["notaries"][notary]["ntx_score"] += float(server_epoch_coin_score)

                        # Global Server Epoch Score and Count Totals
                        self.season_ntx_dict["servers"][server]["epochs"][epoch]["ntx_count"] += server_epoch_coin_count
                        self.season_ntx_dict["servers"][server]["epochs"][epoch]["ntx_score"] += float(server_epoch_coin_score)

                        # Global Server Epoch Coin Score and Count Totals
                        self.season_ntx_dict["servers"][server]["epochs"][epoch]["coins"][coin]["ntx_count"] += server_epoch_coin_count
                        self.season_ntx_dict["servers"][server]["epochs"][epoch]["coins"][coin]["ntx_score"] += float(server_epoch_coin_score)

                        # Global Server Epoch Coin Notary Score and Count Totals
                        self.season_ntx_dict["servers"][server]["epochs"][epoch]["coins"][coin]["notaries"][notary]["ntx_count"] += server_epoch_coin_count
                        self.season_ntx_dict["servers"][server]["epochs"][epoch]["coins"][coin]["notaries"][notary]["ntx_score"] += float(server_epoch_coin_score)

                        # Global Server Epoch Notary Score and Count Totals
                        self.season_ntx_dict["servers"][server]["epochs"][epoch]["notaries"][notary]["ntx_count"] += server_epoch_coin_count
                        self.season_ntx_dict["servers"][server]["epochs"][epoch]["notaries"][notary]["ntx_score"] += float(server_epoch_coin_score)

                        # Global Server Notary Score and Count Totals
                        self.season_ntx_dict["servers"][server]["notaries"][notary]["ntx_count"] += server_epoch_coin_count
                        self.season_ntx_dict["servers"][server]["notaries"][notary]["ntx_score"] += float(server_epoch_coin_score)

        # Div by 13 for non-notary related ntx_counts
        self.season_ntx_dict["ntx_count"] = round(self.season_ntx_dict["ntx_count"] / 13)

        for coin in self.season_ntx_dict["coins"]:
            self.season_ntx_dict["coins"][coin]["ntx_count"]\
                = round(self.season_ntx_dict["coins"][coin]["ntx_count"] / 13)

            for server in self.season_ntx_dict["coins"][coin]["servers"]:
                self.season_ntx_dict["coins"][coin]["servers"][server]["ntx_count"]\
                    = round(self.season_ntx_dict["coins"][coin]["servers"][server]["ntx_count"] / 13)

                for epoch in self.season_ntx_dict["coins"][coin]["servers"][server]["epochs"]:
                    self.season_ntx_dict["coins"][coin]["servers"][server]["epochs"][epoch]["ntx_count"]\
                        = round(self.season_ntx_dict["coins"][coin]["servers"][server]["epochs"][epoch]["ntx_count"] / 13)

        for server in self.season_ntx_dict["servers"]:
            self.season_ntx_dict["servers"][server]["ntx_count"]\
                = round(self.season_ntx_dict["servers"][server]["ntx_count"] / 13)

            for coin in self.season_ntx_dict["servers"][server]["coins"]:
                self.season_ntx_dict["servers"][server]["coins"][coin]["ntx_count"]\
                    = round(self.season_ntx_dict["servers"][server]["coins"][coin]["ntx_count"] / 13)

                for epoch in self.season_ntx_dict["servers"][server]["epochs"]:
                    self.season_ntx_dict["servers"][server]["epochs"][epoch]["ntx_count"]\
                        = round(self.season_ntx_dict["servers"][server]["epochs"][epoch]["ntx_count"] / 13)

                    for _coin in self.season_ntx_dict["servers"][server]["epochs"][epoch]["coins"]:
                        self.season_ntx_dict["servers"][server]["epochs"][epoch]["coins"][_coin]["ntx_count"]\
                            = round(self.season_ntx_dict["servers"][server]["epochs"][epoch]["coins"][_coin]["ntx_count"] / 13)


        self.season_ntx_dict["ntx_score"] = round(self.season_ntx_dict["ntx_score"], 8)


    def add_global_percentages(self):
        # Percentages relative to season global
        for notary in self.season_notaries:
            # Notary Percentage of Global Count
            self.season_ntx_dict["notaries"][notary]["pct_of_season_ntx_count"] = round(
                safe_div(self.season_ntx_dict["notaries"][notary]["ntx_count"],
                         self.season_ntx_dict["ntx_count"])*100,6)

            # Notary Percentage of Global Score
            self.season_ntx_dict["notaries"][notary]["ntx_score"] = round(self.season_ntx_dict["notaries"][notary]["ntx_score"],8)
            self.season_ntx_dict["notaries"][notary]["pct_of_season_ntx_score"] = round(
                safe_div(self.season_ntx_dict["notaries"][notary]["ntx_score"],
                         self.season_ntx_dict["ntx_score"])*100,6)

            for coin in self.season_ntx_dict["notaries"][notary]["coins"]:
                # Notary Coin Percentage of Global Count
                self.season_ntx_dict["notaries"][notary]["coins"][coin]["pct_of_season_ntx_count"] = round(
                    safe_div(self.season_ntx_dict["notaries"][notary]["coins"][coin]["ntx_count"],
                             self.season_ntx_dict["ntx_count"])*100,6)

                # Notary Coin Percentage of Global Score
                self.season_ntx_dict["notaries"][notary]["coins"][coin]["ntx_score"] = round(self.season_ntx_dict["notaries"][notary]["coins"][coin]["ntx_score"],8)
                self.season_ntx_dict["notaries"][notary]["coins"][coin]["pct_of_season_ntx_score"] = round(
                    safe_div(self.season_ntx_dict["notaries"][notary]["coins"][coin]["ntx_score"],
                             self.season_ntx_dict["ntx_score"])*100,6)


            for server in self.season_servers:
                if server not in ["Unofficial", "BTC", "Unofficial", "None"]:
                    # Notary Server Percentage of Global Count
                    self.season_ntx_dict["notaries"][notary]["servers"][server]["pct_of_season_ntx_count"] = round(
                        safe_div(self.season_ntx_dict["notaries"][notary]["servers"][server]["ntx_count"],
                                 self.season_ntx_dict["ntx_count"])*100,6)

                    # Notary Server Percentage of Global Score
                    self.season_ntx_dict["notaries"][notary]["servers"][server]["ntx_score"] = round(self.season_ntx_dict["notaries"][notary]["servers"][server]["ntx_score"],8)
                    self.season_ntx_dict["notaries"][notary]["servers"][server]["pct_of_season_ntx_score"] = round(
                        safe_div(self.season_ntx_dict["notaries"][notary]["servers"][server]["ntx_score"],
                                 self.season_ntx_dict["ntx_score"])*100,6)


                    for coin in self.season_ntx_dict["notaries"][notary]["servers"][server]["coins"]:
                        # Notary Server Coin Percentage of Global Count
                        self.season_ntx_dict["notaries"][notary]["servers"][server]["coins"][coin]["pct_of_season_ntx_count"] = round(
                            safe_div(self.season_ntx_dict["notaries"][notary]["servers"][server]["coins"][coin]["ntx_count"],
                                     self.season_ntx_dict["ntx_count"])*100,6)

                        # Notary Server Coin Percentage of Global Score
                        self.season_ntx_dict["notaries"][notary]["servers"][server]["coins"][coin]["ntx_score"] = round(self.season_ntx_dict["notaries"][notary]["servers"][server]["coins"][coin]["ntx_score"],8)
                        self.season_ntx_dict["notaries"][notary]["servers"][server]["coins"][coin]["pct_of_season_ntx_score"] = round(
                            safe_div(self.season_ntx_dict["notaries"][notary]["servers"][server]["coins"][coin]["ntx_score"],
                                     self.season_ntx_dict["ntx_score"])*100,6)


                    for epoch in self.season_ntx_dict["notaries"][notary]["servers"][server]["epochs"]:
                        # Notary Server Epoch Percentage of Global Count
                        self.season_ntx_dict["notaries"][notary]["servers"][server]["epochs"][epoch]["pct_of_season_ntx_count"] = round(
                            safe_div(self.season_ntx_dict["notaries"][notary]["servers"][server]["epochs"][epoch]["ntx_count"],
                                     self.season_ntx_dict["ntx_count"])*100,6)

                        # Notary Server Epoch Percentage of Global Score
                        self.season_ntx_dict["notaries"][notary]["servers"][server]["epochs"][epoch]["ntx_score"] = round(self.season_ntx_dict["notaries"][notary]["servers"][server]["epochs"][epoch]["ntx_score"],8)
                        self.season_ntx_dict["notaries"][notary]["servers"][server]["epochs"][epoch]["pct_of_season_ntx_score"] = round(
                            safe_div(self.season_ntx_dict["notaries"][notary]["servers"][server]["epochs"][epoch]["ntx_score"],
                                     self.season_ntx_dict["ntx_score"])*100,6)


                        for coin in self.season_ntx_dict["notaries"][notary]["servers"][server]["epochs"][epoch]["coins"]:
                            # Notary Server Epoch Coin Percentage of Global Count
                            self.season_ntx_dict["notaries"][notary]["servers"][server]["epochs"][epoch]["coins"][coin]["pct_of_season_ntx_count"] = round(
                                safe_div(self.season_ntx_dict["notaries"][notary]["servers"][server]["epochs"][epoch]["coins"][coin]["ntx_count"],
                                         self.season_ntx_dict["ntx_count"])*100,6)

                            # Notary Server Epoch Coin Percentage of Global Score
                            self.season_ntx_dict["notaries"][notary]["servers"][server]["epochs"][epoch]["coins"][coin]["ntx_score"] = round(self.season_ntx_dict["notaries"][notary]["servers"][server]["epochs"][epoch]["coins"][coin]["ntx_score"],8)
                            self.season_ntx_dict["notaries"][notary]["servers"][server]["epochs"][epoch]["coins"][coin]["pct_of_season_ntx_score"] = round(
                                safe_div(self.season_ntx_dict["notaries"][notary]["servers"][server]["epochs"][epoch]["coins"][coin]["ntx_score"],
                                         self.season_ntx_dict["ntx_score"])*100,6)


        for server in self.season_servers:
            # Server Percentage of Global Count
            self.season_ntx_dict["servers"][server]["pct_of_season_ntx_count"] = round(
                safe_div(self.season_ntx_dict["servers"][server]["ntx_count"],
                         self.season_ntx_dict["ntx_count"])*100,6)

            # Server Percentage of Global Score
            self.season_ntx_dict["servers"][server]["pct_of_season_ntx_score"] = round(
                safe_div(self.season_ntx_dict["servers"][server]["ntx_score"],
                         self.season_ntx_dict["ntx_score"])*100,6)


            for coin in self.season_ntx_dict["servers"][server]["coins"]:
                # Server Coin Percentage of Global Count
                self.season_ntx_dict["servers"][server]["coins"][coin]["pct_of_season_ntx_count"] = round(
                    safe_div(self.season_ntx_dict["servers"][server]["coins"][coin]["ntx_count"],
                             self.season_ntx_dict["ntx_count"])*100,6)

                # Server Coin Percentage of Global Score
                self.season_ntx_dict["servers"][server]["coins"][coin]["pct_of_season_ntx_score"] = round(
                    safe_div(self.season_ntx_dict["servers"][server]["coins"][coin]["ntx_score"],
                             self.season_ntx_dict["ntx_score"])*100,6)

                for notary in self.season_notaries:
                    # Server Coin Notary Percentage of Global Count
                    self.season_ntx_dict["servers"][server]["coins"][coin]["notaries"][notary]["pct_of_season_ntx_count"] = round(
                    safe_div(self.season_ntx_dict["servers"][server]["coins"][coin]["notaries"][notary]["ntx_count"],
                             self.season_ntx_dict["ntx_count"])*100,6)

                    # Server Coin Notary Percentage of Global Score
                    self.season_ntx_dict["servers"][server]["coins"][coin]["pct_of_season_ntx_score"] = round(
                        safe_div(self.season_ntx_dict["servers"][server]["coins"][coin]["notaries"][notary]["ntx_score"],
                                 self.season_ntx_dict["ntx_score"])*100,6)



            for notary in self.season_notaries:
                # Server Notary Percentage of Global Count
                self.season_ntx_dict["servers"][server]["notaries"][notary]["pct_of_season_ntx_count"] = round(
                    safe_div(self.season_ntx_dict["servers"][server]["notaries"][notary]["ntx_count"],
                             self.season_ntx_dict["ntx_count"])*100,6)

                # Server Notary Percentage of Global Score
                self.season_ntx_dict["servers"][server]["notaries"][notary]["pct_of_season_ntx_score"] = round(
                    safe_div(self.season_ntx_dict["servers"][server]["notaries"][notary]["ntx_score"],
                             self.season_ntx_dict["ntx_score"])*100,6)


            for epoch in self.season_ntx_dict["servers"][server]["epochs"]:
                # Server Epoch Percentage of Global Count
                self.season_ntx_dict["servers"][server]["epochs"][epoch]["pct_of_season_ntx_count"] = round(
                    safe_div(self.season_ntx_dict["servers"][server]["epochs"][epoch]["ntx_count"],
                             self.season_ntx_dict["ntx_count"])*100,6)

                # Server Epoch Percentage of Global Score
                self.season_ntx_dict["servers"][server]["epochs"][epoch]["pct_of_season_ntx_score"] = round(
                    safe_div(self.season_ntx_dict["servers"][server]["epochs"][epoch]["ntx_score"],
                             self.season_ntx_dict["ntx_score"])*100,6)


                for notary in self.season_notaries:
                    # Server Epoch Notary Percentage of Global Count
                    self.season_ntx_dict["servers"][server]["epochs"][epoch]["notaries"][notary]["pct_of_season_ntx_count"] = round(
                        safe_div(self.season_ntx_dict["servers"][server]["epochs"][epoch]["notaries"][notary]["ntx_count"],
                                 self.season_ntx_dict["ntx_count"])*100,6)

                    # Server Epoch Notary Percentage of Global Score
                    self.season_ntx_dict["servers"][server]["epochs"][epoch]["notaries"][notary]["pct_of_season_ntx_score"] = round(
                        safe_div(self.season_ntx_dict["servers"][server]["epochs"][epoch]["notaries"][notary]["ntx_score"],
                                 self.season_ntx_dict["ntx_score"])*100,6)


                for coin in self.season_ntx_dict["servers"][server]["epochs"][epoch]["coins"]:
                    # Server Epoch Coin Percentage of Global Count
                    self.season_ntx_dict["servers"][server]["epochs"][epoch]["coins"][coin]["pct_of_season_ntx_count"] = round(
                        safe_div(self.season_ntx_dict["servers"][server]["epochs"][epoch]["coins"][coin]["ntx_count"],
                                 self.season_ntx_dict["ntx_count"])*100,6)

                    # Server Epoch Coin Percentage of Global Score
                    self.season_ntx_dict["servers"][server]["epochs"][epoch]["coins"][coin]["pct_of_season_ntx_score"] = round(
                        safe_div(self.season_ntx_dict["servers"][server]["epochs"][epoch]["coins"][coin]["ntx_score"],
                                 self.season_ntx_dict["ntx_score"])*100,6)

                    for notary in self.season_notaries:

                        self.season_ntx_dict["servers"][server]["epochs"][epoch]["coins"][coin]["notaries"][notary]["pct_of_season_ntx_count"] = round(
                            safe_div(self.season_ntx_dict["servers"][server]["epochs"][epoch]["coins"][coin]["notaries"][notary]["ntx_count"],
                                     self.season_ntx_dict["ntx_count"])*100,6)

                        # Server Epoch Coin Percentage of Global Score
                        self.season_ntx_dict["servers"][server]["epochs"][epoch]["coins"][coin]["notaries"][notary]["pct_of_season_ntx_score"] = round(
                            safe_div(self.season_ntx_dict["servers"][server]["epochs"][epoch]["coins"][coin]["notaries"][notary]["ntx_score"],
                                     self.season_ntx_dict["ntx_score"])*100,6)

        for coin in self.season_ntx_dict["coins"]:
            # Coin Percentage of Global Count
            self.season_ntx_dict["coins"][coin]["pct_of_season_ntx_count"] = round(
                safe_div(self.season_ntx_dict["coins"][coin]["ntx_count"],
                         self.season_ntx_dict["ntx_count"])*100,6)

            # Coin Percentage of Global Score
            self.season_ntx_dict["coins"][coin]["ntx_score"] = round(self.season_ntx_dict["coins"][coin]["ntx_score"],8)
            self.season_ntx_dict["coins"][coin]["pct_of_season_ntx_score"] = round(
                safe_div(self.season_ntx_dict["coins"][coin]["ntx_score"],
                         self.season_ntx_dict["ntx_score"])*100,6)


            for notary in self.season_notaries:
                # Coin Notary Percentage of Global Count
                self.season_ntx_dict["coins"][coin]["notaries"][notary]["pct_of_season_ntx_count"] = round(
                    safe_div(self.season_ntx_dict["coins"][coin]["notaries"][notary]["ntx_count"],
                             self.season_ntx_dict["ntx_count"])*100,6)

                # Coin Notary Percentage of Global Score
                self.season_ntx_dict["coins"][coin]["notaries"][notary]["ntx_score"] = round(self.season_ntx_dict["coins"][coin]["notaries"][notary]["ntx_score"],8)
                self.season_ntx_dict["coins"][coin]["notaries"][notary]["pct_of_season_ntx_score"] = round(
                    safe_div(self.season_ntx_dict["coins"][coin]["notaries"][notary]["ntx_score"],
                             self.season_ntx_dict["ntx_score"])*100,6)


            for server in self.season_servers:
                if coin in helper.get_season_coins(self.season, server):
                    # Coin Server Percentage of Global Count
                    self.season_ntx_dict["coins"][coin]["servers"][server]["pct_of_season_ntx_count"] = round(
                        safe_div(self.season_ntx_dict["coins"][coin]["servers"][server]["ntx_count"],
                                 self.season_ntx_dict["ntx_count"])*100,6)

                    # Coin Server Percentage of Global Score
                    self.season_ntx_dict["coins"][coin]["servers"][server]["ntx_score"] = round(self.season_ntx_dict["coins"][coin]["servers"][server]["ntx_score"],8)
                    self.season_ntx_dict["coins"][coin]["servers"][server]["pct_of_season_ntx_score"] = round(
                        safe_div(self.season_ntx_dict["coins"][coin]["servers"][server]["ntx_score"],
                                 self.season_ntx_dict["ntx_score"])*100,6)


                    for notary in self.season_notaries:
                        # Coin Server Notary Percentage of Global Count
                        self.season_ntx_dict["coins"][coin]["servers"][server]["notaries"][notary]["pct_of_season_ntx_count"] = round(
                            safe_div(self.season_ntx_dict["coins"][coin]["servers"][server]["notaries"][notary]["ntx_count"],
                                     self.season_ntx_dict["ntx_count"])*100,6)

                        # Coin Server Notary Percentage of Global Score
                        self.season_ntx_dict["coins"][coin]["servers"][server]["notaries"][notary]["ntx_score"] = round(self.season_ntx_dict["coins"][coin]["servers"][server]["notaries"][notary]["ntx_score"],8)
                        self.season_ntx_dict["coins"][coin]["servers"][server]["notaries"][notary]["pct_of_season_ntx_score"] = round(
                            safe_div(self.season_ntx_dict["coins"][coin]["servers"][server]["notaries"][notary]["ntx_score"],
                                     self.season_ntx_dict["ntx_score"])*100,6)


                    for epoch in self.season_ntx_dict["coins"][coin]["servers"][server]["epochs"]:
                        # Coin Server Epoch Percentage of Global Count
                        self.season_ntx_dict["coins"][coin]["servers"][server]["epochs"][epoch]["pct_of_season_ntx_count"] = round(
                            safe_div(self.season_ntx_dict["coins"][coin]["servers"][server]["epochs"][epoch]["ntx_count"],
                                     self.season_ntx_dict["ntx_count"])*100,6)

                        # Coin Server Epoch Percentage of Global Score
                        self.season_ntx_dict["coins"][coin]["servers"][server]["epochs"][epoch]["ntx_score"] = round(self.season_ntx_dict["coins"][coin]["servers"][server]["epochs"][epoch]["ntx_score"],8)
                        self.season_ntx_dict["coins"][coin]["servers"][server]["epochs"][epoch]["pct_of_season_ntx_score"] = round(
                            safe_div(self.season_ntx_dict["coins"][coin]["servers"][server]["epochs"][epoch]["ntx_score"],
                                     self.season_ntx_dict["ntx_score"])*100,6)


                        for notary in self.season_notaries:
                            # Coin Server Epoch Notary Percentage of Global Count
                            self.season_ntx_dict["coins"][coin]["servers"][server]["epochs"][epoch]["notaries"][notary]["pct_of_season_ntx_count"] = round(
                                safe_div(self.season_ntx_dict["coins"][coin]["servers"][server]["epochs"][epoch]["notaries"][notary]["ntx_count"],
                                         self.season_ntx_dict["ntx_count"])*100,6)

                            # Coin Server Epoch Notary Percentage of Global Score
                            self.season_ntx_dict["coins"][coin]["servers"][server]["epochs"][epoch]["notaries"][notary]["ntx_score"] = round(self.season_ntx_dict["coins"][coin]["servers"][server]["epochs"][epoch]["notaries"][notary]["ntx_score"],8)
                            self.season_ntx_dict["coins"][coin]["servers"][server]["epochs"][epoch]["notaries"][notary]["pct_of_season_ntx_score"] = round(
                                safe_div(self.season_ntx_dict["coins"][coin]["servers"][server]["epochs"][epoch]["notaries"][notary]["ntx_score"],
                                         self.season_ntx_dict["ntx_score"])*100,6)


    def add_coin_percentages(self):

        # Percentages relative to coins
        for coin in self.season_ntx_dict["coins"]:

            for notary in self.season_notaries:
                # Coin Percentage of Coins Count
                self.season_ntx_dict["coins"][coin]["notaries"][notary]["pct_of_coin_ntx_count"] = round(
                    safe_div(self.season_ntx_dict["coins"][coin]["notaries"][notary]["ntx_count"],
                             self.season_ntx_dict["coins"][coin]["ntx_count"])*100,6)

                # Coin Percentage of Coins Score
                self.season_ntx_dict["coins"][coin]["notaries"][notary]["ntx_score"] = round(self.season_ntx_dict["coins"][coin]["notaries"][notary]["ntx_score"],8)
                self.season_ntx_dict["coins"][coin]["notaries"][notary]["pct_of_coin_ntx_score"] = round(
                    safe_div(self.season_ntx_dict["coins"][coin]["notaries"][notary]["ntx_score"],
                             self.season_ntx_dict["coins"][coin]["ntx_score"])*100,6)


            for server in self.season_servers:
                if coin in helper.get_season_coins(self.season, server):
                    for notary in self.season_notaries:
                        # Coin Server Notary Percentage of Coins Count
                        self.season_ntx_dict["coins"][coin]["servers"][server]["notaries"][notary]["pct_of_coin_ntx_count"] = round(
                            safe_div(self.season_ntx_dict["coins"][coin]["servers"][server]["notaries"][notary]["ntx_count"],
                                     self.season_ntx_dict["coins"][coin]["ntx_count"])*100,6)

                        # Coin Server Notary Percentage of Coins Score
                        self.season_ntx_dict["coins"][coin]["servers"][server]["notaries"][notary]["ntx_score"] = round(self.season_ntx_dict["coins"][coin]["servers"][server]["notaries"][notary]["ntx_score"],8)
                        self.season_ntx_dict["coins"][coin]["servers"][server]["notaries"][notary]["pct_of_coin_ntx_score"] = round(
                            safe_div(self.season_ntx_dict["coins"][coin]["servers"][server]["notaries"][notary]["ntx_score"],
                                     self.season_ntx_dict["coins"][coin]["ntx_score"])*100,6)


                    for epoch in self.season_ntx_dict["coins"][coin]["servers"][server]["epochs"]:
                        # Coin Server Epoch Percentage of Coins Count
                        self.season_ntx_dict["coins"][coin]["servers"][server]["epochs"][epoch]["pct_of_coin_ntx_count"] = round(
                            safe_div(self.season_ntx_dict["coins"][coin]["servers"][server]["epochs"][epoch]["ntx_count"],
                                     self.season_ntx_dict["coins"][coin]["ntx_count"])*100,6)

                        # Coin Server Epoch Percentage of Coins Score
                        self.season_ntx_dict["coins"][coin]["servers"][server]["epochs"][epoch]["ntx_score"] = round(self.season_ntx_dict["coins"][coin]["servers"][server]["epochs"][epoch]["ntx_score"],8)
                        self.season_ntx_dict["coins"][coin]["servers"][server]["epochs"][epoch]["pct_of_coin_ntx_score"] = round(
                            safe_div(self.season_ntx_dict["coins"][coin]["servers"][server]["epochs"][epoch]["ntx_score"],
                                     self.season_ntx_dict["coins"][coin]["ntx_score"])*100,6)


                        for notary in self.season_notaries:
                            # Coin Server Epoch Notaries Percentage of Coins Count
                            self.season_ntx_dict["coins"][coin]["servers"][server]["epochs"][epoch]["notaries"][notary]["pct_of_coin_ntx_count"] = round(
                                safe_div(self.season_ntx_dict["coins"][coin]["servers"][server]["epochs"][epoch]["notaries"][notary]["ntx_count"],
                                         self.season_ntx_dict["coins"][coin]["ntx_count"])*100,6)

                            # Coin Server Epoch Notaries Percentage of Coins Score
                            self.season_ntx_dict["coins"][coin]["servers"][server]["epochs"][epoch]["notaries"][notary]["ntx_score"] = round(self.season_ntx_dict["coins"][coin]["servers"][server]["epochs"][epoch]["notaries"][notary]["ntx_score"],8)
                            self.season_ntx_dict["coins"][coin]["servers"][server]["epochs"][epoch]["notaries"][notary]["pct_of_coin_ntx_score"] = round(
                                safe_div(self.season_ntx_dict["coins"][coin]["servers"][server]["epochs"][epoch]["notaries"][notary]["ntx_score"],
                                         self.season_ntx_dict["coins"][coin]["ntx_score"])*100,6)


        for notary in self.season_notaries:
            for coin in self.season_ntx_dict["notaries"][notary]["coins"]:

                # Notary Coin Percentage of Coins Count
                self.season_ntx_dict["notaries"][notary]["coins"][coin]["pct_of_coin_ntx_count"] = round(
                    safe_div(self.season_ntx_dict["notaries"][notary]["coins"][coin]["ntx_count"],
                             self.season_ntx_dict["coins"][coin]["ntx_count"])*100,6)

                # Notary Coin Percentage of Coins Score
                self.season_ntx_dict["notaries"][notary]["coins"][coin]["ntx_score"] = round(self.season_ntx_dict["notaries"][notary]["coins"][coin]["ntx_score"],8)
                self.season_ntx_dict["notaries"][notary]["coins"][coin]["pct_of_coin_ntx_score"] = round(
                    safe_div(self.season_ntx_dict["notaries"][notary]["coins"][coin]["ntx_score"],
                             self.season_ntx_dict["coins"][coin]["ntx_score"])*100,6)


        for server in self.season_servers:
            for coin in self.season_ntx_dict["servers"][server]["coins"]:
                # Server Coin Percentage of Coins Count
                self.season_ntx_dict["servers"][server]["coins"][coin]["pct_of_coin_ntx_count"] = round(
                    safe_div(self.season_ntx_dict["servers"][server]["coins"][coin]["ntx_count"],
                             self.season_ntx_dict["coins"][coin]["ntx_count"])*100,6)

                # Server Coin Percentage of Coins Score
                self.season_ntx_dict["servers"][server]["coins"][coin]["ntx_score"] = round(self.season_ntx_dict["servers"][server]["coins"][coin]["ntx_score"],8)
                self.season_ntx_dict["servers"][server]["coins"][coin]["pct_of_coin_ntx_score"] = round(
                    safe_div(self.season_ntx_dict["servers"][server]["coins"][coin]["ntx_score"],
                             self.season_ntx_dict["coins"][coin]["ntx_score"])*100,6)


            for epoch in self.season_ntx_dict["servers"][server]["epochs"]:
                for coin in self.season_ntx_dict["servers"][server]["epochs"][epoch]["coins"]:

                    # Server Epoch Coin Percentage of Coins Count
                    self.season_ntx_dict["servers"][server]["epochs"][epoch]["coins"][coin]["pct_of_coin_ntx_count"] = round(
                        safe_div(self.season_ntx_dict["servers"][server]["epochs"][epoch]["coins"][coin]["ntx_count"],
                                 self.season_ntx_dict["coins"][coin]["ntx_count"])*100,6)

                    # Server Epoch Coin Percentage of Coins Score
                    self.season_ntx_dict["servers"][server]["epochs"][epoch]["coins"][coin]["ntx_score"] = round(self.season_ntx_dict["servers"][server]["epochs"][epoch]["coins"][coin]["ntx_score"],8)
                    self.season_ntx_dict["servers"][server]["epochs"][epoch]["coins"][coin]["pct_of_coin_ntx_score"] = round(
                        safe_div(self.season_ntx_dict["servers"][server]["epochs"][epoch]["coins"][coin]["ntx_score"],
                                 self.season_ntx_dict["coins"][coin]["ntx_score"])*100,6)


                    for notary in self.season_notaries:

                        # Server Epoch Notary Percentage of Coins Count
                        self.season_ntx_dict["servers"][server]["epochs"][epoch]["notaries"][notary]["pct_of_coin_ntx_count"] = round(
                            safe_div(self.season_ntx_dict["servers"][server]["epochs"][epoch]["notaries"][notary]["ntx_count"],
                                     self.season_ntx_dict["coins"][coin]["ntx_count"])*100,6)

                        # Server Epoch Notary Percentage of Coins Score
                        self.season_ntx_dict["servers"][server]["epochs"][epoch]["notaries"][notary]["ntx_score"] = round(self.season_ntx_dict["servers"][server]["epochs"][epoch]["notaries"][notary]["ntx_score"],8)
                        self.season_ntx_dict["servers"][server]["epochs"][epoch]["notaries"][notary]["pct_of_coin_ntx_score"] = round(
                            safe_div(self.season_ntx_dict["servers"][server]["epochs"][epoch]["notaries"][notary]["ntx_score"],
                                     self.season_ntx_dict["coins"][coin]["ntx_score"])*100,6)


    def add_notary_percentages(self):

        # Percentages relative to notary
        for notary in self.season_notaries:
            for coin in self.season_ntx_dict["notaries"][notary]["coins"]:
                # Notary Coin Percentage of Notary Count
                self.season_ntx_dict["notaries"][notary]["coins"][coin]["ntx_score"] = round(self.season_ntx_dict["notaries"][notary]["coins"][coin]["ntx_score"],8)
                self.season_ntx_dict["notaries"][notary]["coins"][coin]["pct_of_notary_ntx_count"] = round(
                    safe_div(self.season_ntx_dict["notaries"][notary]["coins"][coin]["ntx_count"],
                             self.season_ntx_dict["notaries"][notary]["ntx_count"])*100,6)

                # Notary Coin Percentage of Notary Score
                self.season_ntx_dict["notaries"][notary]["coins"][coin]["pct_of_notary_ntx_score"] = round(
                    safe_div(self.season_ntx_dict["notaries"][notary]["coins"][coin]["ntx_score"],
                             self.season_ntx_dict["notaries"][notary]["ntx_score"])*100,6)


            for server in self.season_servers:
                # Notary Server Percentage of Notary Count
                self.season_ntx_dict["notaries"][notary]["servers"][server]["pct_of_notary_ntx_count"] = round(
                    safe_div(self.season_ntx_dict["notaries"][notary]["servers"][server]["ntx_count"],
                             self.season_ntx_dict["notaries"][notary]["ntx_count"])*100,6)

                # Notary Server Percentage of Notary Score
                self.season_ntx_dict["notaries"][notary]["servers"][server]["ntx_score"] = round(self.season_ntx_dict["notaries"][notary]["servers"][server]["ntx_score"],8)
                self.season_ntx_dict["notaries"][notary]["servers"][server]["pct_of_notary_ntx_score"] = round(
                    safe_div(self.season_ntx_dict["notaries"][notary]["servers"][server]["ntx_score"],
                             self.season_ntx_dict["notaries"][notary]["ntx_score"])*100,6)


                for epoch in self.season_ntx_dict["notaries"][notary]["servers"][server]["epochs"]:
                    # Notary Server Epoch Percentage of Notary Count
                    self.season_ntx_dict["notaries"][notary]["servers"][server]["epochs"][epoch]["pct_of_notary_ntx_count"] = round(
                        safe_div(self.season_ntx_dict["notaries"][notary]["servers"][server]["epochs"][epoch]["ntx_count"],
                                 self.season_ntx_dict["notaries"][notary]["ntx_count"])*100,6)

                    # Notary Server Epoch Percentage of Notary Score
                    self.season_ntx_dict["notaries"][notary]["servers"][server]["epochs"][epoch]["ntx_score"] = round(self.season_ntx_dict["notaries"][notary]["servers"][server]["epochs"][epoch]["ntx_score"],8)
                    self.season_ntx_dict["notaries"][notary]["servers"][server]["epochs"][epoch]["pct_of_notary_ntx_score"] = round(
                        safe_div(self.season_ntx_dict["notaries"][notary]["servers"][server]["epochs"][epoch]["ntx_score"],
                                 self.season_ntx_dict["notaries"][notary]["ntx_score"])*100,6)


                    for coin in self.season_ntx_dict["notaries"][notary]["servers"][server]["epochs"][epoch]["coins"]:
                        # Notary Server Epoch Coin Percentage of Notary Count
                        self.season_ntx_dict["notaries"][notary]["servers"][server]["epochs"][epoch]["coins"][coin]["pct_of_notary_ntx_count"] = round(
                            safe_div(self.season_ntx_dict["notaries"][notary]["servers"][server]["epochs"][epoch]["coins"][coin]["ntx_count"],
                                     self.season_ntx_dict["notaries"][notary]["ntx_count"])*100,6)

                        # Notary Server Epoch Coin Percentage of Notary Score
                        self.season_ntx_dict["notaries"][notary]["servers"][server]["epochs"][epoch]["coins"][coin]["ntx_score"] = round(self.season_ntx_dict["notaries"][notary]["servers"][server]["epochs"][epoch]["coins"][coin]["ntx_score"],8)
                        self.season_ntx_dict["notaries"][notary]["servers"][server]["epochs"][epoch]["coins"][coin]["pct_of_notary_ntx_score"] = round(
                            safe_div(self.season_ntx_dict["notaries"][notary]["servers"][server]["epochs"][epoch]["coins"][coin]["ntx_score"],
                                     self.season_ntx_dict["notaries"][notary]["ntx_score"])*100,6)


        for coin in self.season_ntx_dict["coins"]:
            for notary in self.season_notaries:
                # Coin Notary Percentage of Notary Count
                self.season_ntx_dict["coins"][coin]["notaries"][notary]["pct_of_notary_ntx_count"] = round(
                    safe_div(self.season_ntx_dict["coins"][coin]["notaries"][notary]["ntx_count"],
                             self.season_ntx_dict["notaries"][notary]["ntx_count"])*100,6)

                # Coin Notary Percentage of Notary Score
                self.season_ntx_dict["coins"][coin]["notaries"][notary]["ntx_score"] = round(self.season_ntx_dict["coins"][coin]["notaries"][notary]["ntx_score"],8)
                self.season_ntx_dict["coins"][coin]["notaries"][notary]["pct_of_notary_ntx_score"] = round(
                    safe_div(self.season_ntx_dict["coins"][coin]["notaries"][notary]["ntx_score"],
                             self.season_ntx_dict["notaries"][notary]["ntx_score"])*100,6)


    def add_server_percentages(self):
        # Percentages relative to server
        for coin in self.season_ntx_dict["coins"]:

            for server in self.season_servers:
                if coin in helper.get_season_coins(self.season, server):
                    # Coin Server Percentage of Server Count
                    self.season_ntx_dict["coins"][coin]["servers"][server]["pct_of_server_ntx_count"] = round(
                        safe_div(self.season_ntx_dict["coins"][coin]["servers"][server]["ntx_count"],
                                 self.season_ntx_dict["servers"][server]["ntx_count"])*100,6)

                    # Coin Server Percentage of Server Score
                    self.season_ntx_dict["coins"][coin]["servers"][server]["ntx_score"] = round(self.season_ntx_dict["coins"][coin]["servers"][server]["ntx_score"],8)
                    self.season_ntx_dict["coins"][coin]["servers"][server]["pct_of_server_ntx_score"] = round(
                        safe_div(self.season_ntx_dict["coins"][coin]["servers"][server]["ntx_score"],
                                 self.season_ntx_dict["servers"][server]["ntx_score"])*100,6)


                    for notary in self.season_notaries:
                        # Coin Server Notary Percentage of Server Count
                        self.season_ntx_dict["coins"][coin]["servers"][server]["notaries"][notary]["pct_of_server_ntx_count"] = round(
                            safe_div(self.season_ntx_dict["coins"][coin]["servers"][server]["notaries"][notary]["ntx_count"],
                                     self.season_ntx_dict["servers"][server]["ntx_count"])*100,6)

                        # Coin Server Notary Percentage of Server Score
                        self.season_ntx_dict["coins"][coin]["servers"][server]["notaries"][notary]["ntx_score"] = round(self.season_ntx_dict["coins"][coin]["servers"][server]["notaries"][notary]["ntx_score"],8)
                        self.season_ntx_dict["coins"][coin]["servers"][server]["notaries"][notary]["pct_of_server_ntx_score"] = round(
                            safe_div(self.season_ntx_dict["coins"][coin]["servers"][server]["notaries"][notary]["ntx_score"],
                                     self.season_ntx_dict["servers"][server]["ntx_score"])*100,6)


                    for epoch in self.season_ntx_dict["coins"][coin]["servers"][server]["epochs"]:
                        # Coin Server Epoch Percentage of Server Count
                        self.season_ntx_dict["coins"][coin]["servers"][server]["epochs"][epoch]["pct_of_server_ntx_count"] = round(
                            safe_div(self.season_ntx_dict["coins"][coin]["servers"][server]["epochs"][epoch]["ntx_count"],
                                     self.season_ntx_dict["servers"][server]["ntx_count"])*100,6)

                        # Coin Server Epoch Percentage of Server Score
                        self.season_ntx_dict["coins"][coin]["servers"][server]["epochs"][epoch]["ntx_score"] = round(self.season_ntx_dict["coins"][coin]["servers"][server]["epochs"][epoch]["ntx_score"],8)
                        self.season_ntx_dict["coins"][coin]["servers"][server]["epochs"][epoch]["pct_of_server_ntx_score"] = round(
                            safe_div(self.season_ntx_dict["coins"][coin]["servers"][server]["epochs"][epoch]["ntx_score"],
                                     self.season_ntx_dict["servers"][server]["ntx_score"])*100,6)


                        for notary in self.season_notaries:
                            # Coin Server Epoch Notary Percentage of Server Count
                            self.season_ntx_dict["coins"][coin]["servers"][server]["epochs"][epoch]["notaries"][notary]["ntx_score"] = round(self.season_ntx_dict["coins"][coin]["servers"][server]["epochs"][epoch]["notaries"][notary]["ntx_score"],8)
                            self.season_ntx_dict["coins"][coin]["servers"][server]["epochs"][epoch]["notaries"][notary]["pct_of_server_ntx_count"] = round(
                                safe_div(self.season_ntx_dict["coins"][coin]["servers"][server]["epochs"][epoch]["notaries"][notary]["ntx_count"],
                                         self.season_ntx_dict["servers"][server]["ntx_count"])*100,6)

                            # Coin Server Epoch Notary Percentage of Server Score
                            self.season_ntx_dict["coins"][coin]["servers"][server]["epochs"][epoch]["notaries"][notary]["pct_of_server_ntx_score"] = round(
                                safe_div(self.season_ntx_dict["coins"][coin]["servers"][server]["epochs"][epoch]["notaries"][notary]["ntx_score"],
                                         self.season_ntx_dict["servers"][server]["ntx_score"])*100,6)


        for notary in self.season_notaries:
            for server in self.season_servers:

                # Notary Server Percentage of Server Count
                self.season_ntx_dict["notaries"][notary]["servers"][server]["pct_of_server_ntx_count"] = round(
                    safe_div(self.season_ntx_dict["notaries"][notary]["servers"][server]["ntx_count"],
                             self.season_ntx_dict["servers"][server]["ntx_count"])*100,6)

                # Notary Server Percentage of Server Score
                self.season_ntx_dict["notaries"][notary]["servers"][server]["ntx_score"] = round(self.season_ntx_dict["notaries"][notary]["servers"][server]["ntx_score"],8)
                self.season_ntx_dict["notaries"][notary]["servers"][server]["pct_of_server_ntx_score"] = round(
                    safe_div(self.season_ntx_dict["notaries"][notary]["servers"][server]["ntx_score"],
                             self.season_ntx_dict["servers"][server]["ntx_score"])*100,6)


                for coin in self.season_ntx_dict["notaries"][notary]["servers"][server]["coins"]:

                    # Notary Server Coin Percentage of Server Count
                    self.season_ntx_dict["notaries"][notary]["servers"][server]["coins"][coin]["pct_of_server_ntx_count"] = round(
                        safe_div(self.season_ntx_dict["notaries"][notary]["servers"][server]["coins"][coin]["ntx_count"],
                                 self.season_ntx_dict["servers"][server]["ntx_count"])*100,6)

                    # Notary Server Coin Percentage of Server Score
                    self.season_ntx_dict["notaries"][notary]["servers"][server]["coins"][coin]["ntx_score"] = round(self.season_ntx_dict["notaries"][notary]["servers"][server]["coins"][coin]["ntx_score"],8)
                    self.season_ntx_dict["notaries"][notary]["servers"][server]["coins"][coin]["pct_of_server_ntx_score"] = round(
                        safe_div(self.season_ntx_dict["notaries"][notary]["servers"][server]["coins"][coin]["ntx_score"],
                                 self.season_ntx_dict["servers"][server]["ntx_score"])*100,6)


                for epoch in self.season_ntx_dict["notaries"][notary]["servers"][server]["epochs"]:

                    # Notary Server Epoch Percentage of Server Count
                    self.season_ntx_dict["notaries"][notary]["servers"][server]["epochs"][epoch]["pct_of_server_ntx_count"] = round(
                        safe_div(self.season_ntx_dict["notaries"][notary]["servers"][server]["epochs"][epoch]["ntx_count"],
                                 self.season_ntx_dict["servers"][server]["ntx_count"])*100,6)

                    # Notary Server Epoch Percentage of Server Score
                    self.season_ntx_dict["notaries"][notary]["servers"][server]["epochs"][epoch]["ntx_score"] = round(self.season_ntx_dict["notaries"][notary]["servers"][server]["epochs"][epoch]["ntx_score"],8)
                    self.season_ntx_dict["notaries"][notary]["servers"][server]["epochs"][epoch]["pct_of_server_ntx_score"] = round(
                        safe_div(self.season_ntx_dict["notaries"][notary]["servers"][server]["epochs"][epoch]["ntx_score"],
                                 self.season_ntx_dict["servers"][server]["ntx_score"])*100,6)


                    for coin in self.season_ntx_dict["notaries"][notary]["servers"][server]["epochs"][epoch]["coins"]:

                        # Notary Server Epoch Coin Percentage of Server Count
                        self.season_ntx_dict["notaries"][notary]["servers"][server]["epochs"][epoch]["coins"][coin]["pct_of_server_ntx_count"] = round(
                            safe_div(self.season_ntx_dict["notaries"][notary]["servers"][server]["epochs"][epoch]["coins"][coin]["ntx_count"],
                                     self.season_ntx_dict["servers"][server]["ntx_count"])*100,6)

                        # Notary Server Epoch Coin Percentage of Server Score
                        self.season_ntx_dict["notaries"][notary]["servers"][server]["epochs"][epoch]["coins"][coin]["ntx_score"] = round(self.season_ntx_dict["notaries"][notary]["servers"][server]["epochs"][epoch]["coins"][coin]["ntx_score"],8)
                        self.season_ntx_dict["notaries"][notary]["servers"][server]["epochs"][epoch]["coins"][coin]["pct_of_server_ntx_score"] = round(
                            safe_div(self.season_ntx_dict["notaries"][notary]["servers"][server]["epochs"][epoch]["coins"][coin]["ntx_score"],
                                     self.season_ntx_dict["servers"][server]["ntx_score"])*100,6)


        for server in self.season_servers:

            for notary in self.season_notaries:
                # Server Notary Percentage of Server Count
                self.season_ntx_dict["servers"][server]["notaries"][notary]["pct_of_server_ntx_count"] = round(
                    safe_div(self.season_ntx_dict["servers"][server]["notaries"][notary]["ntx_count"],
                             self.season_ntx_dict["servers"][server]["ntx_count"])*100,6)

                # Server Notary Percentage of Server Score
                self.season_ntx_dict["servers"][server]["notaries"][notary]["ntx_score"] = round(self.season_ntx_dict["servers"][server]["notaries"][notary]["ntx_score"],8)
                self.season_ntx_dict["servers"][server]["notaries"][notary]["pct_of_server_ntx_score"] = round(
                    safe_div(self.season_ntx_dict["servers"][server]["notaries"][notary]["ntx_score"],
                             self.season_ntx_dict["servers"][server]["ntx_score"])*100,6)


            for coin in self.season_ntx_dict["servers"][server]["coins"]:
                # Server Coin Percentage of Server Count
                self.season_ntx_dict["servers"][server]["coins"][coin]["pct_of_server_ntx_count"] = round(
                    safe_div(self.season_ntx_dict["servers"][server]["coins"][coin]["ntx_count"],
                             self.season_ntx_dict["servers"][server]["ntx_count"])*100,6)

                # Server Coin Percentage of Server Score
                self.season_ntx_dict["servers"][server]["coins"][coin]["ntx_score"] = round(self.season_ntx_dict["servers"][server]["coins"][coin]["ntx_score"],8)
                self.season_ntx_dict["servers"][server]["coins"][coin]["pct_of_server_ntx_score"] = round(
                    safe_div(self.season_ntx_dict["servers"][server]["coins"][coin]["ntx_score"],
                             self.season_ntx_dict["servers"][server]["ntx_score"])*100,6)


            for epoch in self.season_ntx_dict["servers"][server]["epochs"]:
                # Server Epoch Percentage of Server Count
                self.season_ntx_dict["servers"][server]["epochs"][epoch]["pct_of_server_ntx_count"] = round(
                    safe_div(self.season_ntx_dict["servers"][server]["epochs"][epoch]["ntx_count"],
                             self.season_ntx_dict["servers"][server]["ntx_count"])*100,6)

                # Server Epoch Percentage of Server Score
                self.season_ntx_dict["servers"][server]["epochs"][epoch]["ntx_score"] = round(self.season_ntx_dict["servers"][server]["epochs"][epoch]["ntx_score"],8)
                self.season_ntx_dict["servers"][server]["epochs"][epoch]["pct_of_server_ntx_score"] = round(
                    safe_div(self.season_ntx_dict["servers"][server]["epochs"][epoch]["ntx_score"],
                             self.season_ntx_dict["servers"][server]["ntx_score"])*100,6)


                for coin in self.season_ntx_dict["servers"][server]["epochs"][epoch]["coins"]:
                    # Server Epoch Coin Percentage of Server Count
                    self.season_ntx_dict["servers"][server]["epochs"][epoch]["coins"][coin]["pct_of_server_ntx_count"] = round(
                        safe_div(self.season_ntx_dict["servers"][server]["epochs"][epoch]["coins"][coin]["ntx_count"],
                                 self.season_ntx_dict["servers"][server]["ntx_count"])*100,6)

                    # Server Epoch Coin Percentage of Server Score
                    self.season_ntx_dict["servers"][server]["epochs"][epoch]["coins"][coin]["ntx_score"] = round(self.season_ntx_dict["servers"][server]["epochs"][epoch]["coins"][coin]["ntx_score"],8)
                    self.season_ntx_dict["servers"][server]["epochs"][epoch]["coins"][coin]["pct_of_server_ntx_score"] = round(
                        safe_div(self.season_ntx_dict["servers"][server]["epochs"][epoch]["coins"][coin]["ntx_score"],
                                 self.season_ntx_dict["servers"][server]["ntx_score"])*100,6)


                for notary in self.season_notaries:
                    # Server Epoch Notary Percentage of Server Count
                    self.season_ntx_dict["servers"][server]["epochs"][epoch]["notaries"][notary]["pct_of_server_ntx_count"] = round(
                        safe_div(self.season_ntx_dict["servers"][server]["epochs"][epoch]["notaries"][notary]["ntx_count"],
                                 self.season_ntx_dict["servers"][server]["ntx_count"])*100,6)

                    # Server Epoch Notary Percentage of Server Score
                    self.season_ntx_dict["servers"][server]["epochs"][epoch]["notaries"][notary]["ntx_score"] = round(self.season_ntx_dict["servers"][server]["epochs"][epoch]["notaries"][notary]["ntx_score"],8)
                    self.season_ntx_dict["servers"][server]["epochs"][epoch]["notaries"][notary]["pct_of_server_ntx_score"] = round(
                        safe_div(self.season_ntx_dict["servers"][server]["epochs"][epoch]["notaries"][notary]["ntx_score"],
                                 self.season_ntx_dict["servers"][server]["ntx_score"])*100,6)


    def build_season_ntx_dict(self):
        logger.info(f"Building season ntx dict for {self.season}")
        self.prepopulate()
        self.add_scores_counts()
        self.add_global_percentages()
        self.add_coin_percentages()
        self.add_notary_percentages()
        self.add_server_percentages()
        return self.season_ntx_dict


    def clean_up(self):
        coin_ntx_season_row().delete(self.season)
        notary_ntx_season_row().delete(self.season)
        server_ntx_season_row().delete(self.season)


# Last Notarised tables
class last_notarisations():
    def __init__(self, season):
        self.season = season
        self.ntx_coin_last = {}
        self.last_nota = {}
        if self.season in SEASONS_INFO:
            self.season_last_ntx = query.get_notary_last_ntx()
            self.last_ntx_data = query.get_coin_last_ntx()
            self.notarised_last_data = query.get_notarised_last_data_by_coin()

    @print_runtime
    def update_coin_table(self):
        for coin in SEASONS_INFO[self.season]["coins"]:

            if coin not in self.last_ntx_data:
                self.last_ntx_data.update({coin: 0})

            if coin not in self.notarised_last_data:
                self.notarised_last_data.update({
                    coin: {
                        "block_height": 0,
                        "block_time": 0
                    }
                })

            row = self.get_coin_last_ntx_row_rowdata(coin)
            if row:
                row.update()


    def get_coin_last_ntx_row_rowdata(self, coin):
        data = self.notarised_last_data[coin]
        row = coin_last_ntx_row()
        row.season = self.season
        row.coin = coin
        row.kmd_ntx_blockheight = data["block_height"]
        row.kmd_ntx_blocktime = data["block_time"]
        if data["block_height"] > 0:
            if self.last_ntx_data[coin] < data["block_height"]:
                cols = 'server, notaries, opret, block_hash, block_height, \
                        block_time, txid, ac_ntx_blockhash, ac_ntx_height'
                conditions = f"block_height={row.kmd_ntx_blockheight} AND coin='{row.coin}'"
                last_ntx_data = query.select_from_table('notarised', cols, conditions)[0]

                row.server = last_ntx_data[0]
                row.notaries = last_ntx_data[1]
                row.opret = last_ntx_data[2]
                row.kmd_ntx_blockhash = last_ntx_data[3]
                row.kmd_ntx_blockheight = last_ntx_data[4]
                row.kmd_ntx_blocktime = last_ntx_data[5]
                row.kmd_ntx_txid = last_ntx_data[6]
                row.ac_ntx_blockhash = last_ntx_data[7]
                row.ac_ntx_height = last_ntx_data[8]
                return row

            else:
                logger.info(f"no new ntx for {row.coin}")
                return None

        return None


    @print_runtime
    def update_notary_table(self):

        for notary in SEASONS_INFO[self.season]["notaries"]:
            # handle where no ntx on record
            if notary not in self.season_last_ntx:
                self.season_last_ntx.update({notary:{}})

            self.last_nota.update({
                notary: query.get_notary_coin_last_nota(self.season, notary)
            })
            for coin in SEASONS_INFO[self.season]["coins"]:

                if coin not in self.season_last_ntx[notary]:
                    self.season_last_ntx[notary].update({coin:0})

                if coin not in self.last_nota[notary]:
                    self.last_nota[notary].update({
                        coin: {
                            "block_height": 0
                        }
                    })

        for notary in SEASONS_INFO[self.season]["notaries"]:
            for coin in SEASONS_INFO[self.season]["coins"]:
                row = self.get_notary_last_ntx_row_rowdata(notary, coin)
                if row:
                    row.update()


    def get_notary_last_ntx_row_rowdata(self, notary, coin):
            row = notary_last_ntx_row()
            row.season = self.season
            row.coin = coin
            row.notary = notary
            row.kmd_ntx_blockheight = self.last_nota[notary][coin]["block_height"]

            if row.kmd_ntx_blockheight > 0:
                if row.kmd_ntx_blockheight > self.season_last_ntx[notary][coin]:
                    logger.info(f"new {row.coin} ntx for {row.notary}")

                    cols = 'server, notaries, opret, block_hash, block_height, \
                            block_time, txid, ac_ntx_blockhash, ac_ntx_height'
                    conditions = f"block_height={row.kmd_ntx_blockheight} AND coin='{coin}'"
                    last_ntx_data = query.select_from_table('notarised', cols, conditions)[0]

                    row.server = last_ntx_data[0]
                    row.notaries = last_ntx_data[1]
                    row.opret = last_ntx_data[2]
                    row.kmd_ntx_blockhash = last_ntx_data[3]
                    row.kmd_ntx_blockheight = last_ntx_data[4]
                    row.kmd_ntx_blocktime = last_ntx_data[5]
                    row.kmd_ntx_txid = last_ntx_data[6]
                    row.ac_ntx_blockhash = last_ntx_data[7]
                    row.ac_ntx_height = last_ntx_data[8]
                    return row
                else:
                    logger.info(f"no new {row.coin} ntx for {row.notary}")
                    return None

            else:
                row.server = "N/A"
                row.notaries = []
                row.opret = "N/A"
                row.kmd_ntx_blockhash = "N/A"
                row.kmd_ntx_blockheight = 0
                row.kmd_ntx_blocktime = 0
                row.kmd_ntx_txid = "N/A"
                row.ac_ntx_blockhash = "N/A"
                row.ac_ntx_height = 0
                logger.info(f"no {row.coin} ntx for {row.notary}")
                return row


# BTC / LTC notarisations
def import_nn_btc_txids(season):
    i = 0
    num_addr = len(NOTARY_BTC_ADDRESSES[season])
    addresses = list(NOTARY_BTC_ADDRESSES[season])
    while len(addresses) > 0:
        notary_address = random.choice(addresses)
        i += 1
        logger.info(f">>> Categorising {notary_address} for {season} {i}/{num_addr}")
        txid_list = get_new_master_server_txids(notary_address, "BTC", season)
        logger.info(f"Processing ETA: {0.02*len(txid_list)} sec")

        j = 0
        num_txid = len(txid_list)
        for txid in txid_list:
            j += 1
            logger.info(f">>> Categorising {txid} for {j}/{num_txid}")
            txid_url = urls.get_notary_btc_txid_url(txid, False)
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


def import_nn_ltc_txids(season):

    if season not in NOTARY_LTC_ADDRESSES:
        logger.warning(f"{season} not in NOTARY_LTC_ADDRESSES")
        return

    num_addr = len(NOTARY_LTC_ADDRESSES[season])

    i = 0
    for notary_address in NOTARY_LTC_ADDRESSES[season]:
        j = 0
        i += 1
        txid_list = get_new_master_server_txids(notary_address, "LTC", season)
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
        resp = api.get_ltc_address_txids(notary_address, before_block)
        if "error" in resp:
            logger.info(f"Error in resp: {resp}")
            exit_loop = api.api_sleep_or_exit(resp, exit=True)
            if resp['error'] == 'Limits reached.':
                break
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


def get_new_master_server_txids(notary_address, coin, season):

    existing_txids = []
    if coin == "LTC":
        existing_txids = query.get_existing_nn_ltc_txids(notary_address, None, season)
        url = f"{OTHER_SERVER}/api/info/ltc_txid_list/?notary={notary_address}&season={season}"
        logger.info(f"{len(existing_txids)} existing txids in local DB detected for {notary_address} {season}")

    logger.info(url)
    r = requests.get(url)
    resp = r.json()
    txids = resp['results']

    new_txids = []
    for txid in txids:
        if txid not in existing_txids:
            new_txids.append(txid)
    new_txids = list(set(new_txids))

    if coin == "BTC":
        logger.info(f"{len(new_txids)} extra txids detected for notary_address {notary_address} {season}")

    if coin == "LTC":
        logger.info(f"{len(new_txids)} extra txids detected for notary_address {notary_address} {season}")

    return new_txids


# TODO: data not used or recorded anwhere, but keeping here for future.
def get_extra_ntx_data(coin, scriptPubKey_asm):
    if coin == "KMD":
        btc_txid = crypto.lil_endian(scriptPubKey_asm[72:136])
    elif coin not in noMoM:
        # not sure about this bit, need another source to validate the data
        try:
            start = 72+len(coin)*2+4
            end = 72+len(coin)*2+4+64
            MoM_hash = crypto.lil_endian(scriptPubKey_asm[start:end])
            MoM_depth = int(crypto.lil_endian(scriptPubKey_asm[end:]),16)
        except Exception as e:
            logger.debug(e)
    return



# Deprecated. Kept here for rescanning prior seasons where notarising to BTC

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
        resp = api.get_btc_address_txids(notary_address, before_block)
        if "error" in resp:
            logger.info(f"Error in resp: {resp}")
            exit_loop = api.api_sleep_or_exit(resp, exit=True)
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
