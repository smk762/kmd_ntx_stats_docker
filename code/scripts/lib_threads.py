#!/usr/bin/env python3
import threading
from lib_helper import *
from lib_query import *

from models import *


class update_notary_balances_thread(threading.Thread):
    def __init__(self, season, server, notary, coin, pubkey, address):
        threading.Thread.__init__(self)
        self.season = season
        self.server = server
        self.notary = notary
        self.chain = coin
        self.pubkey = pubkey
        self.address = address

    def run(self):
        update_notary_balances(
            self.season, self.server,
            self.notary, self.chain,
            self.pubkey, self.address
        )


def update_notary_balances(season, server, notary, coin, pubkey, address):
    balance = balance_row()
    balance.season = season
    balance.server = server
    balance.notary = notary
    balance.chain = coin
    balance.pubkey = pubkey
    balance.address = address
    balance.update()



class update_notary_ntx_count_season_thread(threading.Thread):
    def __init__(self, season_ntx_dict, season, notary):
        threading.Thread.__init__(self)
        self.season_ntx_dict = season_ntx_dict
        self.season = season
        self.notary = notary

    def run(self):
        update_notary_ntx_count_season(self.season_ntx_dict, self.season, self.notary)


def update_notary_ntx_count_season(season_ntx_dict, season, notary):
    season_ntx_count_row = notarised_count_season_row()
    season_ntx_count_row.time_stamp = time.time()
    season_ntx_count_row.notary = notary
    season_ntx_count_row.season = season

    if notary in season_ntx_dict["notaries"]:
        season_score = season_ntx_dict["notaries"][notary]["notary_ntx_score"]
        coin_ntx_counts = season_ntx_dict["notaries"][notary]
    else:
        season_score = 0
        coin_ntx_counts = {}

    coin_ntx_pct_dict = {}
    for coin in season_ntx_dict["coins"]:
        coin_ntx_pct_dict.update({
            coin: season_ntx_dict["coins"][coin]["coin_ntx_count_pct"]
        })

    btc_count = 0
    if "KMD" in season_ntx_dict["coins"]:
        btc_count = season_ntx_dict["notaries"][notary]["servers"]["KMD"]["epochs"]["KMD"]["notary_server_epoch_ntx_count"]

    antara_count = 0
    if "Main" in season_ntx_dict["servers"]:
        for epoch in season_ntx_dict["notaries"][notary]["servers"]["Main"]["epochs"]:
            if epoch != "Unofficial":
                antara_count += season_ntx_dict["notaries"][notary]["servers"]["Main"]["epochs"][epoch]["notary_server_epoch_ntx_count"]

    third_party_count = 0
    if "Third_Party" in season_ntx_dict["servers"]:
        for epoch in season_ntx_dict["notaries"][notary]["servers"]["Third_Party"]["epochs"]:
            if epoch != "Unofficial":
                third_party_count += season_ntx_dict["notaries"][notary]["servers"]["Third_Party"]["epochs"][epoch]["notary_server_epoch_ntx_count"]

    other_count = 0
    for server in season_ntx_dict["notaries"][notary]["servers"]:
        for epoch in ["Unofficial","BTC","LTC"]:
            if epoch in season_ntx_dict["notaries"][notary]["servers"][server]["epochs"]:
                other_count += season_ntx_dict["notaries"][notary]["servers"][server]["epochs"][epoch]["notary_server_epoch_ntx_count"]

    season_ntx_count_row.season_score = season_score
    season_ntx_count_row.btc_count = btc_count
    season_ntx_count_row.antara_count = antara_count
    season_ntx_count_row.third_party_count = third_party_count
    season_ntx_count_row.other_count = other_count
    season_ntx_count_row.total_ntx_count = btc_count+antara_count+third_party_count
    season_ntx_count_row.chain_ntx_counts = json.dumps(coin_ntx_counts)
    season_ntx_count_row.chain_ntx_pct = json.dumps(coin_ntx_pct_dict)
    season_ntx_count_row.update()
