#!/usr/bin/env python3

from kmd_ntx_api.lib_info import *

def get_api_testnet(request):
    season = "Season_5_Testnet"

    # Prepare ntx data
    ntx_data = get_notarised_data(season).order_by('chain', '-block_height').values()

    # Prepare 24hr ntx data
    ntx_data_24hr = get_notarised_data_24hr(season).order_by('chain', '-block_height').values()

    ntx_dict = {}
    ntx_dict_24hr = {}

    for item in ntx_data:
        chain = item['chain']
        if chain not in ntx_dict:
            ntx_dict.update({chain:[]})
            ntx_dict_24hr.update({chain:[]})
        # RICK/MORTY heights from gcharang
        # https://discord.com/channels/412898016371015680/455755767132454913/823823358768185344
        if chain in ["RICK", "MORTY"] and item["block_height"] >= 2316959:
            ntx_dict[chain].append(item)
        elif chain in ["LTC"] and item["block_height"] >= 2022000:
            ntx_dict[chain].append(item)


    for item in ntx_data_24hr:
        chain = item['chain']
        if chain in ["RICK", "MORTY"] and item["block_height"] >= 2316959:
            ntx_dict_24hr[chain].append(item)
        elif chain in ["LTC"] and item["block_height"] >= 2022000:
            ntx_dict_24hr[chain].append(item)

    testnet_chains = list(ntx_dict.keys())

    testnet_stats_dict = get_testnet_stats_dict(season, testnet_chains)

    last_notarisations = get_last_nn_chain_ntx(season)

    for chain in testnet_chains:

        # Get last notarised times
        for notary in testnet_stats_dict:
            try:
                last_chain_ntx = last_notarisations[notary][chain]["time_since"]
                testnet_stats_dict[notary].update({f"Last_{chain}":last_chain_ntx})
            except Exception as e:
                logger.error(f"[get_api_testnet] Exception: {e} | notary: {notary} | chain: {chain}")
                testnet_stats_dict[notary].update({f"Last_{chain}":"> 24hrs"})

        # Get notarisation counts
        for item in ntx_dict[chain]:
            ntx_notaries = item["notaries"]

            for notary in ntx_notaries:
                if notary in testnet_stats_dict:

                    if testnet_stats_dict[notary]["Total"] == 0:
                        testnet_stats_dict[notary].update({"Total":1})

                    else:
                        count = testnet_stats_dict[notary]["Total"]+1
                        testnet_stats_dict[notary].update({"Total":count})

                    if testnet_stats_dict[notary][chain] == 0:
                        testnet_stats_dict[notary].update({chain:1})
                        testnet_stats_dict[notary].update({chain:1})
                        
                    else:
                        count = testnet_stats_dict[notary][chain]+1
                        testnet_stats_dict[notary].update({chain:count})
                else:
                    logger.warning(f"[get_api_testnet] {notary} not found in ntx_notaries: {item}")

        # Get notarisation counts 24hr
        for item in ntx_dict_24hr[chain]:
            ntx_notaries = item["notaries"]

            for notary in ntx_notaries:
                if notary in testnet_stats_dict:

                    if testnet_stats_dict[notary]["24hr_Total"] == 0:
                        testnet_stats_dict[notary].update({"24hr_Total":1})

                    else:
                        count = testnet_stats_dict[notary]["24hr_Total"]+1
                        testnet_stats_dict[notary].update({"24hr_Total":count})

                    if testnet_stats_dict[notary][chain] == 0:
                        testnet_stats_dict[notary].update({f"24hr_{chain}":1})
                        testnet_stats_dict[notary].update({f"24hr_{chain}":1})
                        
                    else:
                        count = testnet_stats_dict[notary][f"24hr_{chain}"]+1
                        testnet_stats_dict[notary].update({f"24hr_{chain}":count})
                else:
                    logger.warning(f"[get_api_testnet] {notary} not found in ntx_notaries: {item}")


    # Get notarisation rank
    notary_totals = {}
    for notary in testnet_stats_dict:
        notary_totals.update({notary:testnet_stats_dict[notary]["Total"]})
    ranked_totals = {k: v for k, v in sorted(notary_totals.items(), key=lambda x: x[1])}
    ranked_totals = dict(reversed(list(ranked_totals.items()))) 

    i = 0
    for notary in ranked_totals:
        i += 1
        testnet_stats_dict[notary].update({"Rank":i})

    # Get 24hr notarisation rank
    notary_totals_24hr = {}
    for notary in testnet_stats_dict:
        notary_totals_24hr.update({notary:testnet_stats_dict[notary]["24hr_Total"]})
    ranked_totals_24hr = {k: v for k, v in sorted(notary_totals_24hr.items(), key=lambda x: x[1])}
    ranked_totals_24hr = dict(reversed(list(ranked_totals_24hr.items()))) 

    i = 0
    for notary in ranked_totals_24hr:
        i += 1
        testnet_stats_dict[notary].update({"24hr_Rank":i})

    return testnet_stats_dict