#!/usr/bin/env python3
from django.db.models import Sum, Max, Count
from datetime import datetime, timezone
from kmd_ntx_api.lib_const import *
import kmd_ntx_api.lib_ntx as ntx
import kmd_ntx_api.lib_info as info
import kmd_ntx_api.lib_dexstats as dexstats
import kmd_ntx_api.lib_query as query
import kmd_ntx_api.lib_atomicdex as dex
import kmd_ntx_api.lib_helper as helper
import kmd_ntx_api.serializers as serializers

def get_testnet_scoreboard(request):
    year = helper.get_or_none(request, "year", VOTE_YEAR)
    season = f"{year}_Testnet"
    notary_list = helper.get_notary_list(season)

    # Prepare ntx data
    ntx_data = query.get_notarised_data(season).order_by(
        'coin', '-block_height').values()

    # Prepare 24hr ntx data
    ntx_data_24hr = ntx.get_notarised_date(
        season).order_by('coin', '-block_height').values()

    testnet_coins = ["RICK", "MORTY"]
    testnet_stats_dict = get_testnet_stats_dict(season, testnet_coins)
    last_ntx = info.get_last_nn_coin_ntx(season)

    seednode_scores = dex.get_seednode_version_score_total(request, "VOTE2022_Testnet", 1653091199, 1653436800)
    for notary in seednode_scores:
        testnet_stats_dict[notary].update({"seednode_score": seednode_scores[notary]})

    seednode_scores_24hr = dex.get_seednode_version_score_total(request, "VOTE2022_Testnet")
    for notary in seednode_scores_24hr:
        testnet_stats_dict[notary].update({"24hr_seednode_score": seednode_scores_24hr[notary]})


    ntx_dict = {}
    ntx_dict_24hr = {}

    for item in ntx_data:
        coin = item['coin']
        if coin not in ntx_dict:
            ntx_dict.update({coin: []})
            ntx_dict_24hr.update({coin: []})

        if coin in ["RICK", "MORTY"] and item["block_height"] >= SEASONS_INFO[season]["start_block"]:
            ntx_dict[coin].append(item)

        elif coin in ["KMD"] and item["block_height"] >= SEASONS_INFO[season]["start_block"]:
            ntx_dict[coin].append(item)

    for item in ntx_data_24hr:
        coin = item['coin']

        if coin in ["RICK", "MORTY"] and item["block_height"] >= SEASONS_INFO[season]["start_block"]:
            ntx_dict_24hr[coin].append(item)

        elif coin in ["KMD"] and item["block_height"] >= SEASONS_INFO[season]["start_block"]:
            ntx_dict_24hr[coin].append(item)


    for coin in testnet_coins:

        # Get last notarised times
        for notary in testnet_stats_dict:

            try:
                last_coin_ntx = last_ntx[notary][coin]["time_since"]
                last_coin_ntx_time = last_ntx[notary][coin]["block_time"]
                testnet_stats_dict[notary].update({
                    f"Last_{coin}": last_coin_ntx,
                    f"Last_{coin}_time": last_coin_ntx_time
                })

            except Exception as e:
                logger.error(f"[get_testnet_scoreboard] Exception: {e} \
                               | notary: {notary} | coin: {coin}")
                logger.warning(f"[get_testnet_scoreboard] Setting last_ntx for \
                                 {notary} | coin: {coin} to > 24hrs")
                testnet_stats_dict[notary].update({
                    f"Last_{coin}": "> 24hrs",
                    f"Last_{coin}_time": 0
                })

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
    addresses_data = info.get_coin_addresses('KMD', season)

    for item in addresses_data:
        if item["notary"] not in addresses_dict: 
            addresses_dict.update({item["notary"]:item['address']})
    return addresses_dict


def get_testnet_stats_dict(season, testnet_coins):
    notary_list = helper.get_notary_list(season)
    testnet_stats_dict = helper.create_dict(notary_list)

    addresses_dict = get_testnet_addresses(season)

    testnet_stats_dict = helper.add_numeric_dict_nest(testnet_stats_dict, "Total")
    testnet_stats_dict = helper.add_numeric_dict_nest(testnet_stats_dict, "Rank")
    testnet_stats_dict = helper.add_numeric_dict_nest(testnet_stats_dict, "24hr_Total")
    testnet_stats_dict = helper.add_numeric_dict_nest(testnet_stats_dict, "24hr_Rank")
    testnet_stats_dict = helper.add_string_dict_nest(testnet_stats_dict, "Address")

    for coin in testnet_coins:
        testnet_stats_dict = helper.add_numeric_dict_nest(testnet_stats_dict, coin)
        testnet_stats_dict = helper.add_numeric_dict_nest(testnet_stats_dict, f"24hr_{coin}")
        testnet_stats_dict = helper.add_numeric_dict_nest(testnet_stats_dict, f"Last_{coin}")

    for notary in testnet_stats_dict:
        if notary in addresses_dict:
            address = addresses_dict[notary]
            testnet_stats_dict[notary].update({"Address": address})
        else:
            logger.warning(f"[get_testnet_stats_dict] {notary} not in addresses_dict")
            logger.warning(f"[addresses_dict] {addresses_dict}")
            logger.warning(f"[notaries] {notary_list}")
    return testnet_stats_dict


def get_notary_vote_stats_info(request):
    year = helper.get_or_none(request, "year")
    candidate = helper.get_or_none(request, "candidate")
    block = helper.get_or_none(request, "block")
    txid = helper.get_or_none(request, "txid")
    max_block = helper.get_or_none(request, "max_block")
    max_blocktime = helper.get_or_none(request, "max_blocktime")
    max_locktime = helper.get_or_none(request, "max_locktime")
    year = helper.get_or_none(request, "year", VOTE_YEAR)

    data = query.get_notary_vote_data(year, candidate, block, txid, max_block, max_blocktime, max_locktime, None, True)
    data = data.values('candidate', 'candidate_address').annotate(num_votes=Count('votes'), sum_votes=Sum('votes'))
    unverified = query.get_notary_vote_data(year, candidate, block, txid, max_block, max_blocktime, max_locktime, None, False)
    unverified = unverified.values('candidate').annotate(sum_votes=Sum('votes'))

    unverified_resp = {}
    for item in unverified:
        region = item["candidate"].split("_")[-1]
        if region not in unverified_resp:
            unverified_resp.update({region:{}})
        unverified_resp[region].update({
            item["candidate"]: item["sum_votes"]
        })

    resp = {}
    region_scores = {}
    for item in data:
        region = item["candidate"].split("_")[-1]
        if region not in resp:
            resp.update({region:[]})
            region_scores.update({region:[]})

        ghost_votes = 0
        if region in unverified_resp:
            if item["candidate"] in unverified_resp[region]:
                ghost_votes = unverified_resp[region][item["candidate"]]
            

        item.update({
            "unverified": ghost_votes
        })
        resp[region].append(item)
        region_scores[region].append(item["sum_votes"])

    for region in resp:
        region_scores[region].sort()
        region_scores[region].reverse()
        for item in resp[region]:
            rank = region_scores[region].index(item["sum_votes"]) + 1
            item.update({"region_rank": rank})

    for region in resp:
        resp[region] = sorted(resp[region], key = lambda item: item['region_rank'])

    return resp


def get_notary_vote_table(request):
    candidate = helper.get_or_none(request, "candidate")
    block = helper.get_or_none(request, "block")
    txid = helper.get_or_none(request, "txid")
    mined_by = helper.get_or_none(request, "mined_by")
    max_block = helper.get_or_none(request, "max_block")
    max_blocktime = helper.get_or_none(request, "max_blocktime")
    max_locktime = helper.get_or_none(request, "max_locktime")
    year = helper.get_or_none(request, "year", VOTE_YEAR)


    data = query.get_notary_vote_data(year, candidate, block, txid, max_block, max_blocktime, max_locktime, mined_by)

    if "order_by" in request.GET:
        order_by = request.GET["order_by"]
        data = data.order_by(f'-{order_by}').values()
    else:
        data = data.order_by(f'-block_time').values()

    serializer = serializers.notaryVoteSerializer(data, many=True)
    resp = {}
    for item in serializer.data:
        if item["candidate"] in DISQUALIFIED:
            item.update({"votes": -1})    
        item.update({"lag": item["block_time"]-item["lock_time"]})

    return serializer.data


def get_notary_vote_detail_table(request):
    year = helper.get_or_none(request, "year", VOTE_YEAR)
    candidate = helper.get_or_none(request, "candidate")
    proposals = get_candidates_proposals(request)
    notary_vote_detail_table = get_notary_vote_table(request)

    for item in notary_vote_detail_table:
        notary = translate_candidate_to_proposal_name(item["candidate"])
        item.update({
            "proposal": proposals[notary.lower()]
        })

    if candidate:
        candidate = request.GET["candidate"].replace(".", "-")

    if 'results' in notary_vote_detail_table:
        notary_vote_detail_table = notary_vote_detail_table["results"]

    for item in notary_vote_detail_table:
        date_time = datetime.fromtimestamp(item["block_time"])

        item.update({"block_time_human":date_time.strftime("%m/%d/%Y, %H:%M:%S")})
    return notary_vote_detail_table


def get_candidates_proposals(request):
    data = query.get_notary_candidates_data(VOTE_YEAR).values()
    props = {}
    for item in data:
        notary = item['name'].lower()
        if notary not in props:
            props.update({notary:item["proposal_url"]})
    return props


def translate_candidate_to_proposal_name(notary):
    x = notary.split("_")
    region = x[-1]
    notary = notary.replace(f"_{region}", "")
    if notary == "shadowbit":
        return "decker"
    if notary == "kolo2":
        return "kolo"
    if notary == "phit":
        return "phm87"
    if notary == "cipi2":
        return "cipi"
    if notary == "vanbogan":
        return "van"
    if notary == "metaphilbert":
        return "metaphilibert"
    if notary == "xenbug":
        return "xen"
    if notary == "marmara":
        return "marmarachain"
    if notary == "biz":
        return "who-biz"
    return notary


def get_vote_stats_info(request):
    resp = get_notary_vote_stats_info(request)

    proposals = get_candidates_proposals(request)

    for region in resp:
        for item in resp[region]:
            notary = translate_candidate_to_proposal_name(item["candidate"])
            item.update({
                "proposal": proposals[notary.lower()]
            })
    return resp


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


def translate_proposal_name_to_candidate(name, candidates):
    if name == "metaphilbert":
        name =  "metaphilibert"
    if name == "xenbug":
        name = "xen"
    if name == "who-biz":
        return "biz"
    for candidate in candidates:
        if candidate.lower().find(name.lower()) > -1:
            return candidate.lower()
    return name

    

def get_vote_aggregates(request):
    candidate = helper.get_or_none(request, "candidate")
    year = helper.get_or_none(request, "year", VOTE_YEAR)

    data = list(query.get_notary_vote_data(year).values('candidate', 'votes'))
    resp = {}
    for item in data:
        candidate = item["candidate"]
        if candidate not in resp:
            resp.update({candidate:{"votes": 0}})
        resp[candidate]["votes"] += item["votes"]

    return resp


def is_election_over(year):
    final_block = 22920
    return f"Election complete! Final VOTE2022 block height: <a href='https://vote2022.komodod.com/b/{final_block}'>{final_block}</a>" 
