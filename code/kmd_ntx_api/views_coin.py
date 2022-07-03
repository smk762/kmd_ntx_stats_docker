#!/usr/bin/env python3
import random
import numpy as np
from datetime import datetime as dt
from django.shortcuts import render

from kmd_ntx_api.lib_const import *
import kmd_ntx_api.lib_info as info
import kmd_ntx_api.lib_helper as helper
import kmd_ntx_api.lib_stats as stats
import kmd_ntx_api.lib_graph as graph
import kmd_ntx_api.lib_query as query
import kmd_ntx_api.lib_mining as mining
import kmd_ntx_api.lib_table as table
import kmd_ntx_api.lib_wallet as wallet


def coin_profile_view(request, coin=None): # TODO: REVIEW and ALIGN with NOTARY PROFILE
    season = helper.get_page_season(request)
    coin = helper.get_or_none(request, "coin", coin)
    server = helper.get_coin_server(season, coin)
    context = helper.get_base_context(request)
    context.update({
        "server": server,
        "page_title": "Coin Profile Index"
    })
    
    if coin:
        coin_profile_summary_table = table.get_coin_ntx_season_table_data(request, coin)
        if len(coin_profile_summary_table["coin_ntx_summary_table"]) == 1:

            coin_ntx_summary_table = coin_profile_summary_table["coin_ntx_summary_table"][0]

            coins_data = info.get_coins(request, coin)
            if coin in coins_data:
                coins_data = coins_data[coin]

            coin_balances = wallet.get_balances_rows(request, None, coin)
            max_tick = 0
            for item in coin_balances:
                if float(item['balance']) > max_tick:
                    max_tick = float(item['balance'])
            if max_tick > 0:
                10**(int(round(np.log10(max_tick))))
            else:
                max_tick = 10

            notary_icons = info.get_notary_icons(request)
            coin_notariser_ranks = stats.get_coin_notariser_ranks(season)
            top_region_notarisers = stats.get_top_region_notarisers(coin_notariser_ranks)
            top_coin_notarisers = stats.get_top_coin_notarisers(
                                        top_region_notarisers, coin, notary_icons
                                    )

            context.update({
                "page_title": f"{coin} Profile",
                "server": server,
                "coin": coin,
                "coins_data": coins_data,
                "notary_icons": notary_icons,
                "coin_balances": coin_balances, # Balances in table format
                "max_tick": max_tick,
                "coin_social": info.get_coin_social_info(request),
                "coin_ntx_summary": info.get_coin_ntx_summary(season, coin),
                "coin_ntx_summary_table": coin_ntx_summary_table,
                "coin_notariser_ranks": coin_notariser_ranks,
                "top_region_notarisers": top_region_notarisers,
                "top_coin_notarisers": top_coin_notarisers
            })            

            return render(request, 'views/coin/coin_profile.html', context)

    buttons = ["Main", "Third_Party"]
    button_params = {
        "Main": {
            "action": f"show_card('Main', {buttons})",
            "width_pct": 19,
            "text": "Main"
        },
        "Third_Party": {
            "action": f"show_card('Third_Party', {buttons})",
            "width_pct": 19,
            "text": "Third Party"
        }
    }
    coins_dict = helper.get_dpow_server_coins_dict(season)
    coins_dict["Main"] += ["KMD", "LTC"]
    coins_dict["Main"].sort()
    context.update({ 
        "buttons": button_params,
        "coin_social": info.get_coin_social_info(request),
        "server_coins": coins_dict
    })
    return render(request, 'views/coin/coin_profile_index.html', context)


def notarised_tenure_view(request):
    context = helper.get_base_context(request)
    context.update({
        "page_title":f"Coin Notarisation Tenure"
    })
    return render(request, 'views/ntx/notarised_tenure.html', context)


def coins_last_ntx(request):
    season = helper.get_page_season(request)
    context = helper.get_base_context(request)
    server = helper.get_or_none(request, "server")
    coin = helper.get_or_none(request, "coin")
    context.update({
        "page_title": f"dPoW Last Coin Notarisations",    
        "server": server,
        "coin": coin
    })

    return render(request, 'views/ntx/coins_last_ntx.html', context)


def coin_notarised_24hrs_view(request):
    coin = helper.get_or_none(request, "coin", "MORTY")
    context = helper.get_base_context(request)
    context.update({
        "coin": coin,
    })
    return render(request, 'views/coin/coin_notarised_24hrs.html', context)


def scoring_epochs_view(request):
    season = helper.get_page_season(request)
    epochs = requests.get(f"{THIS_SERVER}/api/table/scoring_epochs/?season={season}").json()['results']
    context = helper.get_base_context(request)
    context.update({
        "page_title":f"dPoW Scoring Epochs",
        "epochs":epochs
    })
    return render(request, 'views/ntx/scoring_epochs.html', context)
 
 