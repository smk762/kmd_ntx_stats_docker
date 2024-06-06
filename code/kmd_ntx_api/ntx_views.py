#!/usr/bin/env python3
import time
import requests
from datetime import datetime as dt
from django.shortcuts import render
from django.contrib import messages
from kmd_ntx_api.buttons import get_faucet_buttons
from kmd_ntx_api.const import SINCE_INTERVALS
from kmd_ntx_api.context import get_base_context, get_notary_profile_context, \
    get_notary_profile_index_context, get_coin_profile_context, \
    get_coin_profile_index_context
from kmd_ntx_api.helper import get_or_none, get_notary_list, \
    get_page_server
from kmd_ntx_api.coins import get_dpow_coin_server
from kmd_ntx_api.info import get_nn_social_info
from kmd_ntx_api.logger import logger
from kmd_ntx_api.notary_seasons import get_page_season, get_notary_seasons
from kmd_ntx_api.query import get_notarised_data
from kmd_ntx_api.stats import get_season_stats_sorted, \
    get_region_score_stats, get_daily_stats_sorted
from kmd_ntx_api.seednodes import seednode_version_context
from kmd_ntx_api.serializers import notarisedSerializer
from kmd_ntx_api.table import get_notary_epoch_scores_table


def notary_profile_view(request, notary=None):
    logger.info("notary_profile_view")
    context = get_base_context(request)
    # TODO: This is not currently used, but can be added for prior season stats given fully populated databases
    context.update({
        "notary_seasons": get_notary_seasons(),
        "notary": notary
    })
    # Base context will return a random notary if one is not specified. For this view, we prefer 'None'.
    if notary in context["notaries"]:
        context = get_notary_profile_context(request, notary, context)
        return render(request, 'views/notarisation/notary_profile.html', context)
    context = get_notary_profile_index_context(request, context)
    return render(request, 'views/notarisation/notary_profile_index.html', context)


def coin_profile_view(request, coin=None): # TODO: REVIEW and ALIGN with NOTARY PROFILE
    logger.info("coin_profile_view")
    context = get_base_context(request)
    season = context["season"]
    coin = get_or_none(request, "coin", coin)
    context.update({
        "server": get_dpow_coin_server(season, coin),
        "page_title": "Coin Profile Index"
    })

    if coin:
        context = get_coin_profile_context(request, season, coin, context)
        return render(request, 'views/coin/coin_profile.html', context)   
    context = get_coin_profile_index_context(request, season, context)
    return render(request, 'views/coin/coin_profile_index.html', context)


def ntx_scoreboard_view(request, region=None):
    logger.info("ntx_scoreboard_view")
    context = get_base_context(request)
    context["region"] = get_or_none(request, "region", region)
    season_stats_sorted = get_season_stats_sorted(context["season"], context["notaries"])
    context.update({
        "page_title": f"Notarisation Scoreboard",
        "anchored": True,
        "season_stats_sorted": season_stats_sorted,
        "region_score_stats": get_region_score_stats(season_stats_sorted),
        "nn_social": get_nn_social_info(request)
    })
    return render(request, 'views/ntx/ntx_scoreboard.html', context)


def ntx_scoreboard_24hrs_view(request, region=None):
    logger.info("ntx_scoreboard_24hrs_view")
    context = get_base_context(request)
    context["region"] = get_or_none(request, "region", region)
    context.update({
        "page_title": f"Last 24hrs Notarisation Scoreboard",
        "anchored": True,
        "daily_stats_sorted": get_daily_stats_sorted(context["notaries"], context["dpow_coins_dict"]),
        "nn_social": get_nn_social_info(request)
    })
    return render(request, 'views/ntx/ntx_scoreboard_24hrs.html', context)
 
 
def seednode_version_view(request):
    logger.info("seednode_version_view")
    context = get_base_context(request)
    context.update(seednode_version_context(request))
    return render(request, 'views/atomicdex/seednode_version_stats.html', context)


def coins_last_ntx_view(request):
    logger.info("coins_last_ntx_view")
    season = get_page_season(request)
    context = get_base_context(request)
    server = get_page_server(request)
    coin = get_or_none(request, "coin")
    context.update({
        "page_title": f"dPoW Last Coin Notarisations",    
        "server": server,
        "coin": coin
    })

    return render(request, 'views/ntx/coins_last_ntx.html', context)

def notarised_tenure_view(request):
    logger.info("notarised_tenure_view")
    context = get_base_context(request)
    context.update({
        "page_title":f"Coin Notarisation Tenure"
    })
    return render(request, 'views/ntx/notarised_tenure.html', context)


def notarisation_view(request):
    txid = get_or_none(request, "txid", "5507e4fb484e51e6d748585e7e08dcda4bb17bfb420c9ccd2c43c0481e265bf6")
    ntx_data = get_notarised_data(txid=txid)
    context = get_base_context(request)
    serializer = notarisedSerializer(ntx_data, many=True)
    context.update({"ntx_data": dict(serializer.data[0])})
    return render(request, 'views/ntx/notarisation.html', context)


def notaryfaucet_view(request):
    season = get_page_season(request)
    notary_list = get_notary_list(season)
    coins_list = []
    try:
        faucet_coins = requests.get("https://notaryfaucet.dragonhound.tools/faucet_coins").json()["result"]
        coins_list = faucet_coins["Main"] + faucet_coins["3P"]
    except:
        pass
    faucet_balances = requests.get("https://notaryfaucet.dragonhound.tools/faucet_balances").json()
    pending_tx_resp = requests.get("https://notaryfaucet.dragonhound.tools/show_pending_tx").json()
    pending_tx_list = []
    tx_rows = []
    pending_index = []
    if "result" in pending_tx_resp:
        if "message" in pending_tx_resp["result"]:
            pending_tx_list = pending_tx_resp["result"]["message"]
    for item in pending_tx_list:
        try:
            logger.info(item)
            tx_rows.append({
                "index": item[0],
                "coin": item[1],
                "pubkey": item[2],
                "notary": item[3],
                "time_sent": "n/a",
                "timestamp": 99999999999999,
                "amount": "n/a",
                "txid": "n/a",
                "status": item[7]
            })
            pending_index.append(item[0])
        except Exception as e:
            logger.info(f"Error: {e}")
        if len(tx_rows) >= 250:
            break
    sent_tx_resp = requests.get("https://notaryfaucet.dragonhound.tools/show_faucet_db").json()
    sent_tx_list = []
    now = time.time()
    sum_24hrs = 0
    count_24hrs = 0
    if "result" in sent_tx_resp:
        if "message" in sent_tx_resp["result"]:
            sent_tx_list = sent_tx_resp["result"]["message"]
    for item in sent_tx_list:
        if item[0] not in pending_index:
            if item[4] > SINCE_INTERVALS['day']:
                sum_24hrs += item[5]
                count_24hrs += 1
            tx_rows.append({
                "index":item[0],
                "coin":item[1],
                "pubkey":item[2],
                "notary": item[3],
                "timestamp": item[4],
                "time_sent":dt.utcfromtimestamp(item[4]),
                "amount":item[5],
                "txid":item[6],
                "status":item[7]
            })
    context = get_base_context(request)
    context.update({
        "page_title": "Notary Faucet",
        "explorers": True,
        "count_24hrs": count_24hrs,
        "sum_24hrs": sum_24hrs,
        "coins_list": coins_list,
        "tx_rows": tx_rows,
        "buttons": get_faucet_buttons(),
        "faucet_balances": faucet_balances
    })
    if request.method == 'POST':
        try:
            if 'coin' in request.POST:
                coin = request.POST['coin'].strip()
            if 'pubkey' in request.POST:
                pubkey = request.POST['pubkey'].strip()
            url = f'https://notaryfaucet.dragonhound.tools/faucet/{pubkey}/{coin}'
            r = requests.get(url)
            resp = r.json()
            messages.success(request, resp["result"]["message"])
            if resp['status'] == "success":
                context.update({"result":coin+"_success"})
            elif resp['status'] == "error":
                context.update({"result":"disqualified"})
            else:
                context.update({"result":"fail"})
        except Exception as e:
            logger.error(f"[notaryfaucet] Exception: {e}")
            messages.success(request, f"Something went wrong... {e} {url}")
            context.update({"result":"fail"})
    return render(request, 'views/tools/tool_notaryfaucet.html', context)
def coin_profile_view(request, coin=None): # TODO: REVIEW and ALIGN with NOTARY PROFILE
    context = get_base_context(request)
    season = context["season"]
    coin = get_or_none(request, "coin", coin)
    context.update({
        "server": get_dpow_coin_server(season, coin),
        "page_title": "Coin Profile Index"
    })
    
    if coin:
        context = get_coin_profile_context(request, season, coin, context)
        return render(request, 'views/coin/coin_profile.html', context)    
    context = get_coin_profile_index_context(request, season, context)
    return render(request, 'views/coin/coin_profile_index.html', context)


def notary_coin_notarised_view(request):
    context = get_base_context(request)
    season = context["season"]
    notary = context["notary"]
    server = context["server"]
    coin = context["coin"]
    context.update({
        "server": server,
        "coin": coin,
        "notary": notary, 
        "filter_params": f"&notary={{{notary}}}&coin={coin}&season={season}&server={server}"
    })

    return render(request, 'views/ntx/notary_coin_notarised.html', context)


def notary_epoch_scores_view(request):
    context = get_base_context(request)
    notary = context["notary"]
    scoring_table, totals = get_notary_epoch_scores_table(request, notary)
    try:
        context.update({
            "table_title": context["notary_clean"],
            "scoring_table": scoring_table,
            "total_count":totals["counts"][notary],
            "total_score":totals["scores"][notary],
            "nn_social": get_nn_social_info(request),
            "table": "epoch_scoring"            
        })
    except Exception as e:
        messages.error(request, f"Error: {e}")
    return render(request, 'views/ntx/notary_epoch_scores_view.html', context)


def notarised_24hrs_view(request):    
    context = get_base_context(request)
    context.update({
        "page_title":"dPoW Notarisations (last 24hrs)"
    })
    return render(request, 'views/ntx/notarised_24hrs.html', context)


def notary_epoch_coin_notarised_view(request):
    context = get_base_context(request)
    return render(request, 'views/ntx/notary_epoch_coin_notarised.html', context)
