#!/usr/bin/env python3
import kmd_ntx_api.lib_table as table
import kmd_ntx_api.lib_helper as helper


def addresses_table(request):
    resp = table.get_addresses_table(request)
    filters = ['season', 'server', 'coin', 'notary', 'address']
    return helper.json_resp(resp, filters)

def balances_table(request):
    resp = table.get_balances_table(request)
    filters = ['season', 'server', 'coin', 'notary', 'address']
    return helper.json_resp(resp, filters)


def last_mined_table(request):
    resp = table.get_last_mined_table(request)
    filters = ["name", "address", "season"]
    return helper.json_resp(resp, filters)

def coin_social_table(request):
    resp = table.get_coin_social_table(request)
    filters = ["season", "coin"]
    return helper.json_resp(resp, filters)


def coin_last_ntx_table(request):
    resp = table.get_coin_last_ntx_table(request)
    filters = ["season", "server", "coin"]
    return helper.json_resp(resp, filters)


def notary_last_ntx_table(request):
    resp = table.get_notary_last_ntx_table(request)
    filters = ["season", "server", "notary", "coin"]
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


def notarised_24hrs_table(request):
    resp = table.get_notarised_24hrs_table(request)
    filters = ['season', 'server', 'epoch', 'coin', 'notary', 'address']
    return helper.json_resp(resp, filters)


def notary_ntx_season_table(request):
    resp = table.get_notary_ntx_season_table(request)
    filters = ["season", "notary", "coin"]
    return helper.json_resp(resp, filters)


def coin_ntx_season_table(request):
    resp = table.get_coin_ntx_season_table(request)
    filters = ["season", "coin"]
    return helper.json_resp(resp, filters)


def notary_ntx_table(request):
    resp = table.get_notary_ntx_table(request)
    filters = ['season', 'server', 'epoch', 'coin', 'notary']
    return helper.json_resp(resp, filters)

def notarised_table(request):
    resp = table.get_notarised_table(request)
    filters = ['season', 'server', 'epoch', 'coin', 'notary', 'address']
    return helper.json_resp(resp, filters)


def notarised_tenure_table(request):
    resp = table.get_notarised_tenure_table(request)
    filters = ["season", "server", "coin"]
    return helper.json_resp(resp, filters)


def scoring_epochs_table(request):
    resp = table.get_scoring_epochs_table(request)
    filters = ['season', 'server', 'epoch', 'coin', 'timestamp']
    return helper.json_resp(resp, filters)


def split_stats_table(request):
    resp = table.get_split_stats_table(request)
    filters = ['season', 'notary']
    return helper.json_resp(resp, filters)



def notary_epoch_scores_table(request):
    filters = ['season', 'notary']
    resp = table.get_notary_epoch_scores_table(request)[0]
    return helper.json_resp(resp, filters)
    

def notary_epoch_coin_notarised_table(request):
    resp = table.get_notarised_table(request)
    if not "error" in resp:
        resp = table.tablize_notarised(resp)
    filters = ['season', 'server', 'epoch', 'coin', 'notary']
    return helper.json_resp(resp, filters)


def notary_coin_notarised_table(request):
    resp = table.get_notarised_table(request)
    if not "error" in resp:
        resp = table.tablize_notarised(resp)
    filters = ['season', 'server', 'epoch', 'coin', 'notary']
    return helper.json_resp(resp, filters)


def coin_notarised_24hrs_table(request):
    resp = table.get_notarised_24hrs_table(request)
    if not "error" in resp:
        resp = table.tablize_notarised(resp)
    filters = ['season', 'server', 'epoch', 'coin', 'notary']
    return helper.json_resp(resp, filters)
