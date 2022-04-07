#!/usr/bin/env python3
import json
from decorators import print_runtime
import lib_coins
import lib_const
import lib_github
import lib_electrum
import lib_epochs
import lib_ntx
import lib_validate
import lib_dpow_const
import lib_query


print(json.dumps(lib_dpow_const.SEASONS_INFO["Season_5"], indent=4))#

'''
data = lib_validate.get_server_active_scoring_dpow_coins_at_time("Season_5", "Main", 1623683800)
print(data[0])
print(data[1])

#print(json.dumps(lib_dpow_const.SCORING_EPOCHS_REPO_DATA["Season_5"], indent=4))
#print(json.dumps(lib_coins.get_dpow_tenure({})["CLC"], indent=4))
servers = lib_query.get_notarised_servers("Season_5")
epochs = lib_query.get_notarised_epochs("Season_5")
coins = lib_query.get_notarised_coins("Season_5")
servers, epochs, coins = lib_query.get_notarised_servers_epochs_coins("Season_5")
season_ntx_dict = lib_ntx.get_season_ntx_dict("Season_5")
'''


'''
print(lib_query.get_notarised_server_epochs("Season_5"))
print(lib_query.get_notarised_server_epochs("Season_5", "Main"))

print(lib_epochs.get_server_epochs("Season_5"))
print(lib_epochs.get_server_epoch_coins("Season_5", lib_epochs.get_server_epochs("Season_5")))

print(lib_query.get_notarised_server_epoch_coins("Season_5"))
print(lib_query.get_notarised_server_epoch_coins("Season_5", "Main"))
print(lib_query.get_notarised_server_epoch_coins("Season_5", "Main", "Epoch_0"))
'''