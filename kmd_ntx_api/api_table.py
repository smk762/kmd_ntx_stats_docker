#!/usr/bin/env python3
import random
from django.http import JsonResponse
from kmd_ntx_api.lib_info import *
from kmd_ntx_api.lib_table import *


def addresses_table(request):
    resp = get_addresses_table(request)
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
    resp = get_balances_table(request)
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
    resp = get_last_mined_table(request)
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
    resp = get_coin_social_table(request)
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
    resp = get_last_notarised_table(request)
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
    resp = get_notary_profile_summary_table(request)
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


def mined_24hrs_table(request):
    resp = get_mined_24hrs_table(request)
    filters = ['name', 'address']
    return JsonResponse({
        "count":len(resp),
        "filters":filters,
        "results":resp
    })


def mined_count_season_table(request):
    resp = get_mined_count_season_table(request)
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
    resp = get_notarised_24hrs_table(request)
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
    resp = get_notarised_chain_season_table(request)
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
    resp = get_notarised_count_season_table(request)
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


def notarised_table(request):
    resp = get_notarised_table(request)
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
    resp = get_notarised_tenure_table(request)
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
    resp = get_scoring_epochs_table(request)
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
    resp = get_split_stats_table(request)
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



# UPDATE PENDING
def notary_epoch_scores_table(request):
    if not "season" in request.GET:
        season = "Season_4"
    else:
        season = request.GET["season"]

    notary_list = get_notary_list(season)
    if not "notary" in request.GET:
        notary = random.choice(notary_list)
    else:
        notary = request.GET["notary"]

    resp = get_notary_epoch_scores_table(notary, season)[0]
    return JsonResponse(resp, safe=False)
    

