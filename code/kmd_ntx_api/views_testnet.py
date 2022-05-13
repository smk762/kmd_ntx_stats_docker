#!/usr/bin/env python3
import requests
import datetime as dt
from datetime import datetime, timezone
from django.shortcuts import render
from kmd_ntx_api.lib_const import *
import kmd_ntx_api.lib_helper as helper
import kmd_ntx_api.lib_testnet as testnet


def testnet_ntx_scoreboard_view(request):
    context = helper.get_base_context(request)
    year = helper.get_or_none(request, "year", VOTE_YEAR)
 
    testnet_ntx_counts = testnet.get_api_testnet(request)

    context = helper.get_base_context(request)
    context.update({
        "year": year,
        "season": f"{year}_Testnet"
    })
    return render(request, 'views/vote/testnet_scoreboard.html', context)


def notary_vote_view(request):
    context = helper.get_base_context(request)
    year = helper.get_or_none(request, "year", VOTE_YEAR)
    context.update({
        "regions": ["AR", "EU", "NA", "SH"],
        "end_timestamp": VOTE_PERIODS[year]["max_blocktime"],
        "year": year
    })

    return render(request, 'views/vote/notary_vote.html', context)


def notary_vote_detail_view(request):
    context = helper.get_base_context(request)
    year = helper.get_or_none(request, "year", VOTE_YEAR)
    candidate = helper.get_or_none(request, "candidate")
    max_block = helper.get_or_none(request, "max_block", VOTE_PERIODS[year]["max_block"])

    proposals = testnet.get_notary_candidates_info(request)
    notary_vote_detail_table = testnet.get_notary_vote_table(request)

    for item in notary_vote_detail_table:
        notary = testnet.translate_notary(item["candidate"])
        item.update({
            "proposal": proposals[notary]
        })

    if candidate:
        candidate = request.GET["candidate"].replace(".", "-")

    if 'results' in notary_vote_detail_table:
        notary_vote_detail_table = notary_vote_detail_table["results"]

    for item in notary_vote_detail_table:
        date_time = datetime.fromtimestamp(item["block_time"])

        item.update({"block_time_human":date_time.strftime("%m/%d/%Y, %H:%M:%S")})

    context.update({
        "candidate": candidate,
        "year": year,
        "notary_vote_detail_table": notary_vote_detail_table
    })

    return render(request, 'views/vote/notary_vote_detail.html', context)


def s5_address_confirmation(request):
    # Populate sidebar
    context = helper.get_base_context(request)

    addr_confirmed_in_PR = [
        "alien_AR",
        "alien_EU",
        "alien_NA",
        "alienx_EU",
        "alienx_NA",
        "computergenie_NA",
        "dappvader_SH",
        "drkush_SH",
        "goldenman_AR",
        "kolo_AR",
        "node-9_EU",
        "node-9_NA",
        "nodeone_NA",
        "nutellaLicka_SH",
        "ptyx_NA",
        "phit_SH",
        "sheeba_SH",
        "slyris_EU",
        "strob_SH",
        "strob_NA",
        "strobnidan_SH",
        "tonyl_AR",
        "tonyl_DEV",
        "strobnidan_SH",
        "webworker01_NA",
        "van_EU"
    ]
    pub_confirmed_in_PR = [
        "alien_AR",
        "alien_EU",
        "alien_NA",
        "alienx_EU",
        "alienx_NA",
        "artem_DEV",
        "artempikulin_AR",
        "ca333_EU",
        "chmex_AR",
        "chmex_EU",
        "chmex_SH",
        "cipi_EU",
        "cipi_AR",
        "cipi_NA",
        "cipi2_EU",
        "collider_SH",
        "karasugoi_NA",
        "komodopioneers_EU",
        "madmax_AR",
        "madmax_EU",
        "madmax_NA",
        "marmarachain_EU",
        "majora31_SH",
        "karasugoi_NA",
        "metaphilibert_SH",
        "mrlynch_AR",
        "metaphilibert_SH",
        "pbca26_NA",
        "pbca26_SH",
        "smdmitry_AR",
        "smdmitry_EU",
        "pbca26_SH",
        "mcrypt_AR",
        "mcrypt_SH",
        "yurii_DEV"
    ]
    pub_confirmed_in_DM = [
        "gcharang_DEV",
        "mylo_SH",
        "hyper_NA",
        "tokel_AR",
        "shadowbit_AR",
        "shadowbit_EU",
        "shadowbit_DEV",
        "ocean_AR",
        "alrighttt_DEV",
        "ca333_DEV"
    ]
    addr_confirmed_in_DM = [
        "dragonhound_DEV",
        "dragonhound_NA",
    ]

    kmd_addresses = requests.get(f"{THIS_SERVER}/api/table/addresses/?season=Season_5&coin=KMD").json()["results"]
    ltc_addresses = requests.get(f"{THIS_SERVER}/api/table/addresses/?season=Season_5&coin=LTC&server=Main").json()["results"]
    addresses = kmd_addresses + ltc_addresses

    for item in addresses:
        if item["notary"] in pub_confirmed_in_PR:
            item.update({"confirmed":"Pubkey (PR)"})
        elif item["notary"] in addr_confirmed_in_PR:
            item.update({"confirmed":"Address (PR)"})
        elif item["notary"] in pub_confirmed_in_DM:
            item.update({"confirmed":"Pubkey (DM)"})
        elif item["notary"] in addr_confirmed_in_DM:
            item.update({"confirmed":"Address (DM)"})

    context.update({
        "page_title": "Address Confirmation",
        "addresses": addresses,
    })

    return render(request, 'views/vote/s5_address_confirmation.html', context)
