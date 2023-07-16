#!/usr/bin/env python3
from django.http import JsonResponse
from kmd_ntx_api.vote import VOTE_YEAR, get_notary_vote_detail_table, get_vote_stats_info, \
    get_vote_aggregates, is_election_over, get_candidates_proposals
from kmd_ntx_api.testnet import get_testnet_scoreboard_table
from kmd_ntx_api.helper import json_resp, get_or_none


# TODO: Deprecate after testnet ends
def api_testnet_scoreboard(request):
    tabled = get_testnet_scoreboard_table(request)
    return json_resp(tabled)


def api_testnet_proposals(request):
    proposals = get_candidates_proposals(request)
    return json_resp(proposals)


def api_notary_vote_detail_table(request):
    table = get_notary_vote_detail_table(request)
    return json_resp(table)


def notary_vote_stats_info(request):
    resp = get_vote_stats_info(request)

    filters = ["year", "candidate", "block", "txid", "max_block",
               "max_blocktime", "max_locktime"]
    return json_resp(resp, filters)


def vote_aggregates_api(request):
    resp = get_vote_aggregates(request)
    filters = ["candidate", "year"]
    return json_resp(resp, filters)


def is_election_over_api(request):
    year = get_or_none(request, "year", VOTE_YEAR)
    resp = is_election_over(year)
    return json_resp(resp)

