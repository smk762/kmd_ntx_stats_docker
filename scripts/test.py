#!/usr/bin/env python3
import sys
from lib_const import SCORING_EPOCHS, NOTARY_PUBKEYS, CURSOR, CONN, SEASONS_INFO
from lib_table_select import *
from lib_table_update import *
from lib_notary import *
from models import get_chain_epoch_at, get_chain_epoch_score_at

import logging
import logging.handlers

logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s', datefmt='%d-%b-%y %H:%M:%S')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)


all_notarised_seasons = get_notarised_seasons()
all_notarised_servers = get_notarised_servers()
all_notarised_epochs = get_notarised_epochs()
#all_notarised_chains = get_notarised_chains()
'''
print(get_all_coins())
print(all_notarised_chains)
print(all_notarised_servers)
print(all_notarised_epochs)
print(all_notarised_chains)
'''
for season in all_notarised_seasons:
    notarised_servers = get_notarised_servers(season)
    logger.info(f"{season} notarised_servers: {notarised_servers}")
    for server in notarised_servers:
        notarised_epochs = get_notarised_epochs(season, server)
        logger.info(f"{season} {server} notarised_epochs: {notarised_epochs}")
        for epoch in notarised_epochs:
            notarised_chains = get_notarised_chains(season, server, epoch)
            logger.info(f"{season} {server} {epoch} notarised_chains: {notarised_chains}")

epochs = get_epochs()
print(epochs)

epochs = get_epochs("Season_5_Testnet", "Main")
print(epochs)

season = "Season_5_Testnet"
server = "Main"
chain = "LTC"
block_height = 1616445129

epoch = get_chain_epoch_at(season, server, chain, block_height)
print(epoch)
assert epoch == "Epoch_1"

score  = get_chain_epoch_score_at(season, server, chain, block_height)
print(score)
input()


print(f"SCORING_EPOCHS: {SCORING_EPOCHS}")
print()
print(f"SCORING_EPOCHS seasons: {SCORING_EPOCHS.keys()}")
print()
for season in list(SCORING_EPOCHS.keys()):
    print()
    print(f"SCORING_EPOCHS season {season} servers: {SCORING_EPOCHS[season].keys()}")
    for server in list(SCORING_EPOCHS[season].keys()):
        print(f"SCORING_EPOCHS season {season} servers: {SCORING_EPOCHS[season][server]}")
print()


epochs = get_epochs()
print(f"epochs: {epochs}")

for season in SEASONS_INFO:
    print()
    epochs = get_epochs(season)
    print(f"{season}: {epochs}")
input()

epochs = get_epochs("Season_5_Testnet", "Main")
print(epochs)

print(get_chain_epoch_at("Season_5_Testnet", "Main", "MORTY", 1617319854))

print(get_chain_epoch_score_at("Season_5_Testnet", "Main", "MORTY", 1617319854))
'''
get_tenure_chains("Season_4", "Third_Party")

official_start, official_end, scored_list, unscored_list = get_dpow_scoring_window("Season_4", "GLEEC", "Third_Party")

get_tenure_chains("Season_4", "Main")
official_start, official_end, scored_list, unscored_list = get_dpow_scoring_window("Season_4", "GLEEC", "Main")

get_tenure_chains("Season_4", "Unofficial")
official_start, official_end, scored_list, unscored_list = get_dpow_scoring_window("Season_4", "GLEEC", "Unofficial")
'''