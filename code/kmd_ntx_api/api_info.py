#!/usr/bin/env python3
from django.http import JsonResponse
from kmd_ntx_api.lib_const import *
import kmd_ntx_api.lib_info as info


def api_index(request):
    resp = info.get_api_index(request)
    filters = ['category', 'sidebar']


    return JsonResponse({
        "count":len(resp),
        "filters":filters,
        "results":resp
    })

def pages_index(request):
    resp = info.get_pages_index(request)
    filters = ['category', 'sidebar']


    return JsonResponse({
        "count":len(resp),
        "filters":filters,
        "results":resp
    })


def base_58_coin_params(request):
    resp = info.get_base_58_coin_params(request)
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
    resp = info.get_balances(request)
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
    resp = info.get_btc_txid_list(request)
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
    resp = info.get_coins(request)
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
    resp = info.get_daemon_cli(request)
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
    resp = info.get_dpow_server_coins_info(request)
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
    resp = info.get_explorers(request)
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


def coin_icons(request):
    resp = info.get_icons(request)
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
    resp = info.get_electrums(request)
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
    resp = info.get_electrums_ssl(request)
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
    resp = info.get_launch_params(request)
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
    resp = info.get_ltc_txid_list(request)
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
    resp = info.get_nn_social_info(request)
    filters = ['season', 'notary']
    return JsonResponse({
        "count":len(resp),
        "filters":filters,
        "results":resp
    })


def notary_mined_count_daily(request):
    resp = info.get_notary_mined_count_daily(request)
    filters = ['mined_date']
    return JsonResponse({
        "count":resp["count"],
        "next":resp["next"],
        "previous":resp["previous"],
        "filters":filters,
        "results":resp["results"]
    })


def mined_count_season_by_name(request):
    resp = info.get_mined_count_season_by_name(request)
    filters = ['season']
    return JsonResponse({
        "count": len(resp),
        "filters": filters,
        "results": resp
    })


def notarised_chain_daily_info(request):
    resp = info.get_notarised_chain_daily(request)
    filters = ['notarised_date']
    return JsonResponse({
        "count":resp["count"],
        "next":resp["next"],
        "previous":resp["previous"],
        "filters":filters,
        "results":resp["results"]
    })


def notarised_count_daily_info(request):
    resp = info.get_notarised_count_daily(request)
    filters = ['notarised_date']
    return JsonResponse({
        "count":resp["count"],
        "next":resp["next"],
        "previous":resp["previous"],
        "filters":filters,
        "results":resp["results"]
    })

def notarised_txid(request):
    resp = info.get_notarised_txid(request)
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

def notarised_chains(request):
    resp = info.get_notarised_chains(request)
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


def notarised_servers(request):
    resp = info.get_notarised_servers(request)
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
    resp = info.get_notarisation_txid_list(request)
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
    resp = info.get_notary_btc_transactions(request)
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
    resp = info.get_notary_btc_txid(request)
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
    resp = info.get_notary_ltc_transactions(request)
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
    resp = info.get_notary_ltc_txid(request)
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
    resp = info.get_notary_nodes_info(request)
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

def vote2021_info(request):
    resp = info.get_vote2021_info(request)
    filters = ["candidate", "block", "txid", "max_block",
               "max_blocktime", "max_locktime"]
    if "error" in resp:
        return JsonResponse({
            "error":resp["error"],
            "filters":filters
        })
    return JsonResponse({
        "filters":filters,
        "results":resp
    })


def rewards_by_address(request):
    resp = info.get_rewards_by_address_info(request)
    filters = ["address", "min_value", "min_block", "max_block", "min_blocktime",
               "exclude_coinbase"]
    if "error" in resp:
        return JsonResponse({
            "error":resp["error"],
            "filters":filters
        })
    return JsonResponse({
        "filters":filters,
        "results":resp
    })