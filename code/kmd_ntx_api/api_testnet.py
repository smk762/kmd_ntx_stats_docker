#!/usr/bin/env python3
from django.http import JsonResponse
import kmd_ntx_api.lib_testnet as testnet
import kmd_ntx_api.lib_helper as helper


# TODO: Deprecate after testnet ends
def api_testnet_totals(request):
    resp = testnet.get_api_testnet(request)
    return JsonResponse(resp)


def notary_vote_table(request):
    resp = testnet.get_notary_vote_table(request)
    filters = ["candidate", "block", "txid", "max_block",
               "max_blocktime", "max_locktime", "mined_by"]
    return helper.json_resp(resp, filters)


def notary_vote_stats_info(request):
    resp = testnet.get_notary_vote_stats_info(request)
    filters = ["year", "candidate", "block", "txid", "max_block",
               "max_blocktime", "max_locktime"]
    return helper.json_resp(resp, filters)


def vote_aggregates_api(request):
    resp = testnet.get_vote_aggregates(request)
    filters = ["candidate", "year"]
    return helper.json_resp(resp, filters)
