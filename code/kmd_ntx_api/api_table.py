#!/usr/bin/env python3
import random
from django.http import JsonResponse
from kmd_ntx_api.lib_const import *
import kmd_ntx_api.lib_info as info
import kmd_ntx_api.lib_table as table
import kmd_ntx_api.lib_helper as helper
from django.db.models import Count, Min, Max, Sum


def addresses_table(request):
    resp = table.get_addresses_table(request)
    filters = ['season', 'server', 'chain', 'notary', 'address']
    if "error" in resp:
        return JsonResponse({
            "error":resp["error"],
            "filters":filters
        })
    return JsonResponse({
        "count":len(resp),
        "filters":filters,
        "results":resp
    })

def balances_table(request):
    resp = table.get_balances_table(request)
    filters = ['season', 'server', 'chain', 'notary', 'address']
    if "error" in resp:
        return JsonResponse({
            "error":resp["error"],
            "filters":filters
        })
    return JsonResponse({
        "count":len(resp),
        "filters":filters,
        "results":resp
    })


def last_mined_table(request):
    resp = table.get_last_mined_table(request)
    filters = ["name", "address", "season"]
    if "error" in resp:
        return JsonResponse({
            "error":resp["error"],
            "filters":filters
        })
    return JsonResponse({
        "count":len(resp),
        "filters":filters,
        "results":resp
    })

def coin_social_table(request):
    resp = table.get_coin_social_table(request)
    filters = ["season", "chain"]
    if "error" in resp:
        return JsonResponse({
            "error":resp["error"],
            "filters":filters
        })
    return JsonResponse({
        "count":len(resp),
        "filters":filters,
        "results":resp
    })


def last_notarised_table(request):
    resp = table.get_last_notarised_table(request)
    filters = ["season", "server", "notary", "chain"]
    if "error" in resp:
        return JsonResponse({
            "error":resp["error"],
            "filters":filters
        })
    return JsonResponse({
        "count":len(resp),
        "filters":filters,
        "results":resp
    })

def notary_profile_summary_table(request):
    resp = table.get_notary_profile_summary_table(request)
    filters = ["season", "server", "notary"]
    if "error" in resp:
        return JsonResponse({
            "error":resp["error"],
            "filters":filters
        })
    return JsonResponse({
        "count":len(resp),
        "filters":filters,
        "results":resp
    })


def notary_epoch_chain_notarised_table(request):
    resp = table.get_notarised_table(request)
    filters = ['season', 'server', 'epoch', 'chain', 'notary']
    if "error" in resp:
        return JsonResponse({
            "error":resp["error"],
            "filters":filters
        })
    table_resp = []
    for i in resp:
        table_resp.append({
            "chain": i["chain"],
            "block_height": i["block_height"],
            "ac_ntx_height": i["ac_ntx_height"],
            "txid": i["txid"],
            "notaries": i["notaries"],
            "opret": i["opret"],
            "block_time": i["block_time"]
        })

    return JsonResponse({
        "data": table_resp
    })

def notary_chain_notarised_table(request):
    resp = table.get_notarised_table(request)
    filters = ['season', 'server', 'epoch', 'chain', 'notary']
    if "error" in resp:
        return JsonResponse({
            "error":resp["error"],
            "filters":filters
        })
    table_resp = []
    for i in resp:
        table_resp.append({
            "chain": i["chain"],
            "block_height": i["block_height"],
            "ac_ntx_height": i["ac_ntx_height"],
            "txid": i["txid"],
            "notaries": i["notaries"],
            "opret": i["opret"],
            "block_time": i["block_time"]
        })

    return JsonResponse({
        "data": table_resp
    })


def chain_notarised_24hrs_table(request):
    resp = table.get_notarised_24hrs_table(request)
    filters = ['season', 'server', 'epoch', 'chain', 'notary']
    if "error" in resp:
        return JsonResponse({
            "error":resp["error"],
            "filters":filters
        })
    table_resp = []
    for i in resp:
        table_resp.append({
            "chain": i["chain"],
            "block_height": i["block_height"],
            "ac_ntx_height": i["ac_ntx_height"],
            "txid": i["txid"],
            "notaries": i["notaries"],
            "opret": i["opret"],
            "block_time": i["block_time"]
        })

    return JsonResponse({
        "data": table_resp
    })


def mined_24hrs_table(request):
    resp = table.get_mined_24hrs_table(request)
    filters = ['name', 'address']
    return JsonResponse({
        "count":len(resp),
        "filters":filters,
        "results":resp
    })


def mined_count_season_table(request):
    resp = table.get_mined_count_season_table(request)
    filters = ["name", "address", "season"]
    if "error" in resp:
        return JsonResponse({
            "error":resp["error"],
            "filters":filters
        })
    return JsonResponse({
        "count":len(resp),
        "filters":filters,
        "results":resp
    })


def notarised_24hrs_table(request):
    resp = table.get_notarised_24hrs_table(request)
    filters = ['season', 'server', 'epoch', 'chain', 'notary', 'address']
    if "error" in resp:
        return JsonResponse({
            "error":resp["error"],
            "filters":filters
        })
    return JsonResponse({
        "count":len(resp),
        "filters":filters,
        "results":resp
    })


def notarised_chain_season_table(request):
    resp = table.get_notarised_chain_season_table(request)
    filters = ["season", "server", "chain"]
    if "error" in resp:
        return JsonResponse({
            "error":resp["error"],
            "filters":filters
        })
    return JsonResponse({
        "count":len(resp),
        "filters":filters,
        "results":resp
    })


def notarised_count_season_table(request):
    resp = table.get_notarised_count_season_table(request)
    filters = ["season", "notary"]
    if "error" in resp:
        return JsonResponse({
            "error":resp["error"],
            "filters":filters
        })
    return JsonResponse({
        "count":len(resp),
        "filters":filters,
        "results":resp
    })


def notary_ntx_table(request):
    resp = table.get_notary_ntx_table(request)
    filters = ['season', 'server', 'epoch', 'chain', 'notary']
    if "error" in resp:
        return JsonResponse({
            "error":resp["error"],
            "filters":filters
        })
    return JsonResponse({
        "count":len(resp),
        "filters":filters,
        "results":resp
    })

def notarised_table(request):
    resp = table.get_notarised_table(request)
    filters = ['season', 'server', 'epoch', 'chain', 'notary', 'address']
    if "error" in resp:
        return JsonResponse({
            "error":resp["error"],
            "filters":filters
        })
    return JsonResponse({
        "count":len(resp),
        "filters":filters,
        "results":resp
    })


def notarised_tenure_table(request):
    resp = table.get_notarised_tenure_table(request)
    filters = ["season", "server", "chain"]
    if "error" in resp:
        return JsonResponse({
            "error":resp["error"],
            "filters":filters
        })
    return JsonResponse({
        "count":len(resp),
        "filters":filters,
        "results":resp
    })


def scoring_epochs_table(request):
    resp = table.get_scoring_epochs_table(request)
    filters = ['season', 'server', 'epoch', 'chain', 'timestamp']
    if "error" in resp:
        return JsonResponse({
            "error":resp["error"],
            "filters":filters
        })
    return JsonResponse({
        "count":len(resp),
        "filters":filters,
        "results":resp
    })


def split_stats_table(request):
    resp = info.get_split_stats_table(request)
    filters = ['season', 'notary']
    if "error" in resp:
        return JsonResponse({
            "error":resp["error"],
            "filters":filters
        })
    return JsonResponse({
        "count":len(resp),
        "filters":filters,
        "results":resp
    })


def vote2021_table(request):
    resp = table.get_vote2021_table(request)
    filters = ["candidate", "block", "txid", "max_block",
               "max_blocktime", "max_locktime", "mined_by"]
    if "error" in resp:
        return JsonResponse({
            "error":resp["error"],
            "filters":filters
        })
    return JsonResponse({
        "count":len(resp),
        "filters":filters,
        "results":resp
    })


def notary_epoch_scores_table(request):
    if not "season" in request.GET:
        season = SEASON
    else:
        season = request.GET["season"]

    notary_list = helper.get_notary_list(season)
    if not "notary" in request.GET:
        notary = random.choice(notary_list)
    else:
        notary = request.GET["notary"]

    resp = table.get_notary_epoch_scores_table(notary, season)[0]
    return JsonResponse(resp, safe=False)
    

