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

    proposals = testnet.get_notary_candidates_info(request)

    for region in notary_vote_table:
        for item in notary_vote_table[region]:
            notary = testnet.translate_notary(item["candidate"])
            item.update({
                "proposal": proposals[notary]
            })

    filters = ["candidate", "block", "txid", "max_block",
               "max_blocktime", "max_locktime", "mined_by"]
    return helper.json_resp(resp, filters)


def notary_vote_stats_info(request):
    resp = testnet.get_notary_vote_stats_info(request)

    proposals = testnet.get_notary_candidates_info(request)

    for region in resp:
        for item in resp[region]:
            notary = testnet.translate_notary(item["candidate"])
            item.update({
                "proposal": proposals[notary]
            })
            
    filters = ["year", "candidate", "block", "txid", "max_block",
               "max_blocktime", "max_locktime"]
    return helper.json_resp(resp, filters)


def vote_aggregates_api(request):
    resp = testnet.get_vote_aggregates(request)
    filters = ["candidate", "year"]
    return helper.json_resp(resp, filters)
