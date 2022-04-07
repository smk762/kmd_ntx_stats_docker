#!/usr/bin/env python3
import time
import random
import numpy as np
from datetime import datetime as dt
from django.shortcuts import render
from kmd_ntx_api.lib_const import *
from kmd_ntx_api.pages import *
from kmd_ntx_api.endpoints import *

import kmd_ntx_api.lib_helper as helper
import kmd_ntx_api.lib_query as query
import kmd_ntx_api.lib_stats as stats
import kmd_ntx_api.lib_info as info
import kmd_ntx_api.lib_testnet as testnet
import kmd_ntx_api.lib_table as table
import kmd_ntx_api.lib_info as info

def chains_last_ntx(request):
    season = helper.get_page_season(request)
    notary_list = helper.get_notary_list(season)
    last_notarised = {}
    last_notarised_data = query.get_last_notarised_data(season).values()
    for item in last_notarised_data:
        chain = item["chain"]
        block_time = item["block_time"]
        if chain not in last_notarised:
            last_notarised.update({
                chain:{
                    "server": item["server"],
                    "txid": item["txid"],
                    "notary": item["notary"],
                    "block_height": item["block_height"],
                    "block_time": item["block_time"],
                    "notaries": []
                }
            })
        elif block_time > last_notarised[chain]["block_time"]:
            last_notarised.update({
                chain:{
                    "server": item["server"],
                    "txid": item["txid"],
                    "notary": item["notary"],
                    "block_height": item["block_height"],
                    "block_time": item["block_time"],
                    "notaries": []
                }
            })
        if block_time == last_notarised[chain]["block_time"]:
            last_notarised[chain]["notaries"].append(item["notary"])
    for chain in last_notarised:
        last_notarised[chain]["notaries"] = ', '.join(last_notarised[chain]["notaries"])
    context = helper.get_base_context(request)
    context.update({
        "page_title": f"dPoW Last Chain Notarisations",
        "explorers": info.get_explorers(request),
        "last_notarised_data": last_notarised
    })

    return render(request, 'last_notarised.html', context)


def coin_profile_view(request, chain=None): # TODO: REVIEW and ALIGN with NOTARY PROFILE
    season = helper.get_page_season(request)
    server = helper.get_chain_server(chain, season)
    context = helper.get_base_context(request)
    context.update({
        "server": server,
        "page_title": "Coin Profile Index"
    })
    
    if chain:
        url = f"{THIS_SERVER}/api/table/balances/?season={season}&chain={chain}"
        chain_balances = requests.get(url).json()['results']

        url = f"{THIS_SERVER}/api/info/coins/?&chain={chain}"
        coins_data = requests.get(url).json()['results']
        if chain in coins_data:
            coins_data = coins_data[chain]

        max_tick = 0
        for item in chain_balances:
            if float(item['balance']) > max_tick:
                max_tick = float(item['balance'])
        if max_tick > 0:
            10**(int(round(np.log10(max_tick))))
        else:
            max_tick = 10

        coin_notariser_ranks = stats.get_coin_notariser_ranks(season)
        top_region_notarisers = stats.get_top_region_notarisers(coin_notariser_ranks)
        top_coin_notarisers = stats.get_top_coin_notarisers(top_region_notarisers, chain, season)
        chain_ntx_summary = info.get_coin_ntx_summary(season, chain)
        season_chain_ntx_data = info.get_season_chain_ntx_data(season)

        context.update({
            "page_title": f"{chain} Profile",
            "server": server,
            "chain": chain,
            "coins_data": coins_data,
            "chain_balances": chain_balances,
            "explorers": info.get_explorers(request),
            "max_tick": max_tick,
            "coin_social": info.get_coin_social(chain),
            "chain_ntx_summary": chain_ntx_summary,
            "coin_notariser_ranks": coin_notariser_ranks,
            "top_region_notarisers": top_region_notarisers,
            "top_coin_notarisers": top_coin_notarisers
        })            

        return render(request, 'coin_profile.html', context)
    else:
        coins_dict = helper.get_dpow_server_coins_dict(season)
        coins_dict["Main"] += ["KMD", "LTC"]
        coins_dict["Main"].sort()
        context.update({ 
            "coin_social": info.get_coin_social(),
            "server_coins": coins_dict
        })
        return render(request, 'coin_profile_index.html', context)


def dash_view(request, dash_name=None):
    season = helper.get_page_season(request)
    # Table Views
    context = helper.get_base_context(request)
    context.update({
        "page_title": "Index"
    })
    gets = ''
    html = 'dash_index.html'

    notary_list = helper.get_notary_list(season)
    coins_dict = helper.get_dpow_server_coins_dict(season)
    coins_list = []
    for server in coins_dict: 
        coins_list += coins_dict[server]

    if dash_name:
        if dash_name.find('table') != -1:
            if dash_name == 'balances_table':
                html = 'tables/balances.html'
            elif dash_name == 'addresses_table':
                html = 'tables/addresses.html'
            elif dash_name == 'rewards_table':
                html = 'tables/rewards.html'
            elif dash_name == 'mining_table':
                html = 'tables/mining.html'
            elif dash_name == 'mining_season_table':
                html = 'tables/mining_season.html'
            elif dash_name == 'mining_daily_table':
                html = 'tables/mining_daily.html'
            elif dash_name == 'ntx_table':
                html = 'tables/ntx.html'
            elif dash_name == 'ntx_chain_season_table':
                html = 'tables/ntx_chain_season.html'
            elif dash_name == 'ntx_chain_daily_table':
                html = 'tables/ntx_chain_daily.html'
            elif dash_name == 'ntx_node_season_table':
                html = 'tables/ntx_node_season.html'
            elif dash_name == 'ntx_node_daily_table':
                html = 'tables/ntx_node_daily.html'
        # Table Views
        elif dash_name.find('graph') != -1:
            getlist = []
            for k in request.GET:
                getlist.append(k+"="+request.GET[k])
            gets = '&'.join(getlist)
            if dash_name == 'balances_graph':
                html = 'graphs/balances.html'
            if dash_name == 'daily_ntx_graph':
                html = 'graphs/daily_ntx_graph.html'
            if dash_name == 'daily_mining_graph':
                html = 'graphs/mined.html'
            if dash_name == 'season_ntx_graph':
                html = 'graphs/daily_ntx_graph.html'
            if dash_name == 'season_mining_graph':
                html = 'graphs/daily_ntx_graph.html'
    else:
        day_ago = int(time.time()) - SINCE_INTERVALS['day']
        ntx_24hr = query.get_notarised_data().filter(
            block_time__gt=str(day_ago)).count()
        try:
            mined_24hr = query.get_mined_data_24hr().aggregate(Sum('value'))['value__sum']
        except:
            # no records returned
            mined_24hr = 0

        biggest_block = query.get_mined_data(season).order_by('-value').first()
        daily_stats_sorted = stats.get_daily_stats_sorted(season, coins_dict)
        season_stats_sorted = stats.get_season_stats_sorted(season, coins_list)
        nn_social = info.get_nn_social(season)
        region_score_stats = stats.get_region_score_stats(season_stats_sorted)
        sidebar_links = helper.get_sidebar_links(season)

        context.update({
            "ntx_24hr": ntx_24hr,
            "mined_24hr": mined_24hr,
            "biggest_block": biggest_block,
            "season_stats_sorted": season_stats_sorted,
            "region_score_stats": region_score_stats,
            "show_ticker": True
        })

    context.update({
        "gets":gets,
        "server_chains": coins_dict,
        "coins_list": coins_list,
        "notaries_list": notary_list,
        "daily_stats_sorted": daily_stats_sorted,
        "nn_social": nn_social
    })
    return render(request, html, context)
    

def faucet(request):
    season = helper.get_page_season(request)
    notary_list = helper.get_notary_list(season)
    faucet_supply = {
        "RICK": 0,
        "MORTY": 0
    }
    faucet_supply_resp = requests.get(f"https://faucet.komodo.live/rm_faucet_balances").json()

    for node in faucet_supply_resp:

        try:
            faucet_supply["RICK"] += faucet_supply_resp[node]["RICK"]
            faucet_supply["MORTY"] += faucet_supply_resp[node]["MORTY"]
        except:
            pass

    pending_tx_resp = requests.get(f"https://faucet.komodo.live/show_pending_tx").json()
    pending_tx_list = []
    tx_rows = []
    pending_index = []
    if "Result" in pending_tx_resp:
        if "Message" in pending_tx_resp["Result"]:
            pending_tx_list = pending_tx_resp["Result"]["Message"]
    for item in pending_tx_list:
        tx_rows.append({
            "index": item[0],    
            "coin": item[1], 
            "address": item[2], 
            "time_sent": "n/a",   
            "amount": "n/a",  
            "txid": "n/a",
            "status": item[6]
        })
        pending_index.append(item[0])
        if len(tx_rows) >= 250:
            break
    sent_tx_resp = requests.get(f"https://faucet.komodo.live/show_faucet_db").json()
    sent_tx_list = []
    now = time.time()
    sum_24hrs = 0
    count_24hrs = 0
    if "Result" in sent_tx_resp:
        if "Message" in sent_tx_resp["Result"]:
            sent_tx_list = sent_tx_resp["Result"]["Message"]
    for item in sent_tx_list:
        if item[0] not in pending_index:
            if item[3] > SINCE_INTERVALS['day']:
                sum_24hrs += item[4]
                count_24hrs += 1
            tx_rows.append({
                "index":item[0],
                "coin":item[1],
                "address":item[2],
                "time_sent":dt.fromtimestamp(item[3]),
                "amount":item[4],
                "txid":item[5],
                "status":item[6]
            })

    context = helper.get_base_context(request)
    context.update({
        "page_title":"Rick / Morty Faucet",
        "explorers":info.get_explorers(request),
        "faucet_supply":faucet_supply,
        "count_24hrs":count_24hrs,
        "sum_24hrs":sum_24hrs,
        "tx_rows": tx_rows
    })

    if request.method == 'POST':
        if 'coin' in request.POST:
            coin = request.POST['coin'].strip()
        if 'address' in request.POST:
            address = request.POST['address'].strip()
        url = f'https://faucet.komodo.live/faucet/{coin}/{address}'
        r = requests.get(url)
        try:
            resp = r.json()
            messages.success(request, resp["Result"]["Message"])
            if resp['Status'] == "Success":
                context.update({"result":coin+"_success"})
            elif resp['Status'] == "Error":
                context.update({"result":"disqualified"})
            else:
                context.update({"result":"fail"})
        except Exception as e:
            logger.error(f"[faucet] Exception: {e}")
            messages.success(request, f"Something went wrong... {e}")
            context.update({"result":"fail"})

    return render(request, 'faucet.html', context)


def funds_sent(request):
    season = helper.get_page_season(request)
    notary_list = helper.get_notary_list(season)
    funding_data = query.get_funding_transactions_data(season).values()
    funding_totals = info.get_funding_totals(funding_data)

    context = helper.get_base_context(request)
    context.update({
        "page_title": "Funding Sent",
        "explorers": info.get_explorers(request),
        "funding_data": funding_data,
        "funding_totals": funding_totals,
    })

    return render(request, 'funding_sent.html', context)


def funding(request):
    season = helper.get_page_season(request)
    # add extra views for per chain or per notary
    low_nn_balances = helper.get_low_nn_balances()
    last_balances_update = helper.day_hr_min_sec(int(time.time()) - low_nn_balances['time'])
    human_now = time.strftime("%a, %d %b %Y %H:%M:%S", time.gmtime())

    chain_low_balance_notary_counts = {}
    notary_low_balance_chain_counts = {}

    ok_balance_notaries = []
    ok_balance_chains = []
    no_data_chains = list(low_nn_balances['sources']['failed'].keys())

    low_balance_data = low_nn_balances['low_balances']
    low_nn_balances['low_balance_chains'].sort()
    low_nn_balances['low_balance_notaries'].sort()

    notary_list = helper.get_notary_list(season)
    chain_list = info.get_dpow_coins_list(season)

    num_chains = len(chain_list)
    num_notaries = len(notary_list)
    num_addresses = num_notaries*num_chains

    # count addresses with low / sufficient balance
    num_low_balance_addresses = 0
    for notary in low_balance_data:
        for chain in low_balance_data[notary]:
            if chain in chain_list:
                num_low_balance_addresses += 1
    num_ok_balance_addresses = num_addresses-num_low_balance_addresses            

    for chain in chain_list:
        chain_low_balance_notary_counts.update({chain:0})
        if chain not in low_nn_balances['low_balance_chains'] and chain not in no_data_chains:
            ok_balance_chains.append(chain)

    for notary in notary_list:
        notary_low_balance_chain_counts.update({notary:0})
        if notary in low_balance_data:
            notary_low_balance_chain_counts.update({notary:len(low_balance_data[notary])})
            for chain in low_balance_data[notary]:
                if chain in chain_list:
                    if chain == 'KMD_3P':
                        val = chain_low_balance_notary_counts["KMD"] + 1
                        chain_low_balance_notary_counts.update({"KMD":val})
                    else:
                        val = chain_low_balance_notary_counts[chain] + 1
                        chain_low_balance_notary_counts.update({chain:val})
        if notary not in low_nn_balances['low_balance_notaries']:
            ok_balance_notaries.append(notary)

    coins_dict = helper.get_dpow_server_coins_dict(season)
    chain_balance_graph_data = helper.prepare_regional_graph_data(notary_low_balance_chain_counts)
    notary_balance_graph_data = helper.prepare_coins_graph_data(chain_low_balance_notary_counts, coins_dict)

    chains_funded_pct = round(len(ok_balance_chains)/len(chain_list)*100,2)
    notaries_funded_pct = round(len(ok_balance_notaries)/len(notary_list)*100,2)
    addresses_funded_pct = round((num_addresses-num_low_balance_addresses)/num_addresses*100,2)

    context = helper.get_base_context(request)
    context.update({
        "page_title":"Funding Info",
        "chains_funded_pct":chains_funded_pct,
        "notaries_funded_pct":notaries_funded_pct,
        "addresses_funded_pct":addresses_funded_pct,
        "num_ok_balance_addresses":num_ok_balance_addresses,
        "num_low_balance_addresses":num_low_balance_addresses,
        "num_addresses":num_addresses,
        "chain_balance_graph_data":chain_balance_graph_data,
        "notary_balance_graph_data":notary_balance_graph_data,
        "chain_low_balance_notary_counts":chain_low_balance_notary_counts,
        "notary_low_balance_chain_counts":notary_low_balance_chain_counts,
        "low_balance_notaries":low_nn_balances['low_balance_notaries'],
        "low_balance_chains":low_nn_balances['low_balance_chains'],
        "ok_balance_notaries":ok_balance_notaries,
        "ok_balance_chains":ok_balance_chains,
        "no_data_chains":no_data_chains,
        "chain_list":chain_list,
        "notaries_list":notary_list,
        "last_balances_update":last_balances_update,
        "explorers":info.get_explorers(request),
        "low_nn_balances": helper.low_nn_balances['low_balances'],
        "notary_funding": helper.get_notary_funding(),
        "bot_balance_deltas": helper.get_bot_balance_deltas()
    })
    return render(request, 'funding.html', context)


def mining_24hrs(request):
    season = helper.get_page_season(request)
    notary_list = helper.get_notary_list(season)
    mined_24hrs = info.get_mined_data_24hr().values()

    context = helper.get_base_context(request)
    context.update({
        "page_title":"KMD Mining Last 24hrs",
        "mined_24hrs":mined_24hrs,
        "explorers":info.get_explorers(request)
    })
    return render(request, 'mining_24hrs.html', context)


def mining_overview(request):
    context = helper.get_base_context(request)
    context.update({
        "page_title":f"Mining Overview",
        "explorers":info.get_explorers(request),
    })
    return render(request, 'mining_overview.html', context)


def notarised_24hrs(request):
    season = helper.get_page_season(request)
    notarised_24hrs = info.get_notarised_data_24hr(season)
    notarised_24hrs = notarised_24hrs.order_by('-block_time').values()[:200]
    
    context = helper.get_base_context(request)
    context.update({
        "page_title":"dPoW Notarisations (last 200)",
        "notarised_24hrs":notarised_24hrs,
        "explorers":info.get_explorers(request)
    })
    return render(request, 'notarised_24hrs.html', context)


def ntx_scoreboard(request):
    season = helper.get_page_season(request)
    season_stats_sorted = stats.get_season_stats_sorted(season)
    context = helper.get_base_context(request)
    context.update({
        "page_title":f"Notarisation Scoreboard",
        "season_stats_sorted":season_stats_sorted,
        "region_score_stats": stats.get_region_score_stats(season_stats_sorted),
        "nn_social": info.get_nn_social(season)
    })
    return render(request, 'ntx_scoreboard.html', context)


def ntx_scoreboard_24hrs(request):
    season = helper.get_page_season(request)
    context = helper.get_base_context(request)
    context.update({
        "page_title": f"Last 24hrs Notarisation Scoreboard",
        "daily_stats_sorted": stats.get_daily_stats_sorted(season),
        "nn_social": info.get_nn_social(season)
    })
    return render(request, 'ntx_scoreboard_24hrs.html', context)


def notary_epoch_chain_notarised_view(request):
    season = helper.get_page_season(request)
    notary = helper.get_or_none(request, "notary", random.choice(helper.get_notary_list(season)))
    server = helper.get_or_none(request, "server", "Main")
    epoch = helper.get_or_none(request, "epoch", "Epoch_0")
    chain = helper.get_or_none(request, "chain", "MORTY")

    context = helper.get_base_context(request)
    context.update({
        "notary": notary,
        "notary_clean": notary.replace("_"," "),
        "server": server,
        "server_clean": server.replace("_"," "),
        "epoch": epoch,
        "epoch_clean": epoch.replace("_"," "),
        "chain": chain,
        "season_clean": season.replace("_"," ")
    })

    return render(request, 'notary_epoch_chain_notarised.html', context)


def chain_notarised_24hrs_view(request):
    chain = helper.get_or_none(request, "chain", "MORTY")
    context = helper.get_base_context(request)
    context.update({
        "chain": chain,
    })
    return render(request, 'chain_notarised_24hrs.html', context)


def notary_chain_notarised_view(request):
    season = helper.get_page_season(request)
    notary = helper.get_or_none(request, "notary", random.choice(helper.get_notary_list(season)))
    server = helper.get_or_none(request, "server", "Main")
    chain = helper.get_or_none(request, "chain", "MORTY")

    context = helper.get_base_context(request)
    context.update({
        "server": server,
        "chain": chain,
        "notary": notary,
        "notary_clean": notary.replace("_"," "),
    })

    return render(request, 'notary_chain_notarised.html', context)


def notary_epoch_scores_view(request):
    season = helper.get_page_season(request)
    notary = helper.get_or_none(request, "notary", random.choice(helper.get_notary_list(season)))
    scoring_table, total = table.get_notary_epoch_scores_table(notary, season)
    
    context = helper.get_base_context(request)
    context.update({
        "page_title":f"dPoW Notarisation Epoch Scores",
        "notary":notary,
        "notary_clean": notary.replace("_"," "),
        "scoring_table": scoring_table,
        "total":total,
        "nn_social": info.get_nn_social(season)
    })
    return render(request, 'notary_epoch_scores_view.html', context)


def notarised_tenure_view(request):
    tenure_data = query.get_notarised_tenure_data().values()
    for item in tenure_data:
        start_time = item["official_start_block_time"]
        end_time = item["official_end_block_time"]
        now = time.time()
        if end_time > now:
            end_time = now
        ntx_days = (end_time - start_time) / 86400
        item.update({
            "ntx_days": ntx_days
        })
    context = helper.get_base_context(request)
    context.update({
        "page_title":f"Chain Notarisation Tenure",
        "tenure_data":tenure_data
    })
    return render(request, 'notarised_tenure.html', context)


def scoring_epochs_view(request):
    season = helper.get_page_season(request)
    epochs = requests.get(f"{THIS_SERVER}/api/table/scoring_epochs/?season={season}").json()['results']
    context = helper.get_base_context(request)
    context.update({
        "page_title":f"dPoW Scoring Epochs",
        "epochs":epochs
    })
    return render(request, 'scoring_epochs.html', context)
  

def testnet_ntx_scoreboard(request):
    season = "Season_5_Testnet"
    notary_list = helper.get_notary_list(season)
 
    testnet_ntx_counts = testnet.get_api_testnet(request)
    num_notaries = len(testnet_ntx_counts)

    combined_total = 0
    combined_total_24hr = 0
    for notary in testnet_ntx_counts:
        combined_total += testnet_ntx_counts[notary]["Total"]
        combined_total_24hr += testnet_ntx_counts[notary]["24hr_Total"]
    average_score = combined_total/num_notaries
    average_score_24hr = combined_total_24hr/num_notaries

    context = helper.get_base_context(request)
    context.update({
        "page_title":f"Season 5 Testnet Scoreboard",
        "average_score":average_score,
        "average_score_24hr":average_score_24hr,
        "testnet_ntx_counts":testnet_ntx_counts
    })
    return render(request, 'testnet_scoreboard.html', context)


def sitemap(request):

    context = helper.get_base_context(request)
    context.update({
        "page_title":f"Sitemap",
        "endpoints":ENDPOINTS,
        "pages":PAGES
    })

    return render(request, 'sitemap.html', context)

