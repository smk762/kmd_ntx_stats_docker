#!/usr/bin/env python3
from django.db.models import Sum, Max, Count
from datetime import datetime, timezone

# S7 refactoring
from kmd_ntx_api.seednodes import get_seednode_version_score_total
from kmd_ntx_api.vote import VOTE_YEAR, get_candidates_proposals, translate_proposal_name_to_candidate
from kmd_ntx_api.notary_seasons import get_seasons_info
from kmd_ntx_api.helper import get_or_none, get_notary_list, create_dict, add_numeric_dict_nest, add_string_dict_nest, add_string_dict_nest
from kmd_ntx_api.query import get_notarised_data
from kmd_ntx_api.info import get_coin_addresses
from kmd_ntx_api.ntx import get_notarised_date
from kmd_ntx_api.logger import logger


TESTNET = False

TESTNET_NAV = {
    "Notarisation": {
        "icon": "",
        "options": {
            "Vote Results": {
                "icon": "",
                "url": "/notary_vote"
            },
            "Testnet Leaderboard": {
                "icon": "",
                "url": "/testnet_ntx_scoreboard"
            },
            "Testnet Seednodes": {
                "icon": "",
                "url": "/seednode_version"
            }
        }
    }
}


def get_testnet_scoreboard(request):
    year = get_or_none(request, "year", VOTE_YEAR)
    seasons_info = get_seasons_info()
    season = f"{year}_Testnet"
    notary_list = get_notary_list(season)

    # Prepare ntx data
    ntx_data = get_notarised_data(season).order_by(
        'coin', '-block_height').values()

    # Prepare 24hr ntx data
    ntx_data_24hr = get_notarised_date(
        season).order_by('coin', '-block_height').values()

    testnet_coins = ["DOC", "MARTY"]
    testnet_stats_dict = get_testnet_stats_dict(season, testnet_coins)

    seednode_scores = get_seednode_version_score_total(request, "VOTE2022_Testnet", 1653091199, 1653436800)
    for notary in seednode_scores:
        testnet_stats_dict[notary].update({"seednode_score": seednode_scores[notary]})

    seednode_scores_24hr = get_seednode_version_score_total(request, "VOTE2022_Testnet")
    for notary in seednode_scores_24hr:
        testnet_stats_dict[notary].update({"24hr_seednode_score": seednode_scores_24hr[notary]})


    ntx_dict = {}
    ntx_dict_24hr = {}

    for item in ntx_data:
        coin = item['coin']
        if coin not in ntx_dict:
            ntx_dict.update({coin: []})
            ntx_dict_24hr.update({coin: []})

        if coin in ["DOC", "MARTY"] and item["block_height"] >= seasons_info[season]["start_block"]:
            ntx_dict[coin].append(item)

        elif coin in ["KMD"] and item["block_height"] >= seasons_info[season]["start_block"]:
            ntx_dict[coin].append(item)

    for item in ntx_data_24hr:
        coin = item['coin']

        if coin in ["DOC", "MARTY"] and item["block_height"] >= seasons_info[season]["start_block"]:
            ntx_dict_24hr[coin].append(item)

        elif coin in ["KMD"] and item["block_height"] >= seasons_info[season]["start_block"]:
            ntx_dict_24hr[coin].append(item)


    for coin in testnet_coins:

        # Get notarisation counts
        for item in ntx_dict[coin]:
            ntx_notaries = item["notaries"]

            for notary in ntx_notaries:
                if notary in testnet_stats_dict:

                    if testnet_stats_dict[notary]["Total"] == 0:
                        testnet_stats_dict[notary].update({"Total": 1})

                    else:
                        count = testnet_stats_dict[notary]["Total"]+1
                        testnet_stats_dict[notary].update({"Total": count})

                    if testnet_stats_dict[notary][coin] == 0:
                        testnet_stats_dict[notary].update({coin: 1})
                        testnet_stats_dict[notary].update({coin: 1})

                    else:
                        count = testnet_stats_dict[notary][coin]+1
                        testnet_stats_dict[notary].update({coin: count})
                else:
                    logger.warning(f"[get_testnet_scoreboard] {notary} not \
                                     found in testnet_stats_dict: {item}")

        # Get notarisation counts 24hr
        for item in ntx_dict_24hr[coin]:
            ntx_notaries = item["notaries"]

            for notary in ntx_notaries:
                if notary in testnet_stats_dict:

                    if testnet_stats_dict[notary]["24hr_Total"] == 0:
                        testnet_stats_dict[notary].update({"24hr_Total": 1})

                    else:
                        count = testnet_stats_dict[notary]["24hr_Total"]+1
                        testnet_stats_dict[notary].update(
                            {"24hr_Total": count})

                    if testnet_stats_dict[notary][coin] == 0:
                        testnet_stats_dict[notary].update({f"24hr_{coin}": 1})
                        testnet_stats_dict[notary].update({f"24hr_{coin}": 1})

                    else:
                        count = testnet_stats_dict[notary][f"24hr_{coin}"]+1
                        testnet_stats_dict[notary].update({f"24hr_{coin}": count})
                else:
                    logger.warning(f"[get_testnet_scoreboard] {notary} not found \
                                     in ntx_notaries: {item}")


    for notary in testnet_stats_dict:
        testnet_stats_dict[notary]["Total"] += seednode_scores[notary]
        testnet_stats_dict[notary]["24hr_Total"] += seednode_scores_24hr[notary]

    notary_totals = {}
    notary_totals_24hr = {}
    for notary in testnet_stats_dict:
        notary_totals.update({notary: testnet_stats_dict[notary]["Total"]})
        notary_totals_24hr.update({notary: testnet_stats_dict[notary]["24hr_Total"]})

    # Get notarisation rank
    ranked_totals = {k: v for k, v in sorted(
        notary_totals.items(), key=lambda x: x[1])}
    ranked_totals = dict(reversed(list(ranked_totals.items())))
    logger.info(ranked_totals)

    i = 0
    for notary in ranked_totals:
        i += 1
        testnet_stats_dict[notary].update({"Rank": i})

    # Get 24hr notarisation rank
    ranked_totals_24hr = {k: v for k, v in sorted(
        notary_totals_24hr.items(), key=lambda x: x[1])}
    ranked_totals_24hr = dict(reversed(list(ranked_totals_24hr.items())))
    logger.info(ranked_totals_24hr)

    i = 0
    for notary in ranked_totals_24hr:
        i += 1
        testnet_stats_dict[notary].update({"24hr_Rank": i})

    return testnet_stats_dict


def get_testnet_addresses(season):
    addresses_dict = {}
    addresses_data = get_coin_addresses('KMD', season)

    for item in addresses_data:
        if item["notary"] not in addresses_dict: 
            addresses_dict.update({item["notary"]:item['address']})
    return addresses_dict


def get_testnet_stats_dict(season, testnet_coins):
    notary_list = get_notary_list(season)
    testnet_stats_dict = create_dict(notary_list)

    addresses_dict = get_testnet_addresses(season)

    testnet_stats_dict = add_numeric_dict_nest(testnet_stats_dict, "Total")
    testnet_stats_dict = add_numeric_dict_nest(testnet_stats_dict, "Rank")
    testnet_stats_dict = add_numeric_dict_nest(testnet_stats_dict, "24hr_Total")
    testnet_stats_dict = add_numeric_dict_nest(testnet_stats_dict, "24hr_Rank")
    testnet_stats_dict = add_string_dict_nest(testnet_stats_dict, "Address")

    for coin in testnet_coins:
        testnet_stats_dict = add_numeric_dict_nest(testnet_stats_dict, coin)
        testnet_stats_dict = add_numeric_dict_nest(testnet_stats_dict, f"24hr_{coin}")
        testnet_stats_dict = add_numeric_dict_nest(testnet_stats_dict, f"Last_{coin}")

    for notary in testnet_stats_dict:
        if notary in addresses_dict:
            address = addresses_dict[notary]
            testnet_stats_dict[notary].update({"Address": address})
        else:
            logger.warning(f"[get_testnet_stats_dict] {notary} not in addresses_dict")
            logger.warning(f"[addresses_dict] {addresses_dict}")
            logger.warning(f"[notaries] {notary_list}")
    return testnet_stats_dict


def get_testnet_scoreboard_table(request):
    resp = get_testnet_scoreboard(request)
    proposals = get_candidates_proposals(request)
    tabled = []
    for name in resp:
        candidate_name = translate_proposal_name_to_candidate(name, proposals.keys())
        proposal = ""
        if candidate_name in proposals:
            proposal = proposals[candidate_name.lower()]
        resp[name].update({
            "name": name,
            "proposal": proposal
        })
        tabled.append(resp[name])
    return tabled
