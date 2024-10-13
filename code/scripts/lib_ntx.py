#!/usr/bin/env python3.12
import time
import json
import random
import requests
import datetime
from datetime import datetime as dt
from functools import cached_property

import alerts
import lib_api as api
import lib_rpc as rpc
import lib_urls as urls
import lib_query as query
import lib_helper as helper
import lib_crypto as crypto
import lib_validate as validate
from decorators import print_runtime
from lib_const import *
from lib_dpow_const import noMoM
from const_seasons import SEASONS
from models import *
from logger import logger


class Notarised:
    def __init__(self, season, rescan=False):
        self.season = season
        self.rescan = rescan
        self.chain_tip = int(RPC["KMD"].getblockcount())
        self.start_block = self._determine_start_block()
        self.end_block = (
            SEASONS.INFO[self.season].get("post_season_end_block") or
            SEASONS.INFO[self.season]["end_block"]
        )
        self.chain_tip = min(self.chain_tip, self.end_block)
        self._existing_txids = None

    def _determine_start_block(self):
        """Determine the starting block based on the rescan flag."""
        return self.chain_tip - 24 * 60 if not self.rescan else SEASONS.INFO[self.season]["start_block"]

    @property
    def existing_txids(self):
        if self._existing_txids is None:
            self._existing_txids = query.get_existing_notarised_txids(self.season)
        return self._existing_txids

    @print_runtime
    def update_table(self):
        logger.info(f"Processing notarisations for {self.season}, blocks {self.start_block} - {self.end_block}")
        
        if not self.rescan:
            self.process_notarisations(self.start_block, self.end_block)
        else:
            logger.info(f"Recanning notarisations for {self.season}, blocks {self.start_block} - {self.end_block}")
            self.rescan_notarisations()

    def refresh_materialized_views(self):
        query.refresh_materialized_view(f"existing_notarised_txids_{self.season}", self.season)
        
        

    def process_notarisations(self, start, end):
        unrecorded_txids = self.get_missing_txids_list(start, end)
        self.update_notarisations(unrecorded_txids)

    def rescan_notarisations(self):
        windows = [
            (i, i + RESCAN_CHUNK_SIZE) for i in range(self.start_block, self.end_block, RESCAN_CHUNK_SIZE)
        ]
        if OTHER_SERVER.find("stats") == -1:
            windows.reverse()

        for i, window in enumerate(windows, start=1):
            logger.info(f"Processing notarisations for blocks in window {window[0]} - {window[1]} ({i} done, {len(windows)} remaining...)")
            unrecorded_txids = self.get_missing_txids_list(window[0], window[1])
            self.update_notarisations(unrecorded_txids)
            self._existing_txids += unrecorded_txids
            time.sleep(0.1)

    @print_runtime
    def get_missing_txids_list(self, start, end):
        logger.info(f"Getting unrecorded notarisation TXIDs for {self.season}, blocks {start} - {end}")
        all_txids = []

        while self.chain_tip - start > RESCAN_CHUNK_SIZE:
            logger.info(f"Adding {start} to {start + RESCAN_CHUNK_SIZE} ntx address txids...")
            all_txids += rpc.get_ntx_txids(start, start + RESCAN_CHUNK_SIZE)
            start += RESCAN_CHUNK_SIZE
            time.sleep(0.02)

        all_txids += rpc.get_ntx_txids(start, self.chain_tip)

        new_txids = list(set(all_txids) - set(self.existing_txids))
        logger.info(f"New TXIDs: {len(new_txids)}")
        random.shuffle(new_txids)
        return new_txids

    @print_runtime
    def update_notarisations(self, unrecorded_txids):
        logger.info(f"Updating KMD {len(unrecorded_txids)} notarisations...")
        for txid in unrecorded_txids:
            row_data = self.get_ntx_data(txid)
            if row_data:
                ntx_row = self.create_ntx_row(row_data)
                ntx_row.update()

    def create_ntx_row(self, row_data):
        ntx_row = NotarisedRow()
        (
            ntx_row.coin,
            ntx_row.block_height,
            ntx_row.block_time,
            ntx_row.block_datetime,
            ntx_row.block_hash,
            ntx_row.notaries,
            ntx_row.notary_addresses,
            ntx_row.ac_ntx_blockhash,
            ntx_row.ac_ntx_height,
            ntx_row.txid,
            ntx_row.opret
        ) = row_data
        ntx_row.season = self.season
        return ntx_row

    def get_import_row(self, txid_info):
        ntx_row = NotarisedRow()
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

        # Retrieve notary addresses if not provided
        if not txid_info["notary_addresses"]:
            ntx_row.notary_addresses = self.get_local_notary_addresses(ntx_row)

        else:
            ntx_row.notary_addresses = txid_info["notary_addresses"]
        
        return ntx_row

    def get_local_notary_addresses(self, ntx_row):
        if ntx_row.coin == "BTC":
            url = urls.get_notary_btc_txid_url(ntx_row.txid, True)
            local_info = requests.get(url).json()["results"]
            return get_local_addresses(local_info)

        elif ntx_row.coin == "LTC":
            url = urls.get_notary_ltc_txid_url(ntx_row.txid, True)
            local_info = requests.get(url).json()["results"]
            return helper.get_local_addresses(local_info)

        return []

    def get_ntx_data(self, txid):
        try:
            raw_tx = RPC["KMD"].getrawtransaction(txid, 1)
            if 'blocktime' in raw_tx:
                return self.extract_ntx_data(raw_tx, txid)
        except Exception as e:
            alerts.send_telegram(f"[{__name__}] [get_ntx_data] TXID: {txid}. Error: {e}")

        return None

    def extract_ntx_data(self, raw_tx, txid):
        block_hash = raw_tx['blockhash']
        dest_addrs = raw_tx["vout"][0]['scriptPubKey']['addresses']
        if dest_addrs and NTX_ADDR in dest_addrs:
            block_time = raw_tx['blocktime']
            block_datetime = dt.fromtimestamp(block_time, datetime.UTC)
            this_block_height = raw_tx['height']

            if len(raw_tx['vin']) > 1:
                notary_list, address_list = helper.get_notary_address_lists(raw_tx['vin'])
                opret = raw_tx['vout'][1]['scriptPubKey']['asm']
                if "OP_RETURN" in opret:
                    return self.build_row_data(opret, block_hash, this_block_height, block_time, block_datetime, notary_list, address_list, txid)

        return None

    def build_row_data(self, opret, block_hash, this_block_height, block_time, block_datetime, notary_list, address_list, txid):
        scriptPubKey_asm = opret.replace("OP_RETURN ", "")
        ac_ntx_blockhash = crypto.lil_endian(scriptPubKey_asm[:64])
        ac_ntx_height = int(crypto.lil_endian(scriptPubKey_asm[64:72]), 16)

        coin = crypto.get_opret_ticker(scriptPubKey_asm)

        # Gets rid of extra data by matching to known coins
        for x in KNOWN_COINS:
            if len(x) > 2 and x not in EXCLUDE_DECODE_OPRET_COINS:
                if coin.endswith(x):
                    coin = x

        if coin.upper() == coin:  # Check if the coin is in uppercase
            return (coin, this_block_height, block_time, block_datetime, block_hash, notary_list, address_list, ac_ntx_blockhash, ac_ntx_height, txid, opret)

        return None

    @print_runtime
    def clean_up(self):
        """ Re-processes existing data to let model validation enforce validation """
        results = query.get_notarised_data_for_season(self.season)
        for item in results:
            row = NotarisedRow()
            self.populate_row(row, item)
            row.update()

    def populate_row(self, row, item):
        row.coin = item[0]
        row.block_height = item[1]
        row.block_time = item[2]
        row.block_datetime = item[3]
        row.block_hash = item[4]
        row.notaries = sorted(item[5])
        row.notary_addresses = sorted(item[6])
        row.ac_ntx_blockhash = item[7]
        row.ac_ntx_height = item[8]
        row.txid = item[9]
        row.opret = item[10]
        row.season = item[11]
        row.server = item[12]
        row.epoch = item[13]
        row.score_value = item[14]
        row.scored = item[15]

    @print_runtime
    def import_ntx(self, server, coin):
        url = urls.get_ntxid_list_url(self.season, server, coin, False)
        response = requests.get(url)
        if response.status_code == 429:
            time.sleep(0.5)
            return

        import_txids = response.json()["results"]
        new_txids = list(set(import_txids) - set(self.existing_txids))
        logger.info(f"NTX TXIDs to import: {len(new_txids)}")
        logger.info(f"Processing ETA: {0.03 * len(new_txids)} sec")

        for txid in new_txids:
            time.sleep(0.2)
            txid_url = urls.get_notarised_txid_url(txid, False)
            self.import_txid(txid_url)

    def import_txid(self, txid_url):
        response = requests.get(txid_url)
        try:
            for txid_info in response.json()["results"]:
                ntx_row = self.get_import_row(txid_info)
                ntx_row.update()
        except Exception as e:
            logger.error(f"Error importing {txid_url}: {e} | response.text: {response.text}")


class NtxDailyStats:
    def __init__(self, season, rescan=False):
        self.season = season
        self.rescan = rescan
        self.dpow_main_coins = self.get_dpow_coins("Main")
        self.dpow_3p_coins = self.get_dpow_coins("Third_Party")
        self.notary_ntx_pct = {}
        self.season_notaries = helper.get_season_notaries(self.season)

    def get_dpow_coins(self, server_type):
        """Retrieve the coins associated with the specified server type."""
        return SEASONS.INFO[self.season]["servers"].get(server_type, {}).get("coins", [])

    def update_daily_ntx_tables(self):
        """Update daily notarised tables for the specified season."""
        season_start_dt = dt.fromtimestamp(SEASONS.INFO[self.season]["start_time"], datetime.UTC)
        season_end_dt = dt.fromtimestamp(SEASONS.INFO[self.season]["end_time"], datetime.UTC)
        start = season_start_dt.date()
        end = datetime.date.today()

        if time.time() > SEASONS.INFO[self.season]["end_time"]:
            end = season_end_dt.date()

        if not self.rescan:
            logger.info(f"Starting {self.season} scan from 3 days ago...")
            start = end - datetime.timedelta(days=3)

        logger.info(f"Updating [notarised_coin_daily] for {self.season} from {start} to {end}")

        while start <= end:
            self.update_daily_ntx_for_date(start)
            start += datetime.timedelta(days=1)

    def update_daily_ntx_for_date(self, date):
        """Update daily notarised stats for a specific date."""
        logger.info(f"Updating [notarised_coin_daily] for {date}")
        self.day = date
        self.notary_counts = {
            'master_server_count':0,
            'main_server_count':0,
            'third_party_server_count':0,
            'other_server_count':0,
            'total_ntx_count':0
        }
        for notary in self.season_notaries:
            self.notary_counts.update({
            notary: {
                'master_server_count':0,
                'main_server_count':0,
                'third_party_server_count':0,
                'other_server_count':0,
                'total_ntx_count':0
            }})
        self.coins_aggr_resp = query.get_notarised_coin_date_aggregates(self.season, self.day)
        self.coin_ntx_count_dict = self.get_coin_ntx_count_dict_for_day()
        self.calculate_daily_ntx_count_pct()        
        self.update_daily_coin_ntx()
        self.update_daily_count_ntx()

    def update_daily_coin_ntx(self):
        """Update daily coin ntx counts."""
        logger.info(f"Getting daily ntx coin counts for {self.day}")
        for item in self.coins_aggr_resp:
            row = notarised_coin_daily_row()
            row.season = self.season
            row.coin = item[0]
            row.ntx_count = item[3]
            row.notarised_date = str(self.day)
            row.update()

    def update_daily_count_ntx(self):
        """Update daily ntx counts for notaries."""
        for notary in self.notary_ntx_count_dict:
            #logger.info(self.notary_ntx_count_dict)
            #logger.info(notary)
            #logger.info(self.notary_ntx_count_dict[notary])
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

    def calculate_daily_ntx_count_pct(self):
        """Calculate notary ntx percentages for coins and return counts."""

        self.notary_ntx_count_dict = self.get_notary_ntx_count_dict_for_day()
        for notary, coin_counts in self.notary_ntx_count_dict.items():
            total_count = sum(coin_counts.values())
            self.notary_ntx_pct[notary] = {coin: round(count / self.coin_ntx_count_dict[coin] * 100, 2)
                                    for coin, count in coin_counts.items()}
            self.notary_counts[notary]["total_ntx_count"] = total_count
            for coin in coin_counts.keys():
                self.update_notary_counts(notary, coin)

    def update_notary_counts(self, notary, coin):
        """Update notary counts based on the coin type."""
        count = self.notary_ntx_count_dict[notary][coin]
        if coin == "KMD":
            self.notary_counts[notary]["master_server_count"] += count
        elif coin in self.dpow_main_coins:
            self.notary_counts[notary]["main_server_count"] += count
        elif coin in self.dpow_3p_coins:
            self.notary_counts[notary]["third_party_server_count"] += count
        else:
            self.notary_counts[notary]["other_server_count"] += count

        self.notary_counts[notary]["total_ntx_count"] += count

    def get_coin_ntx_count_dict_for_day(self):
        """Retrieve daily ntx totals for each coin."""
        return {item[0]: item[3] for item in self.coins_aggr_resp}

    def get_notary_ntx_count_dict_for_day(self):
        """Retrieve daily ntx counts for each notary."""
        notary_ntx_count_dict = {}
        notarised_on_day = query.get_notarised_for_day(self.season, self.day)

        for item in notarised_on_day:
            coin = item[0]
            for notary in item[1]:
                notary_ntx_count_dict.setdefault(notary, {}).setdefault(coin, 0)
                notary_ntx_count_dict[notary][coin] += 1

        return notary_ntx_count_dict


class LastNotarisations:
    def __init__(self, season):
        self.season = season
        self.ntx_coin_last = {}
        self.last_nota = {}

        if self.season in SEASONS.INFO:
            self.season_last_ntx = query.get_notary_last_ntx()
            self.last_ntx_data = query.get_coin_last_ntx()
            self.notarised_last_data = query.get_notarised_last_data_by_coin()

    @print_runtime
    def update_coin_table(self):
        """Update the coin table with the latest notarization information."""
        for coin in SEASONS.INFO[self.season]["coins"]:
            self.initialize_coin_data(coin)
            row = self.get_coin_last_ntx_row_rowdata(coin)

            if row:
                row.update()

    def initialize_coin_data(self, coin):
        """Initialize data for a specific coin if not present."""
        if coin not in self.last_ntx_data:
            self.last_ntx_data[coin] = 0

        if coin not in self.notarised_last_data:
            self.notarised_last_data[coin] = {"block_height": 0, "block_time": 0}

    def get_coin_last_ntx_row_rowdata(self, coin):
        """Get the last notarization row data for a specific coin."""
        data = self.notarised_last_data[coin]
        row = coin_last_ntx_row()
        row.season = self.season
        row.coin = coin
        row.kmd_ntx_blockheight = data["block_height"]
        row.kmd_ntx_blocktime = data["block_time"]

        if data["block_height"] > 0:
            return self.fetch_last_ntx_data(row)

        logger.info(f"No new ntx for {row.coin}")
        return None

    def fetch_last_ntx_data(self, row):
        """Fetch and populate last notarization data for the row."""
        if self.last_ntx_data[row.coin] < row.kmd_ntx_blockheight:
            logger.info(f"Fetching last ntx data for {row.coin}...")

            cols = 'server, notaries, opret, block_hash, block_height, block_time, txid, ac_ntx_blockhash, ac_ntx_height'
            conditions = f"block_height={row.kmd_ntx_blockheight} AND coin='{row.coin}'"
            last_ntx_data = query.select_from_table('notarised', cols, conditions)[0]

            row.server, row.notaries, row.opret, row.kmd_ntx_blockhash, row.kmd_ntx_blockheight, row.kmd_ntx_blocktime, row.kmd_ntx_txid, row.ac_ntx_blockhash, row.ac_ntx_height = last_ntx_data
            return row

        # logger.info(f"No new ntx for {row.coin}")
        return None

    @print_runtime
    def update_notary_table(self):
        """Update the notary table with the latest notarization information."""
        for notary in SEASONS.INFO[self.season]["notaries"]:
            self.initialize_notary_data(notary)

            self.last_nota[notary] = query.get_notary_coin_last_nota(self.season, notary)

            for coin in SEASONS.INFO[self.season]["coins"]:
                self.initialize_coin_for_notary(notary, coin)

        for notary in SEASONS.INFO[self.season]["notaries"]:
            for coin in SEASONS.INFO[self.season]["coins"]:
                row = self.get_notary_last_ntx_row_rowdata(notary, coin)
                if row:
                    row.update()

    def initialize_notary_data(self, notary):
        """Initialize data for a specific notary if not present."""
        if notary not in self.season_last_ntx:
            self.season_last_ntx[notary] = {}

    def initialize_coin_for_notary(self, notary, coin):
        """Initialize coin data for a specific notary."""
        if coin not in self.season_last_ntx[notary]:
            self.season_last_ntx[notary][coin] = 0

        if coin not in self.last_nota[notary]:
            self.last_nota[notary][coin] = {"block_height": 0}

    def get_notary_last_ntx_row_rowdata(self, notary, coin):
        """Get the last notarization row data for a specific notary and coin."""
        row = notary_last_ntx_row()
        row.season = self.season
        row.coin = coin
        row.notary = notary
        row.kmd_ntx_blockheight = self.last_nota[notary][coin]["block_height"]

        if row.kmd_ntx_blockheight > 0:
            return self.fetch_notary_last_ntx_data(row, notary, coin)

        self.set_empty_row_data(row)
        # logger.info(f"No {row.coin} ntx for {row.notary}")
        return row

    def fetch_notary_last_ntx_data(self, row, notary, coin):
        """Fetch and populate last notarization data for a notary."""
        if row.kmd_ntx_blockheight > self.season_last_ntx[notary][coin]:
            logger.info(f"New {row.coin} ntx for {row.notary}")

            cols = 'server, notaries, opret, block_hash, block_height, block_time, txid, ac_ntx_blockhash, ac_ntx_height'
            conditions = f"block_height={row.kmd_ntx_blockheight} AND coin='{coin}'"
            last_ntx_data = query.select_from_table('notarised', cols, conditions)[0]

            row.server, row.notaries, row.opret, row.kmd_ntx_blockhash, row.kmd_ntx_blockheight, row.kmd_ntx_blocktime, row.kmd_ntx_txid, row.ac_ntx_blockhash, row.ac_ntx_height = last_ntx_data
            return row

        # logger.info(f"No new {row.coin} ntx for {row.notary}")
        return None

    def set_empty_row_data(self, row):
        """Set the row data to indicate no transactions found."""
        row.server = "N/A"
        row.notaries = []
        row.opret = "N/A"
        row.kmd_ntx_blockhash = "N/A"
        row.kmd_ntx_blockheight = 0
        row.kmd_ntx_blocktime = 0
        row.kmd_ntx_txid = "N/A"
        row.ac_ntx_blockhash = "N/A"
        row.ac_ntx_height = 0


# Season Notarised tables
class NtxSeasonStats:
    def __init__(self, season):
        self.season = season
        self.season_coins = helper.get_season_coins(self.season)
        self.season_notaries = helper.get_season_notaries(self.season)
        self.epoch_scores_dict = validate.get_epoch_scores_dict(self.season)
        self.season_servers = self.get_filtered_servers(helper.get_season_servers(self.season))
        self.season_ntx_dict = {
            "ntx_count": 0,
            "ntx_score": 0,
            "pct_of_season_ntx_count": 100,
            "pct_of_season_ntx_score": 100
        }


    def get_default_ntx_item_dict(self, item):
        return {
            item: {
                "ntx_count": 0,
                "ntx_score": 0,
                "pct_of_season_ntx_count": 0,
                "pct_of_season_ntx_score": 0,
            }
        }

    def prepopulate(self):
        self.season_ntx_dict.update(self.get_default_ntx_item_dict("coins"))
        self.season_ntx_dict.update(self.get_default_ntx_item_dict("servers"))
        self.season_ntx_dict.update(self.get_default_ntx_item_dict("notaries"))
        for coin in self.season_coins:
            self.initialize_coin(coin)
        for notary in self.season_notaries:
            self.initialize_notary(notary)
        for server in self.season_servers:
            self.initialize_server(server)
        return self.season_ntx_dict

    def initialize_coin(self, coin):
        self.season_ntx_dict["coins"].update(self.get_default_ntx_item_dict(coin))
        self.season_ntx_dict["coins"][coin].update(self.get_default_ntx_item_dict("notaries"))
        self.season_ntx_dict["coins"][coin].update(self.get_default_ntx_item_dict("servers"))
        
        for notary in self.season_notaries:
            self.season_ntx_dict["coins"][coin]["notaries"].update(self.get_default_ntx_item_dict(notary))

        for server in self.season_servers:            
            server_epochs = list(set(get_season_server_epochs(self.season, server)).difference({"Unofficial", "None"}))
            server_coins = helper.get_season_coins(self.season, server)

            if coin in server_coins:
                self.season_ntx_dict["coins"][coin]["servers"].update(self.get_default_ntx_item_dict(server))
                self.season_ntx_dict["coins"][coin]["servers"][server].update(self.get_default_ntx_item_dict("epochs"))
                self.season_ntx_dict["coins"][coin]["servers"][server].update(self.get_default_ntx_item_dict("notaries"))

                for notary in self.season_notaries:
                    self.season_ntx_dict["coins"][coin]["servers"][server]["notaries"].update(self.get_default_ntx_item_dict(notary))
                for epoch in server_epochs:
                    epoch_coins = helper.get_season_coins(self.season, server, epoch)
                    if coin in epoch_coins:
                        self.season_ntx_dict["coins"][coin]["servers"][server]["epochs"].update(self.get_default_ntx_item_dict(epoch))
                        self.season_ntx_dict["coins"][coin]["servers"][server]["epochs"][epoch].update(self.get_default_ntx_item_dict("notaries"))
                        self.season_ntx_dict["coins"][coin]["servers"][server]["epochs"][epoch]["score_per_ntx"] = float(self.epoch_scores_dict[server][epoch])
                        for notary in self.season_notaries:
                            self.season_ntx_dict["coins"][coin]["servers"][server]["epochs"][epoch]["notaries"].update(self.get_default_ntx_item_dict(notary))


    def initialize_notary(self, notary):
        self.season_ntx_dict["notaries"].update(self.get_default_ntx_item_dict(notary))
        self.season_ntx_dict["notaries"][notary].update(self.get_default_ntx_item_dict("coins"))
        self.season_ntx_dict["notaries"][notary].update(self.get_default_ntx_item_dict("servers"))
        for coin in self.season_coins:
            self.season_ntx_dict["notaries"][notary]["coins"].update(self.get_default_ntx_item_dict(coin))
        for server in self.season_servers:
            server_epochs = list(set(get_season_server_epochs(self.season, server)).difference({"Unofficial", "None"}))
            self.season_ntx_dict["notaries"][notary]["servers"].update(self.get_default_ntx_item_dict(server))
            self.season_ntx_dict["notaries"][notary]["servers"][server].update(self.get_default_ntx_item_dict("coins"))
            self.season_ntx_dict["notaries"][notary]["servers"][server].update(self.get_default_ntx_item_dict("epochs"))
            for epoch in server_epochs:
                self.season_ntx_dict["notaries"][notary]["servers"][server]["epochs"].update(self.get_default_ntx_item_dict(epoch))
                self.season_ntx_dict["notaries"][notary]["servers"][server]["epochs"][epoch].update(self.get_default_ntx_item_dict("coins"))
                self.season_ntx_dict["notaries"][notary]["servers"][server]["epochs"][epoch]["score_per_ntx"] = float(self.epoch_scores_dict[server][epoch])
                epoch_coins = helper.get_season_coins(self.season, server, epoch)
                for coin in epoch_coins:
                    self.season_ntx_dict["notaries"][notary]["servers"][server]["epochs"][epoch]["coins"].update(self.get_default_ntx_item_dict(coin))
                    
            server_coins = helper.get_season_coins(self.season, server)
            for coin in server_coins:
                self.season_ntx_dict["notaries"][notary]["servers"][server]["coins"].update(self.get_default_ntx_item_dict(coin))



    def initialize_server(self, server):
        server_coins = helper.get_season_coins(self.season, server)
        self.season_ntx_dict["servers"].update(self.get_default_ntx_item_dict(server))
        self.season_ntx_dict["servers"][server].update(self.get_default_ntx_item_dict("coins"))
        self.season_ntx_dict["servers"][server].update(self.get_default_ntx_item_dict("epochs"))
        self.season_ntx_dict["servers"][server].update(self.get_default_ntx_item_dict("notaries"))
        
        for notary in self.season_notaries:
            self.season_ntx_dict["servers"][server]["notaries"].update(self.get_default_ntx_item_dict(notary))
            self.season_ntx_dict["servers"][server]["notaries"][notary].update(self.get_default_ntx_item_dict("coins"))
            self.season_ntx_dict["servers"][server]["notaries"][notary].update(self.get_default_ntx_item_dict("epochs"))
            for coin in server_coins:
                self.season_ntx_dict["servers"][server]["notaries"][notary]["coins"].update(self.get_default_ntx_item_dict(coin))
            server_epochs = list(set(get_season_server_epochs(self.season, server)).difference({"Unofficial", "None"}))
            for epoch in server_epochs:
                self.season_ntx_dict["servers"][server]["notaries"][notary]["epochs"].update(self.get_default_ntx_item_dict(epoch))
        
        for coin in server_coins:
            self.season_ntx_dict["servers"][server]["coins"].update(self.get_default_ntx_item_dict(coin))
            self.season_ntx_dict["servers"][server]["coins"][coin].update(self.get_default_ntx_item_dict("notaries"))
            for notary in self.season_notaries:                    
                self.season_ntx_dict["servers"][server]["coins"][coin]["notaries"].update(self.get_default_ntx_item_dict(notary))

        server_epochs = list(set(get_season_server_epochs(self.season, server)).difference({"Unofficial", "None"}))
        for epoch in server_epochs:
            self.season_ntx_dict["servers"][server]["epochs"].update(self.get_default_ntx_item_dict(epoch))
            self.season_ntx_dict["servers"][server]["epochs"][epoch].update(self.get_default_ntx_item_dict("coins"))
            self.season_ntx_dict["servers"][server]["epochs"][epoch].update(self.get_default_ntx_item_dict("notaries"))
            self.season_ntx_dict["servers"][server]["epochs"][epoch]["score_per_ntx"] = float(self.epoch_scores_dict[server][epoch])
            for notary in self.season_notaries:
                self.season_ntx_dict["servers"][server]["epochs"][epoch]["notaries"].update(self.get_default_ntx_item_dict(notary))

            for coin in helper.get_season_coins(self.season, server, epoch):
                self.season_ntx_dict["servers"][server]["epochs"][epoch]["coins"].update(self.get_default_ntx_item_dict(coin))
                self.season_ntx_dict["servers"][server]["epochs"][epoch]["coins"][coin].update(self.get_default_ntx_item_dict("notaries"))
                for notary in self.season_notaries:
                    self.season_ntx_dict["servers"][server]["epochs"][epoch]["coins"][coin]["notaries"].update(self.get_default_ntx_item_dict(notary))





    @print_runtime
    def update_ntx_season_stats_tables(self):
        if self.season in SEASONS.INFO:
            self.build_season_ntx_dict()
            self.update_rows(self.season_coins, self.get_coin_row)
            self.update_rows(self.season_notaries, self.get_notary_row)
            # self.update_rows(self.season_servers, self.get_server_row)

    def update_rows(self, items, row_getter):
        for item in items:
            row = row_getter(item)
            row.update()

    def get_row(self, item, row_class, data_key):
        row = row_class()
        row.season = self.season
        row.timestamp = int(time.time())
        if row_class == CoinNtxSeasonRow:
            row.coin = item
            row.coin_data = json.dumps(self.season_ntx_dict[data_key].get(item, {}))
        if row_class == NotaryNtxSeasonRow:
            row.notary = item
            row.notary_data = json.dumps(self.season_ntx_dict[data_key].get(item, {}))
        if row_class == ServerNtxSeasonRow:
            row.server = item
            row.server_data = json.dumps(self.season_ntx_dict[data_key].get(item, {}))
            
        row_data = self.season_ntx_dict[data_key].get(item, {})
        row.data = json.dumps(row_data)
        
        return row

    def get_coin_row(self, coin):
        return self.get_row(coin, CoinNtxSeasonRow, "coins")

    def get_notary_row(self, notary):
        return self.get_row(notary, NotaryNtxSeasonRow, "notaries")

    def get_server_row(self, server):
        return self.get_row(server, ServerNtxSeasonRow, "servers")



    def get_filtered_servers(self, servers):
        return list(set(servers).difference({"Unofficial", "LTC", "BTC", "None"}))


    def add_scores_counts(self):
        total_notaries = len(SEASONS.INFO[self.season]['notaries'])
        
        for i, notary in enumerate(self.season_notaries, start=1):
            logger.info(f"[season_totals] {self.season} {i}/{total_notaries}: {notary}")
            official_ntx_results = query.get_official_ntx_results(self.season, ["server", "epoch", "coin"], None, None, None, notary)

            for item in official_ntx_results:
                server, epoch, coin, server_epoch_coin_count, server_epoch_coin_score = item

                if not self.is_excluded_server_epoch(server, epoch):
                    if coin != 'KMD' or (coin == server and server == epoch):
                        self.update_global_totals(server_epoch_coin_count, server_epoch_coin_score, coin, server, notary, epoch)

        # self.normalize_ntx_counts(13)
        self.season_ntx_dict["ntx_score"] = round(self.season_ntx_dict["ntx_score"], 8)

    def is_excluded_server_epoch(self, server, epoch):
        """Check if the server and epoch are in the excluded set."""
        return bool({server, epoch}.intersection({"Unofficial", "LTC", "BTC", "None"}))

    def update_global_totals(self, count, score, coin, server, notary, epoch):
        """Update all global totals in the season_ntx_dict."""
        self.season_ntx_dict["ntx_count"] += count
        self.season_ntx_dict["ntx_score"] += float(score)
        
        self.season_ntx_dict["coins"]["ntx_count"] += count
        self.season_ntx_dict["coins"]["ntx_score"] += float(score)
        self.season_ntx_dict["coins"][coin]["ntx_count"] += count
        self.season_ntx_dict["coins"][coin]["ntx_score"] += float(score)
        self.season_ntx_dict["coins"][coin]["notaries"]["ntx_count"] += count
        self.season_ntx_dict["coins"][coin]["notaries"]["ntx_score"] += float(score)
        self.season_ntx_dict["coins"][coin]["notaries"][notary]["ntx_count"] += count
        self.season_ntx_dict["coins"][coin]["notaries"][notary]["ntx_score"] += float(score)
        self.season_ntx_dict["coins"][coin]["servers"]["ntx_count"] += count
        self.season_ntx_dict["coins"][coin]["servers"]["ntx_score"] += float(score)
        self.season_ntx_dict["coins"][coin]["servers"][server]["ntx_count"] += count
        self.season_ntx_dict["coins"][coin]["servers"][server]["ntx_score"] += float(score)
        self.season_ntx_dict["coins"][coin]["servers"][server]["notaries"]["ntx_count"] += count
        self.season_ntx_dict["coins"][coin]["servers"][server]["notaries"]["ntx_score"] += float(score)
        self.season_ntx_dict["coins"][coin]["servers"][server]["notaries"][notary]["ntx_count"] += count
        self.season_ntx_dict["coins"][coin]["servers"][server]["notaries"][notary]["ntx_score"] += float(score)
        self.season_ntx_dict["coins"][coin]["servers"][server]["epochs"]["ntx_count"] += count
        self.season_ntx_dict["coins"][coin]["servers"][server]["epochs"]["ntx_score"] += float(score)
        self.season_ntx_dict["coins"][coin]["servers"][server]["epochs"][epoch]["ntx_count"] += count
        self.season_ntx_dict["coins"][coin]["servers"][server]["epochs"][epoch]["ntx_score"] += float(score)
        self.season_ntx_dict["coins"][coin]["servers"][server]["epochs"][epoch]["notaries"]["ntx_count"] += count
        self.season_ntx_dict["coins"][coin]["servers"][server]["epochs"][epoch]["notaries"]["ntx_score"] += float(score)
        self.season_ntx_dict["coins"][coin]["servers"][server]["epochs"][epoch]["notaries"][notary]["ntx_count"] += count
        self.season_ntx_dict["coins"][coin]["servers"][server]["epochs"][epoch]["notaries"][notary]["ntx_score"] += float(score)

        self.season_ntx_dict["notaries"]["ntx_count"] += count
        self.season_ntx_dict["notaries"]["ntx_score"] += float(score)
        self.season_ntx_dict["notaries"][notary]["ntx_count"] += count
        self.season_ntx_dict["notaries"][notary]["ntx_score"] += float(score)
        
        self.season_ntx_dict["notaries"][notary]["coins"]["ntx_count"] += count
        self.season_ntx_dict["notaries"][notary]["coins"]["ntx_score"] += float(score)
        self.season_ntx_dict["notaries"][notary]["coins"][coin]["ntx_count"] += count
        self.season_ntx_dict["notaries"][notary]["coins"][coin]["ntx_score"] += float(score)
        
        self.season_ntx_dict["notaries"][notary]["servers"]["ntx_count"] += count
        self.season_ntx_dict["notaries"][notary]["servers"]["ntx_score"] += float(score)
        self.season_ntx_dict["notaries"][notary]["servers"][server]["ntx_count"] += count
        self.season_ntx_dict["notaries"][notary]["servers"][server]["ntx_score"] += float(score)
        self.season_ntx_dict["notaries"][notary]["servers"][server]["coins"]["ntx_count"] += count
        self.season_ntx_dict["notaries"][notary]["servers"][server]["coins"]["ntx_score"] += float(score)
        self.season_ntx_dict["notaries"][notary]["servers"][server]["coins"][coin]["ntx_count"] += count
        self.season_ntx_dict["notaries"][notary]["servers"][server]["coins"][coin]["ntx_score"] += float(score)
        self.season_ntx_dict["notaries"][notary]["servers"][server]["epochs"]["ntx_count"] += count
        self.season_ntx_dict["notaries"][notary]["servers"][server]["epochs"]["ntx_score"] += float(score)
        self.season_ntx_dict["notaries"][notary]["servers"][server]["epochs"][epoch]["ntx_count"] += count
        self.season_ntx_dict["notaries"][notary]["servers"][server]["epochs"][epoch]["ntx_score"] += float(score)
        self.season_ntx_dict["notaries"][notary]["servers"][server]["epochs"][epoch]["coins"]["ntx_count"] += count
        self.season_ntx_dict["notaries"][notary]["servers"][server]["epochs"][epoch]["coins"]["ntx_score"] += float(score)
        self.season_ntx_dict["notaries"][notary]["servers"][server]["epochs"][epoch]["coins"][coin]["ntx_count"] += count
        self.season_ntx_dict["notaries"][notary]["servers"][server]["epochs"][epoch]["coins"][coin]["ntx_score"] += float(score)

        self.season_ntx_dict["servers"]["ntx_count"] += count
        self.season_ntx_dict["servers"]["ntx_score"] += float(score)
        self.season_ntx_dict["servers"][server]["ntx_count"] += count
        self.season_ntx_dict["servers"][server]["ntx_score"] += float(score)
        self.season_ntx_dict["servers"][server]["coins"]["ntx_count"] += count
        self.season_ntx_dict["servers"][server]["coins"]["ntx_score"] += float(score)
        self.season_ntx_dict["servers"][server]["coins"][coin]["ntx_count"] += count
        self.season_ntx_dict["servers"][server]["coins"][coin]["ntx_score"] += float(score)
        self.season_ntx_dict["servers"][server]["coins"][coin]["notaries"]["ntx_count"] += count
        self.season_ntx_dict["servers"][server]["coins"][coin]["notaries"]["ntx_score"] += float(score)
        self.season_ntx_dict["servers"][server]["coins"][coin]["notaries"][notary]["ntx_count"] += count
        self.season_ntx_dict["servers"][server]["coins"][coin]["notaries"][notary]["ntx_score"] += float(score)
        self.season_ntx_dict["servers"][server]["epochs"]["ntx_count"] += count
        self.season_ntx_dict["servers"][server]["epochs"]["ntx_score"] += float(score)
        self.season_ntx_dict["servers"][server]["epochs"][epoch]["ntx_count"] += count
        self.season_ntx_dict["servers"][server]["epochs"][epoch]["ntx_score"] += float(score)
        self.season_ntx_dict["servers"][server]["epochs"][epoch]["coins"]["ntx_count"] += count
        self.season_ntx_dict["servers"][server]["epochs"][epoch]["coins"]["ntx_score"] += float(score)
        self.season_ntx_dict["servers"][server]["epochs"][epoch]["coins"][coin]["ntx_count"] += count
        self.season_ntx_dict["servers"][server]["epochs"][epoch]["coins"][coin]["ntx_score"] += float(score)
        self.season_ntx_dict["servers"][server]["epochs"][epoch]["coins"][coin]["notaries"]["ntx_count"] += count
        self.season_ntx_dict["servers"][server]["epochs"][epoch]["coins"][coin]["notaries"]["ntx_score"] += float(score)
        self.season_ntx_dict["servers"][server]["epochs"][epoch]["coins"][coin]["notaries"][notary]["ntx_count"] += count
        self.season_ntx_dict["servers"][server]["epochs"][epoch]["coins"][coin]["notaries"][notary]["ntx_score"] += float(score)
        self.season_ntx_dict["servers"][server]["epochs"][epoch]["notaries"]["ntx_count"] += count
        self.season_ntx_dict["servers"][server]["epochs"][epoch]["notaries"]["ntx_score"] += float(score)
        self.season_ntx_dict["servers"][server]["epochs"][epoch]["notaries"][notary]["ntx_count"] += count
        self.season_ntx_dict["servers"][server]["epochs"][epoch]["notaries"][notary]["ntx_score"] += float(score)
        self.season_ntx_dict["servers"][server]["notaries"]["ntx_count"] += count
        self.season_ntx_dict["servers"][server]["notaries"]["ntx_score"] += float(score)
        self.season_ntx_dict["servers"][server]["notaries"][notary]["ntx_count"] += count
        self.season_ntx_dict["servers"][server]["notaries"][notary]["ntx_score"] += float(score)
        self.season_ntx_dict["servers"][server]["notaries"][notary]["coins"]["ntx_count"] += count
        self.season_ntx_dict["servers"][server]["notaries"][notary]["coins"]["ntx_score"] += float(score)
        self.season_ntx_dict["servers"][server]["notaries"][notary]["coins"][coin]["ntx_count"] += count
        self.season_ntx_dict["servers"][server]["notaries"][notary]["coins"][coin]["ntx_score"] += float(score)



    def normalize_ntx_counts(self, divisor):
        """Normalize ntx counts by dividing by the specified divisor."""
        self.season_ntx_dict["ntx_count"] = round(self.season_ntx_dict["ntx_count"] / divisor)

        for coin in self.season_coins:
            self.season_ntx_dict["coins"][coin]["ntx_count"] = round(self.season_ntx_dict["coins"][coin]["ntx_count"] / divisor)

            for server in self.season_ntx_dict["coins"][coin]["servers"]:
                self.season_ntx_dict["coins"][coin]["servers"][server]["ntx_count"] = round(self.season_ntx_dict["coins"][coin]["servers"][server]["ntx_count"] / divisor)

                for epoch in self.season_ntx_dict["coins"][coin]["servers"][server]["epochs"]:
                    if "ntx_count" not in self.season_ntx_dict["coins"][coin]["servers"][server]["epochs"][epoch]:
                        self.season_ntx_dict["coins"][coin]["servers"][server]["epochs"][epoch]["ntx_count"] = 0
                    else:    
                        self.season_ntx_dict["coins"][coin]["servers"][server]["epochs"][epoch]["ntx_count"] = round(self.season_ntx_dict["coins"][coin]["servers"][server]["epochs"][epoch]["ntx_count"] / divisor)

        for server in self.season_ntx_dict["servers"]:
            self.season_ntx_dict["servers"][server]["ntx_count"] = round(self.season_ntx_dict["servers"][server]["ntx_count"] / divisor)

            for coin in self.season_ntx_dict["servers"][server]["coins"]:
                self.season_ntx_dict["servers"][server]["coins"][coin]["ntx_count"] = round(self.season_ntx_dict["servers"][server]["coins"][coin]["ntx_count"] / divisor)

                for epoch in self.season_ntx_dict["servers"][server]["epochs"]:
                    self.season_ntx_dict["servers"][server]["epochs"][epoch]["ntx_count"] = round(self.season_ntx_dict["servers"][server]["epochs"][epoch]["ntx_count"] / divisor)

                    for _coin in self.season_ntx_dict["servers"][server]["epochs"][epoch]["coins"]:
                        self.season_ntx_dict["servers"][server]["epochs"][epoch]["coins"][_coin]["ntx_count"] = round(self.season_ntx_dict["servers"][server]["epochs"][epoch]["coins"][_coin]["ntx_count"] / divisor)



    def add_global_percentages(self):
        # Helper function to calculate and assign percentages
        def calculate_and_assign_percentage(data, key, count_key, score_key):
            if key in data:
                if count_key in data[key] and score_key in data[key]:
                    total_count = self.season_ntx_dict["ntx_count"]
                    total_score = self.season_ntx_dict["ntx_score"]

                    # Percentage of Global Count
                    data[key]["pct_of_season_ntx_count"] = round(safe_div(data[key][count_key], total_count) * 100, 6)

                    # Round the score
                    data[key][score_key] = round(data[key][score_key], 8)

                    # Percentage of Global Score
                    data[key]["pct_of_season_ntx_score"] = round(safe_div(data[key][score_key], total_score) * 100, 6)
                else:
                    logger.warning(f"Invalid item/key combination!")
                    logger.warning(f"key: {key}")
                    logger.warning(f"count_key: {count_key}")
                    logger.warning(f"score_key: {score_key}")
            else:
                logger.warning(f"Key [{key}] not in data!")
                logger.warning(f"Keys: {data.keys()}")
                logger.warning(f"Keys: {data[key].keys()}")

        calculate_and_assign_percentage(self.season_ntx_dict, "coins", "ntx_count", "ntx_score")
        calculate_and_assign_percentage(self.season_ntx_dict, "notaries", "ntx_count", "ntx_score")
        calculate_and_assign_percentage(self.season_ntx_dict, "servers", "ntx_count", "ntx_score")
        # Notary Percentages
        # notary -> coin | server -> epoch -> coin
        
        notary_data = self.season_ntx_dict["notaries"]
        for notary in self.season_notaries:
            calculate_and_assign_percentage(notary_data, notary, "ntx_count", "ntx_score")

            for coin in self.season_coins:
                calculate_and_assign_percentage(notary_data[notary]["coins"], coin, "ntx_count", "ntx_score")

            server_data = notary_data[notary]["servers"]
            for server in self.season_servers:
                server_coins = helper.get_season_coins(self.season, server)
                if server not in ["Unofficial", "BTC", "None"]:
                    calculate_and_assign_percentage(server_data, server, "ntx_count", "ntx_score")

                    server_coins_data = server_data[server]["coins"]
                    for coin in server_coins:
                        calculate_and_assign_percentage(server_coins_data, coin, "ntx_count", "ntx_score")

                    epoch_data = server_data[server]["epochs"]
                    server_epochs = list(set(get_season_server_epochs(self.season, server)).difference({"Unofficial", "None"}))
                    for epoch in server_epochs:
                        calculate_and_assign_percentage(epoch_data, epoch, "ntx_count", "ntx_score")

                        server_epoch_coins = helper.get_season_coins(self.season, server, epoch) 
                        for coin in server_epoch_coins:
                            calculate_and_assign_percentage(epoch_data[epoch]["coins"], coin, "ntx_count", "ntx_score")

        # Server Percentages
        server_data = self.season_ntx_dict["servers"]
        for server in self.season_servers:
            if server not in ["Unofficial", "BTC", "None"]:
                calculate_and_assign_percentage(server_data, server, "ntx_count", "ntx_score")
                
                coin_data = server_data[server]["coins"]
                server_coins = helper.get_season_coins(self.season, server)
                for coin in server_coins:
                    calculate_and_assign_percentage(coin_data, coin, "ntx_count", "ntx_score")
                    
                    notary_data = coin_data[coin]["notaries"]
                    for notary in self.season_notaries:
                        calculate_and_assign_percentage(notary_data, notary, "ntx_count", "ntx_score")

                epoch_data = server_data[server]["epochs"]
                server_epochs = list(set(get_season_server_epochs(self.season, server)).difference({"Unofficial", "None"}))
                for epoch in server_epochs:
                    calculate_and_assign_percentage(epoch_data, epoch, "ntx_count", "ntx_score")

                    for notary in self.season_notaries:
                        notary_data = epoch_data[epoch]["notaries"]
                        calculate_and_assign_percentage(notary_data, notary, "ntx_count", "ntx_score")
                        
                        epoch_coin_data = epoch_data[epoch]["coins"]
                        server_epoch_coins = helper.get_season_coins(self.season, server, epoch) 
                        for coin in server_epoch_coins:
                            calculate_and_assign_percentage(epoch_coin_data, coin, "ntx_count", "ntx_score")

        # Coin Percentages
        coin_data = self.season_ntx_dict["coins"]
        for coin in self.season_coins:
            calculate_and_assign_percentage(coin_data, coin, "ntx_count", "ntx_score")

            notary_data = coin_data[coin]["notaries"]
            for notary in self.season_notaries:
                calculate_and_assign_percentage(notary_data, notary, "ntx_count", "ntx_score")


    def add_coin_percentages(self):
        # Process percentages for coins
        for coin in self.season_coins:
            self._update_coin_percentages(coin)

        # Process percentages for notaries
        for notary in self.season_notaries:
            self._update_notary_percentages(notary)

        # Process percentages for servers
        for server in self.season_servers:
            self._update_server_percentages(server)

    def _update_coin_percentages(self, coin):
        coin_data = self.season_ntx_dict["coins"][coin]
        self.season_ntx_dict["coins"][coin]["notaries"]["pct_of_coin_ntx_count"] = round(
            safe_div(self.season_ntx_dict["coins"][coin]["notaries"]["ntx_count"], coin_data["ntx_count"]) * 100, 6)

        self.season_ntx_dict["coins"][coin]["notaries"]["ntx_score"] = round(self.season_ntx_dict["coins"][coin]["notaries"]["ntx_score"], 8)
        self.season_ntx_dict["coins"][coin]["notaries"]["pct_of_coin_ntx_score"] = round(
            safe_div(self.season_ntx_dict["coins"][coin]["notaries"]["ntx_score"], coin_data["ntx_score"]) * 100, 6)


        for notary in self.season_notaries:
            self._update_notary_coin_percentages(coin, notary)

        for server in self.season_servers:
            if coin in helper.get_season_coins(self.season, server):
                self._update_server_coin_percentages(coin, server)

    def _update_notary_coin_percentages(self, coin, notary):
        coin_data = self.season_ntx_dict["coins"][coin]
      
        notary_data = self.season_ntx_dict["coins"][coin]["notaries"][notary]        

        notary_data["pct_of_coin_ntx_count"] = round(
            safe_div(notary_data["ntx_count"], coin_data["ntx_count"]) * 100, 6)

        notary_data["ntx_score"] = round(notary_data["ntx_score"], 8)
        notary_data["pct_of_coin_ntx_score"] = round(
            safe_div(notary_data["ntx_score"], coin_data["ntx_score"]) * 100, 6)

    def _update_server_coin_percentages(self, coin, server):
        for notary in self.season_notaries:
            self._update_server_notary_percentages(coin, server, notary)

        server_epochs = list(set(get_season_server_epochs(self.season, server)).difference({"Unofficial", "None"}))
        for epoch in server_epochs: 
            self._update_server_epoch_percentages(coin, server, epoch)

    def _update_server_notary_percentages(self, coin, server, notary):
        notary_data = self.season_ntx_dict["coins"][coin]["servers"][server]["notaries"][notary]
        coin_data = self.season_ntx_dict["coins"][coin]

        # Coin Server Notary Percentage of Coins Count
        notary_data["pct_of_coin_ntx_count"] = round(
            safe_div(notary_data["ntx_count"], coin_data["ntx_count"]) * 100, 6)

        # Coin Server Notary Percentage of Coins Score
        notary_data["ntx_score"] = round(notary_data["ntx_score"], 8)
        notary_data["pct_of_coin_ntx_score"] = round(
            safe_div(notary_data["ntx_score"], coin_data["ntx_score"]) * 100, 6)

    def _update_server_epoch_percentages(self, coin, server, epoch):
        for notary in self.season_notaries:
            self._update_server_epoch_notary_percentages(coin, server, epoch, notary)

        epoch_data = self.season_ntx_dict["coins"][coin]["servers"][server]["epochs"][epoch]
        coin_data = self.season_ntx_dict["coins"][coin]

        # Coin Server Epoch Percentage of Coins Count
        epoch_data["pct_of_coin_ntx_count"] = round(
            safe_div(epoch_data["ntx_count"], coin_data["ntx_count"]) * 100, 6)

        # Coin Server Epoch Percentage of Coins Score
        epoch_data["ntx_score"] = round(epoch_data["ntx_score"], 8)
        epoch_data["pct_of_coin_ntx_score"] = round(
            safe_div(epoch_data["ntx_score"], coin_data["ntx_score"]) * 100, 6)

    def _update_server_epoch_notary_percentages(self, coin, server, epoch, notary):
        notary_data = self.season_ntx_dict["servers"][server]["epochs"][epoch]["notaries"][notary]
        coin_data = self.season_ntx_dict["coins"][coin]

        # Server Epoch Notary Percentage of Coins Count
        notary_data["pct_of_coin_ntx_count"] = round(
            safe_div(notary_data["ntx_count"], coin_data["ntx_count"]) * 100, 6)

        # Server Epoch Notary Percentage of Coins Score
        notary_data["ntx_score"] = round(notary_data["ntx_score"], 8)
        notary_data["pct_of_coin_ntx_score"] = round(
            safe_div(notary_data["ntx_score"], coin_data["ntx_score"]) * 100, 6)

    def _update_notary_percentages(self, notary):
        for coin in self.season_coins:
            self._update_notary_coin_percentages_for_notary(notary, coin)

    def _update_notary_coin_percentages_for_notary(self, notary, coin):
        coin_data = self.season_ntx_dict["coins"][coin]
        notary_coin_data = self.season_ntx_dict["notaries"][notary]["coins"][coin]

        # Notary Coin Percentage of Coins Count
        notary_coin_data["pct_of_coin_ntx_count"] = round(
            safe_div(notary_coin_data["ntx_count"], coin_data["ntx_count"]) * 100, 6)

        # Notary Coin Percentage of Coins Score
        notary_coin_data["ntx_score"] = round(notary_coin_data["ntx_score"], 8)
        notary_coin_data["pct_of_coin_ntx_score"] = round(
            safe_div(notary_coin_data["ntx_score"], coin_data["ntx_score"]) * 100, 6)

    def _update_server_percentages(self, server):
        server_coins = helper.get_season_coins(self.season, server)
        for coin in server_coins:
            self._update_server_coin_percentages_for_server(server, coin)

        server_epochs = list(set(get_season_server_epochs(self.season, server)).difference({"Unofficial", "None"}))
        for epoch in server_epochs:
            self._update_server_epoch_percentages_for_server(server, epoch)

    def _update_server_coin_percentages_for_server(self, server, coin):
        coin_data = self.season_ntx_dict["coins"][coin]
        server_coin_data = self.season_ntx_dict["servers"][server]["coins"][coin]

        # Server Coin Percentage of Coins Count
        server_coin_data["pct_of_coin_ntx_count"] = round(
            safe_div(server_coin_data["ntx_count"], coin_data["ntx_count"]) * 100, 6)

        # Server Coin Percentage of Coins Score
        server_coin_data["ntx_score"] = round(server_coin_data["ntx_score"], 8)
        server_coin_data["pct_of_coin_ntx_score"] = round(
            safe_div(server_coin_data["ntx_score"], coin_data["ntx_score"]) * 100, 6)

    def _update_server_epoch_percentages_for_server(self, server, epoch):
        epoch_coins = helper.get_season_coins(self.season, server, epoch)
        for coin in epoch_coins:
            self._update_server_epoch_coin_percentages(server, epoch, coin)

    def _update_server_epoch_coin_percentages(self, server, epoch, coin):
        coin_data = self.season_ntx_dict["coins"][coin]
        server_epoch_coin_data = self.season_ntx_dict["servers"][server]["epochs"][epoch]["coins"][coin]

        # Server Epoch Coin Percentage of Coins Count
        server_epoch_coin_data["pct_of_coin_ntx_count"] = round(
            safe_div(server_epoch_coin_data["ntx_count"], coin_data["ntx_count"]) * 100, 6)

        # Server Epoch Coin Percentage of Coins Score
        server_epoch_coin_data["ntx_score"] = round(server_epoch_coin_data["ntx_score"], 8)
        server_epoch_coin_data["pct_of_coin_ntx_score"] = round(
            safe_div(server_epoch_coin_data["ntx_score"], coin_data["ntx_score"]) * 100, 6)


    def add_notary_percentages(self):
        # Helper method to compute percentages
        def compute_percentage(value, total):
            return round(safe_div(value, total) * 100, 6)

        # Update percentages relative to notary
        for notary in self.season_notaries:
            notary_data = self.season_ntx_dict["notaries"][notary]
            total_notary_count = notary_data["ntx_count"]
            notary_score = round(notary_data["ntx_score"], 8)

            for coin in self.season_coins:
                coin_data = notary_data["coins"][coin]
                coin_data["ntx_score"] = notary_score
                coin_data["pct_of_notary_ntx_count"] = compute_percentage(coin_data["ntx_count"], total_notary_count)
                coin_data["pct_of_notary_ntx_score"] = compute_percentage(coin_data["ntx_score"], notary_score)

            for server in self.season_servers:
                server_data = notary_data["servers"][server]
                server_count = server_data["ntx_count"]
                server_data["ntx_score"] = round(server_data["ntx_score"], 8)

                server_data["pct_of_notary_ntx_count"] = compute_percentage(server_count, total_notary_count)
                server_data["pct_of_notary_ntx_score"] = compute_percentage(server_data["ntx_score"], notary_score)

                server_epochs = list(set(get_season_server_epochs(self.season, server)).difference({"Unofficial", "None"}))
                for epoch in server_epochs:
                    epoch_data = server_data["epochs"][epoch]
                    epoch_count = epoch_data["ntx_count"]
                    epoch_data["ntx_score"] = round(epoch_data["ntx_score"], 8)

                    epoch_data["pct_of_notary_ntx_count"] = compute_percentage(epoch_count, total_notary_count)
                    epoch_data["pct_of_notary_ntx_score"] = compute_percentage(epoch_data["ntx_score"], notary_score)


                    epoch_data["coins"]["pct_of_notary_ntx_count"] = compute_percentage(coin_data["ntx_count"], total_notary_count)
                    epoch_data["coins"]["ntx_score"] = round(coin_data["ntx_score"], 8)
                    epoch_data["coins"]["pct_of_notary_ntx_score"] = compute_percentage(coin_data["ntx_score"], notary_score)
                    epoch_coins = helper.get_season_coins(self.season, server, epoch)
                    for coin in epoch_coins:
                        epoch_data["coins"][coin]["pct_of_notary_ntx_count"] = compute_percentage(epoch_data["coins"][coin]["ntx_count"], total_notary_count)
                        epoch_data["coins"][coin]["ntx_score"] = round(epoch_data["coins"][coin]["ntx_score"], 8)
                        epoch_data["coins"][coin]["pct_of_notary_ntx_score"] = compute_percentage(epoch_data["coins"][coin]["ntx_score"], notary_score)
                            

        for coin in self.season_coins:
            for notary in self.season_notaries:
                notary_coin_data = self.season_ntx_dict["coins"][coin]["notaries"][notary]
                notary_coin_data["pct_of_notary_ntx_count"] = compute_percentage(notary_coin_data["ntx_count"], self.season_ntx_dict["notaries"][notary]["ntx_count"])
                notary_coin_data["ntx_score"] = round(notary_coin_data["ntx_score"], 8)
                notary_coin_data["pct_of_notary_ntx_score"] = compute_percentage(notary_coin_data["ntx_score"], self.season_ntx_dict["notaries"][notary]["ntx_score"])

    def add_server_percentages(self):
        for coin in self.season_coins:
            for server in self.season_servers:
                if coin in helper.get_season_coins(self.season, server):
                    self._calculate_coin_server_percentages(coin, server)

        for notary in self.season_notaries:
            for server in self.season_servers:
                self._calculate_notary_server_percentages(notary, server)

        for server in self.season_servers:
            for notary in self.season_notaries:
                self._calculate_server_notary_percentages(server, notary)

    def _calculate_coin_server_percentages(self, coin, server):
        coin_data = self.season_ntx_dict["coins"][coin]["servers"][server]
        server_ntx_count = self.season_ntx_dict["servers"][server]["ntx_count"]
        coin_data["pct_of_server_ntx_count"] = self._calculate_percentage(coin_data["ntx_count"], server_ntx_count)
        coin_data["ntx_score"] = round(coin_data["ntx_score"], 8)
        coin_data["pct_of_server_ntx_score"] = self._calculate_percentage(coin_data["ntx_score"], self.season_ntx_dict["servers"][server]["ntx_score"])

        for notary in self.season_notaries:
            self._calculate_notary_percentages(coin_data, notary, server_ntx_count)

        server_epochs = list(set(get_season_server_epochs(self.season, server)).difference({"Unofficial", "None"}))
        for epoch in server_epochs:
            self._calculate_epoch_percentages(coin_data["epochs"][epoch], server_ntx_count, notary)

    def _calculate_notary_percentages(self, coin_data, notary, server_ntx_count):
        notary_data = coin_data["notaries"][notary]
        notary_data["pct_of_server_ntx_count"] = self._calculate_percentage(notary_data["ntx_count"], server_ntx_count)
        notary_data["ntx_score"] = round(notary_data["ntx_score"], 8)
        notary_data["pct_of_server_ntx_score"] = self._calculate_percentage(notary_data["ntx_score"], self.season_ntx_dict["servers"][server]["ntx_score"])

    def _calculate_epoch_percentages(self, epoch_data, server_ntx_count, notary):
        epoch_data["pct_of_server_ntx_count"] = self._calculate_percentage(epoch_data["ntx_count"], server_ntx_count)
        epoch_data["ntx_score"] = round(epoch_data["ntx_score"], 8)
        epoch_data["pct_of_server_ntx_score"] = self._calculate_percentage(epoch_data["ntx_score"], self.season_ntx_dict["servers"][server]["ntx_score"])

        for notary in self.season_notaries:
            notary_data = epoch_data["notaries"][notary]
            notary_data["pct_of_server_ntx_count"] = self._calculate_percentage(notary_data["ntx_count"], server_ntx_count)
            notary_data["ntx_score"] = round(notary_data["ntx_score"], 8)
            notary_data["pct_of_server_ntx_score"] = self._calculate_percentage(notary_data["ntx_score"], self.season_ntx_dict["servers"][server]["ntx_score"])

    def _calculate_notary_server_percentages(self, notary, server):
        notary_server_data = self.season_ntx_dict["notaries"][notary]["servers"][server]
        server_ntx_count = self.season_ntx_dict["servers"][server]["ntx_count"]
        notary_server_data["pct_of_server_ntx_count"] = self._calculate_percentage(notary_server_data["ntx_count"], server_ntx_count)
        notary_server_data["ntx_score"] = round(notary_server_data["ntx_score"], 8)
        notary_server_data["pct_of_server_ntx_score"] = self._calculate_percentage(notary_server_data["ntx_score"], self.season_ntx_dict["servers"][server]["ntx_score"])

        for coin in helper.get_season_coins(self.season, server):
            coin_data = notary_server_data["coins"][coin]
            coin_data["pct_of_server_ntx_count"] = self._calculate_percentage(coin_data["ntx_count"], server_ntx_count)
            coin_data["ntx_score"] = round(coin_data["ntx_score"], 8)
            coin_data["pct_of_server_ntx_score"] = self._calculate_percentage(coin_data["ntx_score"], self.season_ntx_dict["servers"][server]["ntx_score"])

        server_epochs = list(set(get_season_server_epochs(self.season, server)).difference({"Unofficial", "None"}))
        for epoch in server_epochs:
            notary_server_data["epochs"][epoch]["pct_of_server_ntx_count"] = self._calculate_percentage(notary_server_data["epochs"][epoch]["ntx_count"], server_ntx_count)
            notary_server_data["epochs"][epoch]["ntx_score"] = round(notary_server_data["epochs"][epoch]["ntx_score"], 8)
            notary_server_data["epochs"][epoch]["pct_of_server_ntx_score"] = self._calculate_percentage(notary_server_data["epochs"][epoch]["ntx_score"], self.season_ntx_dict["servers"][server]["ntx_score"])

    def _calculate_server_notary_percentages(self, server, notary):
        notary_data = self.season_ntx_dict["servers"][server]["notaries"][notary]
        server_ntx_count = self.season_ntx_dict["servers"][server]["ntx_count"]
        notary_data["pct_of_server_ntx_count"] = self._calculate_percentage(notary_data["ntx_count"], server_ntx_count)
        notary_data["ntx_score"] = round(notary_data["ntx_score"], 8)
        notary_data["pct_of_server_ntx_score"] = self._calculate_percentage(notary_data["ntx_score"], self.season_ntx_dict["servers"][server]["ntx_score"])

        server_coins = helper.get_season_coins(self.season, server)
        for coin in server_coins:
            coin_data = notary_data["coins"][coin]
            coin_data["pct_of_server_ntx_count"] = self._calculate_percentage(coin_data["ntx_count"], server_ntx_count)
            coin_data["ntx_score"] = round(coin_data["ntx_score"], 8)
            coin_data["pct_of_server_ntx_score"] = self._calculate_percentage(coin_data["ntx_score"], self.season_ntx_dict["servers"][server]["ntx_score"])

        server_epochs = list(set(get_season_server_epochs(self.season, server)).difference({"Unofficial", "None"}))
        for epoch in server_epochs:
            notary_data["epochs"][epoch]["pct_of_server_ntx_count"] = self._calculate_percentage(notary_data["epochs"][epoch]["ntx_count"], server_ntx_count)
            notary_data["epochs"][epoch]["ntx_score"] = round(notary_data["epochs"][epoch]["ntx_score"], 8)
            notary_data["epochs"][epoch]["pct_of_server_ntx_score"] = self._calculate_percentage(notary_data["epochs"][epoch]["ntx_score"], self.season_ntx_dict["servers"][server]["ntx_score"])


    def _calculate_percentage(self, value, total):
        return round(safe_div(value, total) * 100, 6) if total else 0.0

    def build_season_ntx_dict(self):
        logger.info(f"Building season ntx dict for {self.season}")
        self.prepopulate()
        self.add_scores_counts()
        self.add_global_percentages()
        self.add_coin_percentages()
        self.add_notary_percentages()
        self.add_server_percentages()
        with open("season_ntx_dict.json", "w+") as f:
            json.dump(self.season_ntx_dict, f, indent=4)
        return self.season_ntx_dict


    def clean_up(self):
        CoinNtxSeasonRow().delete(self.season)
        NotaryNtxSeasonRow().delete(self.season)
        ServerNtxSeasonRow().delete(self.season)


def import_nn_txids(season, coin_type):
    coin_import_functions = {
        "BTC": import_nn_btc_txids,
        "LTC": import_nn_ltc_txids
    }

    if coin_type in coin_import_functions:
        addresses = NOTARY_BTC_ADDRESSES.get(season, []) if coin_type == "BTC" else NOTARY_LTC_ADDRESSES.get(season, [])
        coin_import_functions[coin_type](season, addresses)
    else:
        logger.warning(f"Unsupported coin type: {coin_type}")


def import_nn_txids_generic(season, addresses, coin):
    if not addresses:
        logger.warning(f"{season} not in NOTARY_{coin}_ADDRESSES")
        return

    num_addr = len(addresses)
    
    for i, notary_address in enumerate(addresses, start=1):
        logger.info(f">>> Categorising {notary_address} for {season} {i}/{num_addr}")
        txid_list = get_new_master_server_txids(coin, notary_address, season)
        logger.info(f"Processing ETA: {0.02 * len(txid_list)} sec")
        process_txids(txid_list, coin)


def import_nn_btc_txids(season, addresses):
    import_nn_txids_generic(season, addresses, "BTC")


def import_nn_ltc_txids(season, addresses):
    import_nn_txids_generic(season, addresses, "LTC")


def process_txids(txid_list, coin_type):
    total_txids = len(txid_list)
    for j, txid in enumerate(txid_list, start=1):
        logger.info(f">>> Categorising {txid} for {j}/{total_txids}")
        txid_url = get_txid_url(txid, coin_type)
        time.sleep(0.02)  # Rate limiting
        
        try:
            r = requests.get(txid_url)
            r.raise_for_status()  # Raise an error for bad responses
            resp = r.json()
            tx_resp = resp.get("results", [])
            for row in tx_resp:
                txid_data = create_txid_row(row, txid)
                txid_data.update()
        except requests.RequestException as e:
            logger.error(f"Request error for {txid_url}: {e}")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")


def get_txid_url(txid, coin_type):
    url_builders = {
        "BTC": urls.get_notary_btc_txid_url,
        "LTC": lambda txid: f"{OTHER_SERVER}/api/info/notary_ltc_txid/?txid={txid}"
    }

    if coin_type in url_builders:
        return url_builders[coin_type](txid)
    else:
        raise ValueError(f"Unsupported coin type: {coin_type}")


def create_txid_row(row, txid):
    txid_data = tx_row() if row['coin'] == 'BTC' else ltc_tx_row()
    data_mapping = {
        'txid': txid,
        'block_hash': row["block_hash"],
        'block_height': row["block_height"],
        'block_time': row["block_time"],
        'block_datetime': row["block_datetime"],
        'address': row["address"],
        'notary': row["notary"],
        'category': row["category"],
        'season': row["season"],
        'input_index': row["input_index"],
        'input_sats': row["input_sats"],
        'output_index': row["output_index"],
        'output_sats': row["output_sats"],
        'fees': row["fees"],
        'num_inputs': row["num_inputs"],
        'num_outputs': row["num_outputs"],
    }
    for key, value in data_mapping.items():
        setattr(txid_data, key, value)

    return txid_data

 
def process_tx_list(tx_list, new_txids, existing_txids):
    new_txids_set = set(new_txids)  # Convert to set for faster lookup

    for tx in tx_list:
        tx_hash = tx['tx_hash']
        if tx_hash not in new_txids_set and tx_hash not in existing_txids:
            new_txids_set.add(tx_hash)  # Add to set for efficiency
            logger.info(f"Appended tx {tx_hash} to new_txids")

    new_txids.clear()  # Clear the original list
    new_txids.extend(new_txids_set)  # Update with new unique txids


def get_new_master_server_txids(coin, notary_address, season):
    existing_txids = query.get_existing_nn_txids(coin, notary_address, season=season) 
    url = f"{OTHER_SERVER}/api/info/{coin.lower()}_txid_list/?notary={notary_address}&season={season}"
    logger.info(f"{len(existing_txids)} existing txids in local DB detected for {notary_address} {season}")

    try:
        r = requests.get(url)
        r.raise_for_status()
        resp = r.json()
        txids = resp.get('results', [])
        
        # set comprehension to filter new TXIDs
        new_txids = {txid for txid in txids if txid not in existing_txids}

        logger.info(f"{len(new_txids)} extra txids detected for {coin} notary_address {notary_address} {season}")
        return list(new_txids)
    except requests.RequestException as e:
        logger.error(f"Request error for {url}: {e}")
        return []
    except ValueError as e:
        logger.error(f"Error parsing JSON response: {e}")
        return []


def get_extra_ntx_data(coin, scriptPubKey_asm):
    if coin == "KMD":
        return crypto.lil_endian(scriptPubKey_asm[72:136])
    elif coin not in noMoM:
        try:
            start = 72 + len(coin) * 2 + 4
            end = start + 64
            MoM_hash = crypto.lil_endian(scriptPubKey_asm[start:end])
            MoM_depth = int(crypto.lil_endian(scriptPubKey_asm[end:]), 16)
            return MoM_hash, MoM_depth
        except IndexError as e:
            logger.debug(f"Index error: {e}")
        except ValueError as e:
            logger.debug(f"Value error: {e}")
    return None


def get_new_nn_txids(existing_txids, notary_address, coin, page_break=None, stop_block=None):
    page = 1
    before_block = None
    new_txids = []

    while page <= API_PAGE_BREAK:
        logger.info(f"Getting TXIDs from API Page {page}...")
        resp = api.get_ltc_address_txids(notary_address, before_block) if coin == "LTC" else api.get_btc_address_txids(notary_address, before_block)

        if "error" in resp:
            logger.error(f"Error in response: {resp}")
            api.api_sleep_or_exit(resp, exit=True)
            break

        page += 1
        tx_list = resp.get('txrefs', [])

        if not tx_list:
            logger.info("No more transactions for address!")
            break

        before_block = tx_list[-1]['block_height']
        process_tx_list(tx_list, new_txids, existing_txids)

        if None not in [before_block, stop_block]:
            if before_block < stop_block:
                logger.info("Reached stop block height.")
                break

    logger.info(f"{len(set(new_txids))} DISTINCT TXIDs counted from API")
    return new_txids


def get_new_nn_ltc_txids(existing_txids, notary_address):
    return get_new_nn_txids(existing_txids, notary_address, "LTC")


def get_new_nn_btc_txids(existing_txids, notary_address, page_break=None, stop_block=None):
    stop_block = stop_block or 634774
    page_break = page_break or API_PAGE_BREAK
    return get_new_nn_txids(existing_txids, notary_address, "BTC", page_break, stop_block)
