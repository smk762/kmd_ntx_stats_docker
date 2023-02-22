#!/usr/bin/env python3
import kmd_ntx_api.lib_info as info
import kmd_ntx_api.lib_query as query
import kmd_ntx_api.lib_helper as helper


def api_index(request):
    resp = info.get_api_index(request)
    filters = ['category', 'sidebar']
    return helper.json_resp(resp, filters)


def pages_index(request):
    resp = info.get_pages_index(request)
    filters = ['category', 'sidebar']
    return helper.json_resp(resp, filters)


def mined_between_blocks(request):
    resp = info.get_mined_between_blocks(request)
    filters = ['min_block', 'max_block']
    print(f"======================================  {resp}")
    return helper.json_resp(resp, filters)


def mined_between_blocktimes(request):
    resp = info.get_mined_between_blocktimes(request)
    filters = ['min_blocktime', 'max_blocktime']
    print(f"======================================  {resp}")
    return helper.json_resp(resp, filters)


def base_58_coin_params(request):
    resp = info.get_base_58_coin_params(request)
    filters = ['coin']
    return helper.json_resp(resp, filters)


def balances_info(request):
    resp = info.get_balances(request)
    filters = ['season', 'server', 'notary', 'coin']
    return helper.json_resp(resp, filters)


def btc_txid_list(request):
    resp = info.get_btc_txid_list(request)
    filters = ['season', 'notary', 'category', 'address']
    return helper.json_resp(resp, filters)


def coins_info(request, coin=None):
    resp = info.get_coins(request, coin)
    filters = ['coin', 'dpow_active', 'mm2_active']
    return helper.json_resp(resp, filters)


def coin_prefixes(request, coin=None):
    resp = info.get_coin_prefixes(request, coin)
    filters = ['coin']
    return helper.json_resp(resp, filters)


def coin_daemon_cli(request):
    resp = info.get_daemon_cli(request)
    filters = ['coin']
    return helper.json_resp(resp, filters)


def dpow_server_coins_info(request):
    resp = info.get_dpow_server_coins_info(request)
    filters = ['season', 'server', 'epoch', 'timestamp']
    return helper.json_resp(resp, filters)


def coin_explorers(request):
    resp = info.get_explorers(request)
    filters = ['coin']
    return helper.json_resp(resp, filters)


def coin_icons_info(request):
    resp = info.get_coin_icons(request)
    filters = ['coin']
    return helper.json_resp(resp, filters)


def coin_electrums(request):
    resp = info.get_electrums(request)
    filters = ['coin']
    return helper.json_resp(resp, filters)


def coin_electrums_ssl(request):
    resp = info.get_electrums_ssl(request)
    filters = ['coin']
    return helper.json_resp(resp, filters)


def coin_launch_params(request):
    resp = info.get_launch_params(request)
    filters = ['coin']
    return helper.json_resp(resp, filters)


def coin_social_info(request):
    resp = info.get_coin_social_info(request)
    filters = ['season', 'coin']
    return helper.json_resp(resp, filters)


def ltc_txid_list(request):
    resp = info.get_ltc_txid_list(request)
    filters = ['season', 'notary', 'category', 'address']
    return helper.json_resp(resp, filters)


def notary_icons_info(request):
    resp = info.get_notary_icons(request)
    filters = ['notary', 'season']
    return helper.json_resp(resp, filters)


def nn_social_info(request):
    resp = info.get_nn_social_info(request)
    filters = ['season', 'notary']
    return helper.json_resp(resp, filters)



def notarised_coin_daily_info(request):
    resp = info.get_notarised_coin_daily(request)
    filters = ['notarised_date']
    return helper.json_resp(resp, filters)


def notarised_count_daily_info(request):
    resp = info.get_notarised_count_daily(request)
    filters = ['notarised_date']
    return helper.json_resp(resp, filters)


def notarised_coins(request):
    resp = info.get_notarised_coins(request)
    filters = ['txid']
    return helper.json_resp(resp, filters)


def notarised_servers(request):
    resp = info.get_notarised_servers(request)
    filters = ['txid']
    return helper.json_resp(resp, filters)


def notarisation_txid_list(request):
    resp = info.get_notarisation_txid_list(request)
    filters = ['season', 'server', 'coin', 'notary']
    return helper.json_resp(resp, filters)


def notary_btc_transactions(request):
    resp = info.get_notary_btc_transactions(request)
    filters = ['season', 'category', 'notary', 'address']
    return helper.json_resp(resp, filters)

    
def notarised_txid(request):
    resp = info.get_notarised_txid(request)
    print(resp)
    filters = ['txid']
    return helper.json_resp(resp, filters)


def notary_btc_txid(request):
    resp = info.get_notary_btc_txid(request)
    filters = ['txid']
    return helper.json_resp(resp, filters)


def notary_ltc_transactions(request):
    resp = info.get_notary_ltc_transactions(request)
    filters = ['season', 'category', 'notary', 'address']
    return helper.json_resp(resp, filters)


def notary_ltc_txid(request):
    resp = info.get_notary_ltc_txid(request)
    filters = ['txid']
    return helper.json_resp(resp, filters)


def notary_nodes_info(request):
    resp = info.get_notary_nodes_info(request)
    filters = ['year']
    return helper.json_resp(resp, filters)
