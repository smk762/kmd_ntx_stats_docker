#!/usr/bin/env python3
import time
import random
import numpy as np
from datetime import datetime as dt
from django.shortcuts import render
from django.db.models import Sum
from kmd_ntx_api.lib_const import *
from kmd_ntx_api.pages import *
from kmd_ntx_api.endpoints import *

import kmd_ntx_api.lib_helper as helper
import kmd_ntx_api.lib_mining as mining
import kmd_ntx_api.lib_query as query
import kmd_ntx_api.lib_stats as stats
import kmd_ntx_api.lib_info as info
import kmd_ntx_api.lib_table as table
import kmd_ntx_api.lib_info as info


def dash_view(request, dash_name=None):
    season = helper.get_page_season(request)
    # Table Views
    context = helper.get_base_context(request)

    day_ago = int(time.time()) - SINCE_INTERVALS['day']

    # Get NTX Counts
    data = query.get_notarised_data(season=season, exclude_epoch="Unofficial")
    ntx_season = data.count()
    ntx_24hr = data.filter(block_time__gt=str(day_ago)).count()


    # Get Mining Stats
    try:
        mined_data = query.get_mined_data(season=season)
        mined_season = mined_data.aggregate(Sum('value'))['value__sum']
    except Exception as e:
        print(e)
        mined_season = 0

    try:
        mined_24hr = mined_data.filter(block_time__gt=str(day_ago)).aggregate(Sum('value'))['value__sum']        
    except Exception as e:
        print(e)
        mined_24hr = 0
    
    try:
        biggest_block = mined_data.order_by('-value').first()
    except Exception as e:
        print(e)
        biggest_block = 0
    

    coins_dict = helper.get_dpow_server_coins_dict(season)
    coins_list = []
    for server in coins_dict: 
        coins_list += coins_dict[server]

    daily_stats_sorted = stats.get_daily_stats_sorted(season, coins_dict)
    season_stats_sorted = stats.get_season_stats_sorted(season, coins_list)
    nn_social = info.get_nn_social_info(request)
    region_score_stats = stats.get_region_score_stats(season_stats_sorted)
    sidebar_links = helper.get_sidebar_links(season)

    context.update({
        "page_title": "Index",
        "ntx_24hr": ntx_24hr,
        "ntx_season": ntx_season,
        "mined_24hr": mined_24hr,
        "mined_season": mined_season,
        "biggest_block": biggest_block,
        "season_stats_sorted": season_stats_sorted,
        "region_score_stats": region_score_stats,
        "show_ticker": True,
        "server_coins": coins_dict,
        "coins_list": coins_list,
        "daily_stats_sorted": daily_stats_sorted,
        "nn_social": nn_social
    })
    return render(request, 'views/dash_index.html', context)
    

def funds_sent(request):
    season = helper.get_page_season(request)
    notary_list = helper.get_notary_list(season)
    funding_data = query.get_funding_transactions_data(season).values()
    funding_totals = info.get_funding_totals(funding_data)

    context = helper.get_base_context(request)
    context.update({
        "page_title": "Funding Sent",
        "funding_data": funding_data,
        "funding_totals": funding_totals,
    })

    return render(request, 'funding_sent.html', context)


def funding(request):
    season = helper.get_page_season(request)
    # add extra views for per coin or per notary
    low_nn_balances = helper.get_low_nn_balances()
    last_balances_update = helper.day_hr_min_sec(int(time.time()) - low_nn_balances['time'])
    human_now = time.strftime("%a, %d %b %Y %H:%M:%S", time.gmtime())

    coin_low_balance_notary_counts = {}
    notary_low_balance_coin_counts = {}

    ok_balance_notaries = []
    ok_balance_coins = []
    no_data_coins = list(low_nn_balances['sources']['failed'].keys())

    low_balance_data = low_nn_balances['low_balances']
    low_nn_balances['low_balance_coins'].sort()
    low_nn_balances['low_balance_notaries'].sort()

    notary_list = helper.get_notary_list(season)
    coin_list = info.get_dpow_coins_list(season)

    num_coins = len(coin_list)
    num_notaries = len(notary_list)
    num_addresses = num_notaries * num_coins

    # count addresses with low / sufficient balance
    num_low_balance_addresses = 0
    for notary in low_balance_data:
        for coin in low_balance_data[notary]:
            if coin in coin_list:
                num_low_balance_addresses += 1
    num_ok_balance_addresses = num_addresses-num_low_balance_addresses            

    for coin in coin_list:
        coin_low_balance_notary_counts.update({coin:0})
        if coin not in low_nn_balances['low_balance_coins'] and coin not in no_data_coins:
            ok_balance_coins.append(coin)

    for notary in notary_list:
        notary_low_balance_coin_counts.update({notary:0})
        if notary in low_balance_data:
            notary_low_balance_coin_counts.update({notary:len(low_balance_data[notary])})
            for coin in low_balance_data[notary]:
                if coin in coin_list:
                    if coin == 'KMD_3P':
                        val = coin_low_balance_notary_counts["KMD"] + 1
                        coin_low_balance_notary_counts.update({"KMD":val})
                    else:
                        val = coin_low_balance_notary_counts[coin] + 1
                        coin_low_balance_notary_counts.update({coin:val})
        if notary not in low_nn_balances['low_balance_notaries']:
            ok_balance_notaries.append(notary)

    coins_dict = helper.get_dpow_server_coins_dict(season)
    coin_balance_graph_data = helper.prepare_regional_graph_data(notary_low_balance_coin_counts)
    notary_balance_graph_data = helper.prepare_coins_graph_data(coin_low_balance_notary_counts, coins_dict)

    coins_funded_pct = round(len(ok_balance_coins)/len(coin_list)*100,2)
    notaries_funded_pct = round(len(ok_balance_notaries)/len(notary_list)*100,2)
    addresses_funded_pct = round((num_addresses-num_low_balance_addresses)/num_addresses*100,2)

    context = helper.get_base_context(request)
    context.update({
        "page_title":"Funding Info",
        "coins_funded_pct":coins_funded_pct,
        "notaries_funded_pct":notaries_funded_pct,
        "addresses_funded_pct":addresses_funded_pct,
        "num_ok_balance_addresses":num_ok_balance_addresses,
        "num_low_balance_addresses":num_low_balance_addresses,
        "num_addresses":num_addresses,
        "coin_balance_graph_data":coin_balance_graph_data,
        "notary_balance_graph_data":notary_balance_graph_data,
        "coin_low_balance_notary_counts":coin_low_balance_notary_counts,
        "notary_low_balance_coin_counts":notary_low_balance_coin_counts,
        "low_balance_notaries":low_nn_balances['low_balance_notaries'],
        "low_balance_coins":low_nn_balances['low_balance_coins'],
        "ok_balance_notaries":ok_balance_notaries,
        "ok_balance_coins":ok_balance_coins,
        "no_data_coins":no_data_coins,
        "coin_list":coin_list,
        "notaries_list":notary_list,
        "last_balances_update":last_balances_update,
        "low_nn_balances": helper.low_nn_balances['low_balances'],
        "notary_funding": helper.get_notary_funding(),
        "bot_balance_deltas": helper.get_bot_balance_deltas()
    })
    return render(request, 'funding.html', context)


def sitemap(request):

    context = helper.get_base_context(request)
    context.update({
        "page_title":f"Sitemap",
        "endpoints":ENDPOINTS,
        "pages":PAGES
    })

    return render(request, 'sitemap.html', context)


def test_component(request):
    context = helper.get_base_context(request)
    context.update({
        "page_title":f"Test"
    })

    return render(request, 'components/tables/generic_source/notary_vote_table.html', context)
    return render(request, 'tables/ntx_node_daily.html', context)

