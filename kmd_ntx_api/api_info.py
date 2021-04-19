#!/usr/bin/env python3
from django.http import JsonResponse
from kmd_ntx_api.lib_info import *


def api_index(request):
    resp = get_api_index(request)
    filters = ['category', 'sidebar']


    return JsonResponse({
        "count":len(resp),
        "filters":filters,
        "results":resp
    })

def pages_index(request):
    resp = get_pages_index(request)
    filters = ['category', 'sidebar']


    return JsonResponse({
        "count":len(resp),
        "filters":filters,
        "results":resp
    })


def base_58_coin_params(request):
    resp = get_base_58_coin_params(request)
    filters = ['chain']
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


def balances_info(request):
    resp = get_balances(request)
    filters = ['season', 'server', 'notary', 'chain']
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


def btc_txid_list(request):
    resp = get_btc_txid_list(request)
    filters = ['season', 'notary', 'category', 'address']
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


def coins_info(request):
    resp = get_coins(request)
    filters = ['chain', 'dpow_active', 'mm2_active']
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


def coin_daemon_cli(request):
    resp = get_daemon_cli(request)
    filters = ['chain']
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


def dpow_server_coins_info(request):
    resp = get_dpow_server_coins_info(request)
    filters = ['season', 'server', 'epoch', 'timestamp']
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


def coin_explorers(request):
    resp = get_explorers(request)
    filters = ['chain']
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


def coin_electrums(request):
    resp = get_electrums(request)
    filters = ['chain']
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


def coin_electrums_ssl(request):
    resp = get_electrums_ssl(request)
    filters = ['chain']
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


def coin_launch_params(request):
    resp = get_launch_params(request)
    filters = ['chain']
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


def ltc_txid_list(request):
    resp = get_ltc_txid_list(request)
    filters = ['season', 'notary', 'category', 'address']
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


def nn_social_info(request):
    resp = get_nn_social_info(request)
    filters = ['season', 'notary']
    return JsonResponse({
        "count":len(resp),
        "filters":filters,
        "results":resp
    })


def notary_mined_count_daily(request):
    resp = get_notary_mined_count_daily(request)
    filters = ['mined_date']
    return JsonResponse({
        "count":resp["count"],
        "next":resp["next"],
        "previous":resp["previous"],
        "filters":filters,
        "results":resp["results"]
    })


def notarised_chain_daily_info(request):
    resp = get_notarised_chain_daily(request)
    filters = ['notarised_date']
    return JsonResponse({
        "count":resp["count"],
        "next":resp["next"],
        "previous":resp["previous"],
        "filters":filters,
        "results":resp["results"]
    })


def notarised_count_daily_info(request):
    resp = get_notarised_count_daily(request)
    filters = ['notarised_date']
    return JsonResponse({
        "count":resp["count"],
        "next":resp["next"],
        "previous":resp["previous"],
        "filters":filters,
        "results":resp["results"]
    })

def notarised_txid(request):
    resp = get_notarised_txid(request)
    filters = ['txid']
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


def notarisation_txid_list(request):
    resp = get_notarisation_txid_list(request)
    filters = ['season', 'server', 'chain', 'notary']
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


def notary_btc_transactions(request):
    resp = get_notary_btc_transactions(request)
    filters = ['season', 'category', 'notary', 'address']
    if "error" in resp:
        return JsonResponse({
            "error":resp["error"],
            "filters":filters
        })
    return JsonResponse({
        "count":resp["count"],
        "filters":filters,
        "results":resp["results"]
    })

    
def notary_btc_txid(request):
    resp = get_notary_btc_txid(request)
    filters = ['txid']
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


def notary_ltc_transactions(request):
    resp = get_notary_ltc_transactions(request)
    filters = ['season', 'category', 'notary', 'address']
    if "error" in resp:
        return JsonResponse({
            "error":resp["error"],
            "filters":filters
        })
    return JsonResponse({
        "count":resp["count"],
        "filters":filters,
        "results":resp["results"]
    })


def notary_ltc_txid(request):
    resp = get_notary_ltc_txid(request)
    filters = ['txid']
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


def notary_nodes_info(request):
    resp = get_notary_nodes_info(request)
    filters = ['season']
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