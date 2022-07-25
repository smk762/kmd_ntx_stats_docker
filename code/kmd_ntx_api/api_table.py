#!/usr/bin/env python3
import kmd_ntx_api.lib_table as table
import kmd_ntx_api.lib_helper as helper
import kmd_ntx_api.lib_ntx as ntx
import kmd_ntx_api.lib_atomicdex as dex

# Source Data Tables
def addresses_table_api(request):
    data = table.get_addresses_rows(request)
    return helper.json_resp(data)


def balances_table_api(request):
    data = table.get_balances_rows(request)
    return helper.json_resp(data)


def coin_last_ntx_table_api(request):
    data = table.get_coin_last_ntx_rows(request)
    return helper.json_resp(data)


def coin_ntx_season_table_api(request):
    data = table.get_coin_ntx_season_rows(request)
    return helper.json_resp(data)


def mined_table_api(request):
    data = table.get_mined_rows(request)
    return helper.json_resp(data)


def mined_count_daily_table_api(request):
    data = table.get_mined_count_daily_rows(request)
    return helper.json_resp(data)


def mined_count_season_table_api(request):
    data = table.get_mined_count_season_rows(request)
    return helper.json_resp(data)


def nn_ltc_tx_table_api(request):
    data = table.get_nn_ltc_tx_rows(request)
    return helper.json_resp(data)


def notary_last_ntx_table_api(request):
    data = table.get_notary_last_ntx_rows(request)
    return helper.json_resp(data)


def notarised_coin_daily_table_api(request):
    data = table.get_notarised_coin_daily_rows(request)
    return helper.json_resp(data)

def notarised_count_daily_table_api(request):
    data = table.get_notarised_count_daily_rows(request)
    return helper.json_resp(data)


def notarised_table_api(request):
    data = table.get_notarised_rows(request)
    return helper.json_resp(data)


def notary_ntx_season_table_api(request):
    data = table.get_notary_ntx_season_rows(request)
    return helper.json_resp(data)


def rewards_tx_table_api(request):
    data = table.get_rewards_tx_rows(request)
    return helper.json_resp(data)


def server_ntx_season_table_api(request):
    data = table.get_server_ntx_season_rows(request)
    return helper.json_resp(data)


def scoring_epochs_table_api(request):
    data = table.get_scoring_epochs_rows(request)
    return helper.json_resp(data)


'''
# Contains json data, not intended for source table
# Can be used to source base58 params, contract address tables etc.
def coins_table_api(request):

# Used for coin profile cards, not intended for source table
def coin_social_table_api(request):

# Not intended for source table
def notary_social_table_api(request):
'''

def notary_last_mined_table_api(request):
    resp = table.get_notary_last_mined_table_api(request)
    filters = ['season']
    return helper.json_resp(resp, filters)


def coin_social_table(request):
    resp = table.get_coin_social_table(request)
    filters = ["season", "coin"]
    return helper.json_resp(resp, filters)


def coin_last_ntx_table(request):
    resp = table.get_coin_last_ntx_table(request)
    filters = ["season", "server", "coin"]
    return helper.json_resp(resp, filters)


def notary_profile_summary_table(request):
    resp = table.get_notary_ntx_season_table_data(request)
    filters = ["season", "server", "notary"]
    return helper.json_resp(resp, filters)


def mined_24hrs_table(request):
    resp = table.get_mined_24hrs_table(request)
    filters = ['name', 'address']
    return helper.json_resp(resp, filters)


def mined_count_season_table(request):
    resp = table.get_mined_count_season_table(request)
    filters = ["name", "address", "season"]
    return helper.json_resp(resp, filters)


def notary_ntx_season_table(request):
    resp = table.get_notary_ntx_season_table(request)
    filters = ["season", "notary", "coin"]
    return helper.json_resp(resp, filters)


def coin_ntx_season_table(request):
    resp = table.get_coin_ntx_season_table(request)
    filters = ["season", "coin"]
    return helper.json_resp(resp, filters)


def notarised_tenure_table(request):
    resp = table.get_notarised_tenure_table(request)
    filters = ["season", "server", "coin"]
    return helper.json_resp(resp, filters)


def split_stats_table(request):
    resp = table.get_split_stats_table(request)
    filters = ['season', 'notary']
    return helper.json_resp(resp, filters)


def notary_epoch_scores_table(request):
    filters = ['season', 'notary']
    resp = table.get_notary_epoch_scores_table(request)[0]
    return helper.json_resp(resp, filters)
    

def notarised_table(request):
    resp = table.get_notarised_rows(request)
    filters = ['season', 'server', 'epoch',
               'coin', 'notary', 'address',
               'txid', 'min_blocktime', 'max_blocktime',
              ]
    return helper.json_resp(resp, filters)


## AtomicDEX Related
def coin_activation_table(request):
    resp = table.get_coin_activation_table(request)
    filters = ['platform']
    return helper.json_resp(resp, filters)


def bestorders_table(request):
    resp = table.get_bestorders_table(request)
    filters = ['coin']
    return helper.json_resp(resp, filters)


def dex_stats_table(request):
    stats = dex.get_swaps_gui_stats(request)
    resp = table.get_dex_stats_table(stats)
    filters = ['from_time', 'to_time']
    return helper.json_resp(resp, filters)


def dex_os_stats_table(request):
    stats = dex.get_swaps_gui_stats(request)
    resp = table.get_dex_os_stats_table(stats)
    filters = ['from_time', 'to_time']
    return helper.json_resp(resp, filters)


def dex_ui_stats_table(request):
    stats = dex.get_swaps_gui_stats(request)
    resp = table.get_dex_ui_stats_table(stats)
    filters = ['from_time', 'to_time']
    return helper.json_resp(resp, filters)


def dex_version_stats_table(request):
    stats = dex.get_swaps_gui_stats(request)
    resp = table.get_dex_version_stats_table(stats)
    filters = ['from_time', 'to_time']
    return helper.json_resp(resp, filters)

