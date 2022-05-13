#!/usr/bin/env python3
from django.db.models import Sum, Max, Count
from kmd_ntx_api.lib_const import *
import kmd_ntx_api.lib_info as info
import kmd_ntx_api.lib_query as query
import kmd_ntx_api.lib_helper as helper
import kmd_ntx_api.serializers as serializers

def get_api_testnet(request):
    year = helper.get_or_none(request, "year", VOTE_YEAR)
    season = f"{year}_Testnet"
    notary_list = helper.get_notary_list(season)

    # Prepare ntx data
    ntx_data = query.get_notarised_data(season).order_by(
        'coin', '-block_height').values()

    # Prepare 24hr ntx data
    ntx_data_24hr = info.get_notarised_data_24hr(
        season).order_by('coin', '-block_height').values()

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

    testnet_coins = list(ntx_dict.keys())
    testnet_stats_dict = get_testnet_stats_dict(season, testnet_coins)
    last_ntx = info.get_last_nn_coin_ntx(season)

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
                logger.error(f"[get_api_testnet] Exception: {e} \
                               | notary: {notary} | coin: {coin}")
                logger.warning(f"[get_api_testnet] Setting last_ntx for \
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
                    logger.warning(f"[get_api_testnet] {notary} not \
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
                    logger.warning(f"[get_api_testnet] {notary} not found \
                                     in ntx_notaries: {item}")

    # Get notarisation rank
    notary_totals = {}
    for notary in testnet_stats_dict:
        notary_totals.update({notary: testnet_stats_dict[notary]["Total"]})
    ranked_totals = {k: v for k, v in sorted(
        notary_totals.items(), key=lambda x: x[1])}
    ranked_totals = dict(reversed(list(ranked_totals.items())))
    logger.info(ranked_totals)

    i = 0
    for notary in ranked_totals:
        i += 1
        testnet_stats_dict[notary].update({"Rank": i})

    # Get 24hr notarisation rank
    notary_totals_24hr = {}
    for notary in testnet_stats_dict:
        notary_totals_24hr.update(
            {notary: testnet_stats_dict[notary]["24hr_Total"]})
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
    valid = helper.get_or_none(request, "valid", "true")

    if valid is not None:
        valid = (valid == "true")

    data = query.get_notary_vote_data(year, candidate, block, txid, max_block, max_blocktime, max_locktime, None, valid)
    data = data.values('candidate', 'candidate_address').annotate(num_votes=Count('votes'), sum_votes=Sum('votes'))

    resp = {}
    region_scores = {}
    for item in data:
        region = item["candidate"].split("_")[1]
        if region not in resp:
            resp.update({region:[]})
            region_scores.update({region:[]})
        resp[region].append(item)
        if item["candidate"] in DISQUALIFIED:
            region_scores[region].append(-1)
        else:
            region_scores[region].append(item["sum_votes"])


    for region in resp:
        region_scores[region].sort()
        region_scores[region].reverse()
        for item in resp[region]:
            if item["candidate"] in DISQUALIFIED:
                rank = region_scores[region].index(-1) + 1
                item.update({"sum_votes": "DISQUALIFIED"})
            else:
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
        data = data.values().order_by(f'-{order_by}')
    else:
        data = data.values().order_by(f'-block_time')

    serializer = serializers.notaryVoteSerializer(data, many=True)
    resp = {}
    for item in serializer.data:
        if item["candidate"] in DISQUALIFIED:
            item.update({"votes": -1})    
        item.update({"lag": item["block_time"]-item["lock_time"]})

    return serializer.data


def get_notary_candidates_info(request):
    year = helper.get_or_none(request, "year", VOTE_YEAR)
    data = query.get_notary_candidates_data(year).values()
    props = {}
    for item in data:
        notary = item['name']
        if notary not in props:
            props.update({notary:item["proposal_url"]})
    return props

def translate_notary(notary):
    notary = notary.lower().split("_")[0]
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
    return notary

def translate_testnet_name(name, candidates):
    for candidate in candidates:
        if candidate.lower().find(name.lower()) > -1:
            return candidate
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
    end_time = VOTE_PERIODS[year]["max_blocktime"]
    print(time.time(), end_time)
    if time.time() < end_time:
        return "before timestamp"
    
    last_notarised_blocks = query.get_notarised_data(
        season="Season_5", coin=year, min_blocktime=end_time)
    print(last_notarised_blocks.count())
    if last_notarised_blocks.count() == 0:
        return "Waiting for notarised block..."

    else:
        return "Election complete!"