#!/usr/bin/env python3
from kmd_ntx_api.table import get_addresses_rows, get_balances_rows, \
    get_coin_last_ntx_rows, get_coin_ntx_season_rows, get_mined_rows, \
    get_mined_count_daily_rows, get_mined_count_season_rows, \
    get_nn_ltc_tx_rows, get_notary_last_ntx_rows, get_notarised_coin_daily_rows, \
    get_notarised_count_daily_rows, get_notarised_rows, get_notary_ntx_season_rows, \
    get_server_ntx_season_rows, get_scoring_epochs_rows, \
    get_kmd_supply_rows, get_notary_last_mined_table_api, get_coin_social_table, \
    get_coin_last_ntx_table, get_notary_ntx_season_table, get_notary_ntx_season_table_data, \
    get_mined_24hrs_table, get_mined_count_season_table, get_coin_ntx_season_table, \
    get_notarised_tenure_table, get_notary_epoch_scores_table, \
    get_coin_activation_table, get_bestorders_table, get_dex_stats_table, \
    get_dex_os_stats_table, get_dex_version_stats_table, get_dex_ui_stats_table
            
from kmd_ntx_api.swaps import get_swaps_gui_stats
from kmd_ntx_api.helper import json_resp

# Source Data Tables
def addresses_table_api(request):
    data = get_addresses_rows(request)
    return json_resp(data)


def balances_table_api(request):
    data = get_balances_rows(request)
    return json_resp(data)


def coin_last_ntx_table_api(request):
    data = get_coin_last_ntx_rows(request)
    return json_resp(data)


def coin_ntx_season_table_api(request):
    data = get_coin_ntx_season_rows(request)
    return json_resp(data)


def mined_table_api(request):
    data = get_mined_rows(request)
    return json_resp(data)


def mined_count_daily_table_api(request):
    data = get_mined_count_daily_rows(request)
    return json_resp(data)


def mined_count_season_table_api(request):
    data = get_mined_count_season_rows(request)
    return json_resp(data)


def nn_ltc_tx_table_api(request):
    data = get_nn_ltc_tx_rows(request)
    return json_resp(data)


def notary_last_ntx_table_api(request):
    data = get_notary_last_ntx_rows(request)
    return json_resp(data)


def notarised_coin_daily_table_api(request):
    data = get_notarised_coin_daily_rows(request)
    return json_resp(data)

def notarised_count_daily_table_api(request):
    data = get_notarised_count_daily_rows(request)
    return json_resp(data)


def notarised_table_api(request):
    data = get_notarised_rows(request)
    return json_resp(data)


def notary_ntx_season_table_api(request):
    data = get_notary_ntx_season_rows(request)
    return json_resp(data)



def server_ntx_season_table_api(request):
    data = get_server_ntx_season_rows(request)
    return json_resp(data)


def scoring_epochs_table_api(request):
    data = get_scoring_epochs_rows(request)
    return json_resp(data)


'''
# Contains json data, not intended for source table
# Can be used to source base58 params, contract address tables etc.
def coins_table_api(request):

# Used for coin profile cards, not intended for source table
def coin_social_table_api(request):

# Not intended for source table
def notary_social_table_api(request):
'''


def kmd_supply_table_api(request):
    data = get_kmd_supply_rows(request)
    return json_resp(data)


def notary_last_mined_table_api(request):
    resp = get_notary_last_mined_table_api(request)
    filters = ['season']
    return json_resp(resp, filters)


def coin_social_table(request):
    resp = get_coin_social_table(request)
    filters = ["season", "coin"]
    return json_resp(resp, filters)


def coin_last_ntx_table(request):
    resp = get_coin_last_ntx_table(request)
    filters = ["season", "server", "coin"]
    return json_resp(resp, filters)


def notary_profile_summary_table(request):
    resp = get_notary_ntx_season_table_data(request)
    filters = ["season", "server", "notary"]
    return json_resp(resp, filters)


def notary_season_ntx_summary_table(request):
    resp = get_notary_ntx_season_table_data(request)['notary_ntx_summary_table']
    table_data = []
    for coin in resp[0]:
        table_data.append(resp[0][coin])
    filters = ["season", "server", "notary"]
    return json_resp(table_data, filters)


def mined_24hrs_table(request):
    resp = get_mined_24hrs_table(request)
    filters = ['name', 'address']
    return json_resp(resp, filters)


def mined_count_season_table(request):
    resp = get_mined_count_season_table(request)
    filters = ["name", "address", "season"]
    return json_resp(resp, filters)


def notary_ntx_season_table(request):
    resp = get_notary_ntx_season_table(request)
    filters = ["season", "notary", "coin"]
    return json_resp(resp, filters)


def coin_ntx_season_table(request):
    resp = get_coin_ntx_season_table(request)
    filters = ["season", "coin"]
    return json_resp(resp, filters)


def notarised_tenure_table(request):
    resp = get_notarised_tenure_table(request)
    filters = ["season", "server", "coin"]
    return json_resp(resp, filters)


def notary_epoch_scores_table(request):
    filters = ['season', 'notary']
    resp = get_notary_epoch_scores_table(request)[0]
    return json_resp(resp, filters)
    

def notarised_table(request):
    resp = get_notarised_rows(request)
    filters = ['season', 'server', 'epoch',
               'coin', 'notary', 'address',
               'txid', 'min_blocktime', 'max_blocktime',
              ]
    return json_resp(resp, filters)


## AtomicDEX Related
def coin_activation_table(request):
    resp = get_coin_activation_table(request)
    filters = ['platform']
    return json_resp(resp, filters)


def bestorders_table(request):
    resp = get_bestorders_table(request)
    filters = ['coin']
    return json_resp(resp, filters)


def dex_stats_table(request):
    stats = get_swaps_gui_stats(request)
    resp = get_dex_stats_table(stats)
    filters = ['from_time', 'to_time']
    return json_resp(resp, filters)


def dex_os_stats_table(request):
    stats = get_swaps_gui_stats(request)
    resp = get_dex_os_stats_table(stats)
    filters = ['from_time', 'to_time']
    return json_resp(resp, filters)


def dex_ui_stats_table(request):
    stats = get_swaps_gui_stats(request)
    resp = get_dex_ui_stats_table(stats)
    filters = ['from_time', 'to_time']
    return json_resp(resp, filters)


def dex_version_stats_table(request):
    stats = get_swaps_gui_stats(request)
    resp = get_dex_version_stats_table(stats)
    filters = ['from_time', 'to_time']
    return json_resp(resp, filters)

