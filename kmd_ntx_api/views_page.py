#!/usr/bin/env python3

import time
import random
import numpy as np
from django.shortcuts import render
from kmd_ntx_api.pages import *
from kmd_ntx_api.endpoints import *
from kmd_ntx_api.lib_stats import *
from kmd_ntx_api.api_table import *
from kmd_ntx_api.lib_testnet import *


## DASHBOARD        

def chains_last_ntx(request):
    season = SEASON
    notary_list = get_notary_list(season)

    season_chain_ntx_data = get_season_chain_ntx_data(season)

    context = {
        "page_title":"dPoW Last Chain Notarisations",
        "sidebar_links":get_sidebar_links(season),
        "eco_data_link":get_eco_data_link(),
        "explorers":get_explorers(request),
        "season_chain_ntx_data":season_chain_ntx_data
    }

    return render(request, 'last_notarised.html', context)


# TODO: Awaiting delegation to crons / db table
def chain_sync(request):
    season = SEASON
    context = get_chain_sync_data(request)

    context.update({
        "page_title":"Chain Sync",
        "sidebar_links":get_sidebar_links(season),
        "explorers":get_explorers(request),
        "eco_data_link":get_eco_data_link()
        })
    return render(request, 'chain_sync.html', context)

def coin_profile_view(request, chain=None): # TODO: REVIEW and ALIGN with NOTARY PROFILE
    season = SEASON
    server = get_chain_server(chain)

    context = {
        "page_title":"Coin Profile Index",
        "sidebar_links":get_sidebar_links(season),
        "eco_data_link":get_eco_data_link()
    }
    
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

        coin_notariser_ranks = get_coin_notariser_ranks(season)
        top_region_notarisers = get_top_region_notarisers(coin_notariser_ranks)
        top_coin_notarisers = get_top_coin_notarisers(top_region_notarisers, chain)
        chain_ntx_summary = get_coin_ntx_summary(chain)
        season_chain_ntx_data = get_season_chain_ntx_data(season)

        context.update({
            "page_title": f"{chain} Profile",
            "season":season,
            "server":server,
            "chain":chain,
            "coins_data":coins_data,
            "chain_balances":chain_balances,
            "explorers":get_explorers(request),
            "eco_data_link":get_eco_data_link(),
            "max_tick": max_tick,
            "coin_social": get_coin_social(chain),
            "chain_ntx_summary": chain_ntx_summary,
            "top_coin_notarisers":top_coin_notarisers
        })            

        return render(request, 'coin_profile.html', context)
    else:
        context.update({ 
            "coin_social": get_coin_social(),
            "server_coins": get_dpow_server_coins_dict()
        })
        return render(request, 'coin_profile_index.html', context)


def dash_view(request, dash_name=None):
    # Table Views
    context = {
        "page_title":"Index"
        }
    gets = ''
    html = 'dash_index.html'

    if "season" in request.GET:
        season = request.GET["season"]
        
    else:
        season = SEASON

    notary_list = get_notary_list(season)
    coins_list = get_dpow_coins_list(season)
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
        coin_notariser_ranks = get_coin_notariser_ranks(season)
        ntx_24hr = get_notarised_data().filter(
            block_time__gt=str(int(time.time()-24*60*60))
            ).count()
        try:
            mined_24hr = get_mined_data_24hr().values('season').annotate(sum_mined=Sum('value'))[0]['sum_mined']
        except:
            # no records returned
            mined_24hr = 0
        biggest_block = get_mined_data(season).order_by('-value').first()
        
        notarisation_scores = get_notarisation_scores(season)
        
        region_score_stats = get_region_score_stats(notarisation_scores)
        context.update({
            "ntx_24hr":ntx_24hr,
            "mined_24hr":mined_24hr,
            "biggest_block":biggest_block,
            "notarisation_scores":notarisation_scores,
            "region_score_stats":region_score_stats,
            "show_ticker":True
        })

    server_chains = get_dpow_server_coins_dict(season)
    context.update({
        "gets":gets,
        "sidebar_links":get_sidebar_links(season),
        "eco_data_link":get_eco_data_link(),
        "server_chains":server_chains,
        "coins_list":coins_list,
        "notaries_list":notary_list,
        "daily_stats_sorted":get_daily_stats_sorted(notary_list),
        "nn_social":get_nn_social(),

    })
    return render(request, html, context)
    

def faucet(request):
    season = SEASON
    notary_list = get_notary_list(season)
    context = {
        "page_title":"Rick / Morty Faucet",
        "sidebar_links":get_sidebar_links(season),
        "explorers":get_explorers(request),
        "eco_data_link":get_eco_data_link()
        }
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
    season = SEASON
    notary_list = get_notary_list(season)
    funding_data = get_funding_transactions_data(season).values()
    funding_totals = get_funding_totals(funding_data)

    context = {
        "page_title":"Funding Sent",
        "sidebar_links":get_sidebar_links(season),
        "explorers":get_explorers(request),
        "eco_data_link":get_eco_data_link(),
        "funding_data":funding_data,
        "funding_totals":funding_totals,
    }  
    return render(request, 'funding_sent.html', context)


def funding(request):
    # add extra views for per chain or per notary
    low_nn_balances = get_low_nn_balances()
    last_balances_update = day_hr_min_sec(int(time.time()) - low_nn_balances['time'])
    human_now = time.strftime("%a, %d %b %Y %H:%M:%S", time.gmtime())

    chain_low_balance_notary_counts = {}
    notary_low_balance_chain_counts = {}

    ok_balance_notaries = []
    ok_balance_chains = []
    no_data_chains = list(low_nn_balances['sources']['failed'].keys())

    low_balance_data = low_nn_balances['low_balances']
    low_nn_balances['low_balance_chains'].sort()
    low_nn_balances['low_balance_notaries'].sort()

    season = SEASON
    notary_list = get_notary_list(season)

    chain_list = get_dpow_coins_list(season)

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

    coins_dict = get_dpow_server_coins_dict(season)
    chain_balance_graph_data = prepare_regional_graph_data(notary_low_balance_chain_counts)
    notary_balance_graph_data = prepare_coins_graph_data(chain_low_balance_notary_counts, coins_dict)

    chains_funded_pct = round(len(ok_balance_chains)/len(chain_list)*100,2)
    notaries_funded_pct = round(len(ok_balance_notaries)/len(notary_list)*100,2)
    addresses_funded_pct = round((num_addresses-num_low_balance_addresses)/num_addresses*100,2)

    context = {
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
        "sidebar_links":get_sidebar_links(season),
        "explorers":get_explorers(request),
        "low_nn_balances":low_nn_balances['low_balances'],
        "notary_funding":get_notary_funding(),
        "bot_balance_deltas":get_bot_balance_deltas(),
        "eco_data_link":get_eco_data_link()
    }
    return render(request, 'funding.html', context)


def mining_24hrs(request):
    season = SEASON
    notary_list = get_notary_list(season)
    mined_24hrs = get_mined_data_24hr().values()

    context = {
        "page_title":"KMD Mining Last 24hrs",
        "sidebar_links":get_sidebar_links(season),
        "eco_data_link":get_eco_data_link(),
        "mined_24hrs":mined_24hrs,
        "explorers":get_explorers(request),
        "season":season.replace("_"," ")
    }
    return render(request, 'mining_24hrs.html', context)


def mining_overview(request):
    season = SEASON
    mined_season = requests.get(f"{THIS_SERVER}/api/table/mined_count_season/?season={season}").json()['results']
    context = {
        "page_title":f"{season.replace('_',' ')} Mining Overview",
        "sidebar_links":get_sidebar_links(season),
        "eco_data_link":get_eco_data_link(),
        "explorers":get_explorers(request),
        "mined_season":mined_season,
        "season":season.replace("_"," ")
    }
    return render(request, 'mining_overview.html', context)


def notarised_24hrs(request):
    season = SEASON
    notarised_24hrs = get_notarised_data_24hr()
    print(f"notarised_24hrs.count(): {notarised_24hrs.count()}")
    notarised_24hrs = notarised_24hrs.order_by('-block_time').values()[:200]
    

    context = {
        "page_title":"dPoW Notarisations (last 200)",
        "sidebar_links":get_sidebar_links(season),
        "eco_data_link":get_eco_data_link(),
        "notarised_24hrs":notarised_24hrs,
        "explorers":get_explorers(request),
        "season":season.replace("_"," ")
    }
    return render(request, 'notarised_24hrs.html', context)


def ntx_scoreboard(request):
    if not "season" in request.GET:
        season = SEASON
    else:
        season = request.GET["season"]

    notarisation_scores = get_notarisation_scores(season)

    context = {
        "page_title":f"{season.replace('_',' ')} Notarisation Scoreboard",
        "sidebar_links":get_sidebar_links(season),
        "eco_data_link":get_eco_data_link(),
        "notarisation_scores":notarisation_scores,
        "region_score_stats":get_region_score_stats(notarisation_scores),
        "nn_social":get_nn_social()
    }
    return render(request, 'ntx_scoreboard.html', context)


def ntx_scoreboard_24hrs(request):
    if not "season" in request.GET:
        season = SEASON
    else:
        season = request.GET["season"]
    context = {
        "page_title":f"{season.replace('_',' ')} Last 24hrs Notarisation Scoreboard",
        "daily_stats_sorted":get_daily_stats_sorted(),
        "sidebar_links":get_sidebar_links(season),
        "eco_data_link":get_eco_data_link(),
        "nn_social":get_nn_social()
    }
    return render(request, 'ntx_scoreboard_24hrs.html', context)


def notary_epoch_scores_view(request):
    if not "season" in request.GET:
        season = SEASON
    else:
        season = request.GET["season"]

    notary_list = get_notary_list(season)
    if not "notary" in request.GET:
        notary = random.choice(notary_list)
    else:
        notary = request.GET["notary"]

    scoring_table, total = get_notary_epoch_scores_table(notary, season)
    

    context = {
        "page_title":f"{season.replace('_',' ')} dPoW Notarisation Epoch Scores",
        "sidebar_links":get_sidebar_links(season),
        "eco_data_link":get_eco_data_link(),
        "notary":notary,
        "season":season,
        "scoring_table":scoring_table,
        "total":total,
        "nn_social":get_nn_social()
    }
    return render(request, 'notary_epoch_scores_view.html', context)


def notarised_tenure_view(request):
    season = SEASON
    notary_list = get_notary_list(season)
    tenure_data = get_notarised_tenure_data().values()
    context = {
        "page_title":f"{season.replace('_',' ')} Chain Notarisation Tenure",
        "sidebar_links":get_sidebar_links(season),
        "tenure_data":tenure_data,
        "eco_data_link":get_eco_data_link()
    }
    return render(request, 'notarised_tenure.html', context)


def scoring_epochs_view(request):
    season = SEASON
    notary_list = get_notary_list(season)
    epochs = requests.get(f"{THIS_SERVER}/api/table/scoring_epochs/?season={season}").json()['results']
    context = {
        "page_title":f"{season.replace('_',' ')} dPoW Scoring Epochs",
        "sidebar_links":get_sidebar_links(season),
        "epochs":epochs,
        "eco_data_link":get_eco_data_link()
    }
    return render(request, 'scoring_epochs.html', context)
  

def testnet_ntx_scoreboard(request):
    season = "Season_5_Testnet"
    notary_list = get_notary_list(season)
 
    testnet_ntx_counts = get_api_testnet(request)
    num_notaries = len(testnet_ntx_counts)

    combined_total = 0
    combined_total_24hr = 0
    for notary in testnet_ntx_counts:
        combined_total += testnet_ntx_counts[notary]["Total"]
        combined_total_24hr += testnet_ntx_counts[notary]["24hr_Total"]
    average_score = combined_total/num_notaries
    average_score_24hr = combined_total_24hr/num_notaries

    context = {
        "page_title":f"Season 5 Testnet Scoreboard",
        "sidebar_links":get_sidebar_links(season),
        "eco_data_link":get_eco_data_link(),
        "average_score":average_score,
        "average_score_24hr":average_score_24hr,
        "testnet_ntx_counts":testnet_ntx_counts
    }
    return render(request, 'testnet_scoreboard.html', context)


def sitemap(request):

    context = {
        "page_title":f"Sitemap",
        "endpoints":ENDPOINTS,
        "pages":PAGES
    }
    return render(request, 'sitemap.html', context)

