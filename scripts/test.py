#!/usr/bin/env python3
from lib_const import SCORING_EPOCHS, NOTARY_PUBKEYS, CURSOR, CONN, SEASONS_INFO
from lib_table_select import get_notarised_chains, get_notarised_seasons, get_notarised_servers, get_tenure_chains, get_epochs
from lib_notary import get_dpow_scoring_window
from models import get_chain_epoch_at, get_chain_epoch_score_at

#all_notarised_seasons = get_notarised_seasons()
#all_notarised_servers = get_notarised_servers()
#all_notarised_chains = get_notarised_chains()


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

get_tenure_chains("Season_4", "Unoffical")
official_start, official_end, scored_list, unscored_list = get_dpow_scoring_window("Season_4", "GLEEC", "Unoffical")
'''