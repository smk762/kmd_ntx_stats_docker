#!/usr/bin/env python3
from django.http import JsonResponse
from kmd_ntx_api.lib_const import *
import kmd_ntx_api.lib_testnet as testnet
import kmd_ntx_api.lib_helper as helper
import kmd_ntx_api.lib_query as query


# TODO: Deprecate after testnet ends
def api_testnet_scoreboard(request):
    resp = testnet.get_testnet_scoreboard(request)
    proposals = testnet.get_notary_candidates_info(request)
    tabled = []
    for name in resp:
        candidate_name = testnet.translate_testnet_name(name, proposals.keys())
        proposal = ""
        if candidate_name in proposals:
            proposal = proposals[candidate_name]
        resp[name].update({
            "name": name,
            "proposal": proposal
        })
        tabled.append(resp[name])

    return helper.json_resp(tabled)


def api_testnet_proposals(request):
    proposals = testnet.get_notary_candidates_info(request)
    return helper.json_resp(proposals)


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


def is_election_over_api(request):
    year = helper.get_or_none(request, "year", VOTE_YEAR)
    resp = testnet.is_election_over(year)
    return helper.json_resp(resp)

