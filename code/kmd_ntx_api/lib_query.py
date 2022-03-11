#!/usr/bin/env python3
import os
import time
import logging
import datetime
import random
from datetime import datetime as dt
from .models import *
from .lib_helper import *

from dotenv import load_dotenv
from django.db.models import Count, Min, Max, Sum
from kmd_ntx_api.serializers import *

load_dotenv()


def get_timespan_season(start, end):
    season = get_season()
    if not start:
        start = time.time() - 60*60*24
    if not end:
        end = time.time()
    else:
        season = get_season((end+start)/2)
    return int(float(start)), int(float(end)), season


def get_nn_seed_version_scores(start, end, notary=None):
    '''
    {
    "12/03/21": {
      "12:00": {
            "notary": {
                "versions": [],
                "score": 0
            },
            "notary": {
                "versions": [],
                "score": 1
            },
        }    
    }
    '''

    start, end, season = get_timespan_season(start, end)
    data = mm2_version_stats.objects.filter(
        timestamp__range=(start, end-1)
    )

    if notary:
        data = data.filter(name=notary)

    data = data.order_by("-timestamp")
    date_hour_notary_scores = {}

    for i in data.values():
        i["date"], i["hour"] = date_hour(i["timestamp"]).split(" ")

        if i["date"] not in date_hour_notary_scores:
            date_hour_notary_scores.update({
                i["date"]: {
                        i["hour"]: {
                            i["name"]: {
                                "versions": [],
                                "score": i["score"]
                            }
                        }
                    }
                })

        elif i["hour"] not in date_hour_notary_scores[i["date"]]:
            date_hour_notary_scores[i["date"]].update({
                i["hour"]: {
                    i["name"]: {
                        "versions": [],
                        "score": i["score"]
                    }
                }
            })

        elif i["name"] not in date_hour_notary_scores[i["date"]][i["hour"]]:
            date_hour_notary_scores[i["date"]][i["hour"]].update({
                i["name"]: {
                    "versions": [],
                    "score": i["score"]
                }
            })
        if i["version"] not in date_hour_notary_scores[i["date"]][i["hour"]][i["name"]]["versions"]:
            date_hour_notary_scores[i["date"]][i["hour"]][i["name"]]["versions"].append(i["version"])

    return date_hour_notary_scores



def get_nn_seed_version_scores_daily(start, end, notary=None):
    '''
    {
    "12/03/21": {
        "notary": {
            "versions": [],
            "score": 0
        },
        "notary": {
            "versions": [],
            "score": 1
        }
    }
    '''

    start, end, season = get_timespan_season(start, end)
    start = floor_to_utc_day(start)
    end = floor_to_utc_day(end)
    data = mm2_version_stats.objects.filter(
        timestamp__range=(start, end)
    )

    if notary:
        data = data.filter(name=notary)

    data = data.order_by("-timestamp")
    date_notary_scores = {}

    for i in data.values():
        i["date"], i["hour"] = date_hour(i["timestamp"]).split(" ")
        score = round(i["score"],2)
        if i["date"] not in date_notary_scores:
            date_notary_scores.update({
                i["date"]: {
                        i["name"]: {
                            "versions": [],
                            "score": score
                        }
                    }
                })

        elif i["name"] not in date_notary_scores[i["date"]]:
            date_notary_scores[i["date"]].update({
                i["name"]: {
                    "versions": [],
                    "score": score
                }
            })
        else:
            date_notary_scores[i["date"]][i["name"]]["score"] += score

        if i["version"] not in date_notary_scores[i["date"]][i["name"]]["versions"]:
            date_notary_scores[i["date"]][i["name"]]["versions"].append(i["version"])


    return date_notary_scores

def get_nn_seed_version_scores_month(start, end, notary=None):
    '''
    {
    "12/21": {
        "notary": {
            "versions": [],
            "score": 0
        },
        "notary": {
            "versions": [],
            "score": 1
        }
    }
    '''

    start, end, season = get_timespan_season(start, end)
    start = floor_to_utc_day(start)
    end = floor_to_utc_day(end)
    data = mm2_version_stats.objects.filter(
        timestamp__range=(start, end)
    )

    if notary:
        data = data.filter(name=notary)

    data = data.order_by("-timestamp")
    date_notary_scores = {}

    for i in data.values():
        i["date"], i["hour"] = date_hour(i["timestamp"]).split(" ")
        score = i["score"]
        month_day_year = i["date"].split("/")
        month_year = month_day_year[0]+"/"+month_day_year[2]
        if month_year not in date_notary_scores:
            date_notary_scores.update({
                month_year: {
                        i["name"]: {
                            "versions": [],
                            "score": score
                        }
                    }
                })

        elif i["name"] not in date_notary_scores[month_year]:
            date_notary_scores[month_year].update({
                i["name"]: {
                    "versions": [],
                    "score": score
                }
            })

        else:
            date_notary_scores[month_year][i["name"]]["score"] += score
        
        if i["version"] not in date_notary_scores[month_year][i["name"]]["versions"]:
            date_notary_scores[month_year][i["name"]]["versions"].append(i["version"])
        
    return date_notary_scores


def get_nn_seed_version_scores_hourly_table(request, start=None, end=None):
    # TODO: Views for day (by hour), month (by day), season (by month)
    # Season view: click on month, goes to month view
    # Month view: click on day, goes to day view
    # TODO: Incorporate these scores into overall NN score, and profile stats.
    if not start:
        start = get_or_none(request, "start")
    if not end:
        end = get_or_none(request, "end")

    if not start:
        start = time.time()
        end = time.time() + 24 * 60 * 60
    season = get_season()
    notary_list = get_notary_list(season)
    date_hour_notary_scores = get_nn_seed_version_scores(start, end)
    
    table_headers = ["Total"]
    table_data = []
    notary_scores = {}

    for notary in notary_list:
        notary_scores.update({notary:[]})

    for date in date_hour_notary_scores:
        for hour in date_hour_notary_scores[date]:
            table_headers.append(f"{hour.split(':')[0]}")
            for notary in notary_list:
                if notary in date_hour_notary_scores[date][hour]:
                    score = round(date_hour_notary_scores[date][hour][notary]["score"],2)
                else:
                    score = 0
                notary_scores[notary].append(score)

    table_headers.append("Notary")
    table_headers.reverse()
    # Get total for timespan
    for notary in notary_scores:
        notary_scores[notary].reverse()
        total = round(sum(notary_scores[notary]),2)
        notary_scores[notary].append(total)

    return {
        "headers": table_headers,
        "scores": notary_scores
        }

def get_nn_seed_version_scores_daily_table(request, start=None, end=None):
    # TODO: Views for day (by hour), month (by day), season (by month)
    # Season view: click on month, goes to month view
    # Month view: click on day, goes to day view
    # TODO: Incorporate these scores into overall NN score, and profile stats.
    if not start:
        start = get_or_none(request, "start")
    if not end:
        end = get_or_none(request, "end")

    if not start:
        end = time.time() + 24 * 60 * 60
        start = end - 14 * (24 * 60 * 60)
    season = get_season()
    notary_list = get_notary_list(season)
    date_notary_scores = get_nn_seed_version_scores_daily(start, end)
    
    table_headers = ["Total"]
    table_data = []
    notary_scores = {}

    for notary in notary_list:
        notary_scores.update({notary:[]})

    for date in date_notary_scores:
        table_headers.append(f"{date}")
        for notary in notary_list:
            if notary in date_notary_scores[date]:
                score = round(date_notary_scores[date][notary]["score"],2)
            else:
                score = 0
            notary_scores[notary].append(score)

    table_headers.append("Notary")
    table_headers.reverse()
    # Get total for timespan
    for notary in notary_scores:
        notary_scores[notary].reverse()
        total = round(sum(notary_scores[notary]),2)
        notary_scores[notary].append(total)

    return {
        "headers": table_headers,
        "scores": notary_scores
        }

def get_nn_seed_version_scores_month_table(request, start=None, end=None):
    # TODO: Views for day (by hour), month (by day), season (by month)
    # Season view: click on month, goes to month view
    # Month view: click on day, goes to day view
    # TODO: Incorporate these scores into overall NN score, and profile stats.
    season = get_season()
    notary_list = get_notary_list(season)
    month_notary_scores = get_nn_seed_version_scores_month(start, end)
    
    table_headers = ["Total"]
    table_data = []
    notary_scores = {}

    for notary in notary_list:
        notary_scores.update({notary:[]})

    for date in month_notary_scores:
        table_headers.append(f"{date}")
        for notary in notary_list:
            if notary in month_notary_scores[date]:
                score = round(month_notary_scores[date][notary]["score"],2)
            else:
                score = 0
            notary_scores[notary].append(score)

    table_headers.append("Notary")
    table_headers.reverse()
    # Get total for timespan
    for notary in notary_scores:
        notary_scores[notary].reverse()
        total = round(sum(notary_scores[notary]),2)
        notary_scores[notary].append(total)

    return {
        "headers": table_headers,
        "scores": notary_scores
        }



def get_nn_mm2_stats_by_hour_chart_data(start, end, notary=None):
    start, end, season = get_timespan_season(start, end)
    stats = get_nn_mm2_stats_by_hour_data(start, end, notary)
    ts_dict = stats["ts_dict"]
    # Chartify
    # need to setup something to populate this via the dpow repo.
    valid_versions = [
        "2.1.4401_mm2.1_87837cb54_Linux_Release"
    ]
    colors_dict = {}

    notary_list = get_notary_list(season)

    for notary in notary_list:
        colors_dict.update({notary:[]})

    hours_list = []
    dates_list = []
    valid_cell_color = '#00cf6677'
    invalid_cell_color = '#ffa00099'
    no_data_cell_color = '#FFFFFF11'
    for date in ts_dict:
        dates_list.append(date)
        for hour in ts_dict[date]:
            hours_list.append(date+" "+hour)
            for notary in notary_list:
                color = no_data_cell_color
                for version in ts_dict[date][hour]:
                    if version in valid_versions:
                        if notary in ts_dict[date][hour][version]:
                            color = valid_cell_color
                            break
                    else:
                        if notary in ts_dict[date][hour][version]:
                            color = invalid_cell_color
                            break

                colors_dict[notary].append(color)

    chart_data = {
        "dates_list": dates_list,
        "hours_list": hours_list,
        "colors_dict": colors_dict
    }
    return {
        "chart_data": chart_data
    }


def get_nn_mm2_stats_by_hour_data(start, end, notary=None):
    start, end, season = get_timespan_season(start, end)

    data = mm2_version_stats.objects.filter(
        timestamp__range=(start, end)
    )
    if notary:
        data = data.filter(name=notary)
    data = data.order_by("-timestamp")

    ts_dict = {}
    nn_dict = {}
    rows = []
    for i in data.values():
        
        i["date"], i["hour"] = date_hour(i["timestamp"]).split(" ")
        rows.append(i)

        if i["date"] not in ts_dict:
            ts_dict.update({i["date"]:{}})
        if i["hour"] not in ts_dict[i["date"]]:
            ts_dict[i["date"]].update({i["hour"]:{}})
        if i["version"] not in ts_dict[i["date"]][i["hour"]]:
            ts_dict[i["date"]][i["hour"]].update({i["version"]:[]})
        if i["name"] not in ts_dict[i["date"]][i["hour"]][i["version"]]:
            ts_dict[i["date"]][i["hour"]][i["version"]].append(i["name"])
        

        if i["name"] not in nn_dict:
            nn_dict.update({i["name"]:{}})

        if i["date"] not in nn_dict[i["name"]]:
            nn_dict[i["name"]].update({i["date"]:{}})

        if i["hour"] not in nn_dict[i["name"]][i["date"]]:
            nn_dict[i["name"]][i["date"]].update({i["hour"]:[]})

        if i["version"] not in nn_dict[i["name"]][i["date"]][i["hour"]]:
            nn_dict[i["name"]][i["date"]][i["hour"]].append(i["version"])


    resp = {
        "ts_dict":ts_dict,
        "nn_dict":nn_dict,
        "rows":rows
    }
    return resp

def get_addresses_data(season=None, server=None, chain=None, notary=None, address=None):
    data = addresses.objects.all()
    if season:
        season = season.title()
        data = data.filter(season=season)

    if server:
        data = data.filter(server=server)

    if notary:
        data = data.filter(notary=notary)

    if chain:
        data = data.filter(chain=chain)

    if address:
        data = data.filter(address=address)

    return data.order_by('-season', 'server', 'chain', 'notary')


def get_balances_data(season=None, server=None, chain=None, notary=None, address=None):
    data = balances.objects.all()
    if season:
        season = season.title()
        data = data.filter(season=season)

    if server:
        data = data.filter(server=server)

    if notary:
        data = data.filter(notary=notary)

    if chain:
        data = data.filter(chain=chain)
    if address:
        data = data.filter(address=address)

    return data.order_by('-season', 'server', 'chain', 'notary')

def get_nn_mm2_stats_data(name=None, version=None, limit=None):
    data = mm2_version_stats.objects.all()
    if name:
        data = data.filter(name=name)
    if version:
        data = data.filter(version=version)
    data = data.order_by("-timestamp")
    if limit:
        data = data[:limit]
    return data

# TODO: Awaiting delegation to crons / db table
def get_chain_sync_data(chain=None):
    data = chain_sync.objects.all()
    if chain:
        data = data.filter(chain=chain)
    return data


def get_coins_data(chain=None, mm2_compatible=None, dpow_active=None):
    data = coins.objects.all()
    if chain:
        data = data.filter(chain=chain)
    if mm2_compatible:
        data = data.filter(mm2_compatible=mm2_compatible)
    if dpow_active:
        data = data.filter(dpow_active=dpow_active)
    return data


def get_coin_social_data(chain=None):
    data = coin_social.objects.all()
    if chain:
        data = data.filter(chain=chain)
    return data


def get_funding_transactions_data(season=None, notary=None, category=None, chain=None):
    data = funding_transactions.objects.all()
    if season:
        season = season.title()
        data = data.filter(season=season)
    if notary:
        data = data.filter(notary=notary)
    if category:
        data = data.filter(category=category)
    if address:
        data = data.filter(chain=chain)
    return data


def get_last_notarised_data(season=None, server=None, notary=None, chain=None):
    data = last_notarised.objects.all()
    if season:
        season = season.title()
        data = data.filter(season=season)
    if server:
        data = data.filter(server=server)
    if notary:
        data = data.filter(notary=notary)
    if chain:
        data = data.filter(chain=chain)
    return data


def get_mined_count_daily_data(season=None, notary=None, mined_date=None):
    data = mined_count_daily.objects.all()
    if mined_date:
        data = data.filter(mined_date=mined_date)
    if season:
        season = season.title()
        data = data.filter(season=season)
    if notary:
        data = data.filter(notary=notary)
    return data


def get_mined_count_season_data(season=None, name=None, address=None):
    data = mined_count_season.objects.all()
    if season:
        season = season.title()
        data = data.filter(season=season)
    if name:
        data = data.filter(name=name)
    if address:
        data = data.filter(address=address)
    return data


def get_mined_data(season=None, name=None, address=None):
    data = mined.objects.all()
    if season:
        season = season.title()
        data = data.filter(season=season)
    if name:
        data = data.filter(name=name)
    if address:
        data = data.filter(address=address)
    data = data.order_by('block_height')
    return data

def get_seed_version_data(season=None, name=None):
    data = mm2_version_stats.objects.all()
    if season:
        season = season.title()
        data = data.filter(season=season)
    if name:
        data = data.filter(name=name)
    return data


def get_nn_btc_tx_data(season=None, notary=None, category=None, address=None, txid=None):
    if txid:
        data = nn_btc_tx.objects.filter(txid=txid)
    else:
        data = nn_btc_tx.objects.all()
    if season:
        season = season.title()
        data = data.filter(season=season)
    if notary:
        data = data.filter(notary=notary)
    if category:
        data = data.filter(category=category)
    if address:
        data = data.filter(address=address)
    return data


def get_nn_ltc_tx_data(season=None, notary=None, category=None, address=None, txid=None):
    if txid:
        data = nn_ltc_tx.objects.filter(txid=txid)
    else:
        data = nn_ltc_tx.objects.all()
    if season:
        season = season.title()
        data = data.filter(season=season)
    if notary:
        data = data.filter(notary=notary)
    if category:
        data = data.filter(category=category)
    if address:
        data = data.filter(address=address)
    return data


def get_nn_social_data(season=None, notary=None):
    data = nn_social.objects.all()
    if season:
        season = season.title()
        data = data.filter(season=season)
    if notary:
        data = data.filter(notary=notary)
    return data


def get_notarised_data(season=None, server=None, epoch=None, chain=None, notary=None, address=None, txid=None):
    if txid:
        data = notarised.objects.filter(txid=txid)
    else:
        data = notarised.objects.exclude(season="Season_1").exclude(
            season="Season_2").exclude(season="Season_3")
    if season:
        season = season.title()
        data = data.filter(season=season)
    if server:
        data = data.filter(server=server)
    if chain:
        data = data.filter(chain=chain)
    if epoch:
        data = data.filter(epoch=epoch)
    if notary:
        data = data.filter(notaries__contains=[notary])
    if address:
        data = data.filter(notary_addresses__contains=[address])
    return data


# TODO: Is this still in use?
def get_notarised_btc_data(season=None):
    data = notarised_btc.objects.all()
    if season:
        season = season.title()
        data = data.filter(season=season)
    return data


def get_notarised_chain_daily_data(notarised_date=None, chain=None):
    data = notarised_chain_daily.objects.all()
    if notarised_date:
        data = data.filter(notarised_date=notarised_date)
    if chain:
        data = data.filter(chain=chain)
    return data


def get_notarised_chain_season_data(season=None, server=None, chain=None):
    data = notarised_chain_season.objects.all()
    if season:
        season = season.title()
        data = data.filter(season=season)
    if server:
        data = data.filter(server=server)
    if chain:
        data = data.filter(chain=chain)
    return data


def get_notarised_count_daily_data(notarised_date=None, notary=None):
    data = notarised_count_daily.objects.all()
    if notarised_date:
        data = data.filter(notarised_date=notarised_date)
    if notary:
        data = data.filter(notary=notary)
    return data


def get_notarised_count_season_data(season=None, notary=None):
    data = notarised_count_season.objects.all()
    if season:
        season = season.title()
        data = data.filter(season=season)
    if notary:
        data = data.filter(notary=notary)
    return data


def get_notarised_tenure_data(season=None, server=None, chain=None):
    data = notarised_tenure.objects.all()

    if season:
        season = season.title()
        data = data.filter(season=season)

    if server:
        data = data.filter(server=server)

    if chain:
        data = data.filter(chain=chain)

    return data


def get_rewards_data(notary=None):
    data = rewards.objects.all()

    if notary:
        data = data.filter(notary=notary)

    return data


def get_scoring_epochs_data(season=None, server=None, chain=None, epoch=None, timestamp=None):
    data = scoring_epochs.objects.all()

    if season:
        season = season.title()
        data = data.filter(season=season)

    if server:
        data = data.filter(server=server)

    if chain:
        data = data.filter(epoch_chains__contains=[chain])

    if epoch:
        data = data.filter(epoch=epoch)

    if timestamp:
        data = data.filter(epoch_start__lte=timestamp)
        data = data.filter(epoch_end__gte=timestamp)

    return data


def get_vote2021_data(candidate=None, block=None, txid=None,
                      max_block=None, max_blocktime=None,
                      max_locktime=None, mined_by=None):
    data = vote2021.objects.all()

    if candidate:
        data = data.filter(candidate=candidate)

    if block:
        data = data.filter(block=block)

    if txid:
        data = data.filter(txid=txid)

    if mined_by:
        data = data.filter(mined_by=mined_by)

    if max_block:
        data = data.filter(block_height__lte=max_block)

    if max_blocktime:
        data = data.filter(block_time__lte=max_blocktime)

    if max_locktime:
        data = data.filter(lock_time__lte=max_locktime)

    return data


def get_swaps_failed_data(uuid=None):
    data = swaps_failed.objects.all()
    if uuid:
        data = data.filter(uuid=uuid)
    return data


def get_swaps_data(uuid=None):
    data = swaps.objects.all()
    if uuid:
        data = data.filter(uuid=uuid)
    return data


def get_swaps_counts(swaps_data):
    q_pairs_counts = swaps_data.values('maker_coin', 'taker_coin').annotate(
        count=Count('taker_coin')
    )

    q_pairs_volumes = swaps_data.values('maker_coin', 'taker_coin').annotate(
        swap_count=Count('maker_coin'),
        maker_amount=Sum('maker_amount'),
        taker_amount=Sum('taker_amount')
    )
    q_maker_guis = swaps_data.values(
        'maker_gui').annotate(count=Count('maker_gui'))
    q_taker_guis = swaps_data.values(
        'taker_gui').annotate(count=Count('taker_gui'))

    guis = {}

    for i in q_taker_guis:
        guis.update(
            {
                i["taker_gui"]: {
                    "taker_swaps": i["count"],
                    "maker_swaps": 0
                }
            }
        )

    for i in q_maker_guis:
        if i["maker_gui"] not in guis:
            guis.update(
                {
                    i["maker_gui"]: {
                        "maker_swaps": i["count"],
                        "taker_swaps": 0
                    }
                }
            )
        else:
            guis[i["maker_gui"]].update({"maker_swaps": i["count"]})

    pair_counts = [
        {"maker": i['maker_coin'], "taker":i['taker_coin'], "count":i['count']}
        for i in q_pairs_counts  # if i["count"] >= 10
    ]

    pair_volumes = [
        {
            "maker": i['maker_coin'],
            "taker":i['taker_coin'],
            "swap_count":i['swap_count'],
            "maker_volume":i['maker_amount'],
            "taker_volume":i['taker_amount']
        }
        for i in q_pairs_volumes  # if i["count"] >= 10
    ]

    return {
        "pair_volumes": pair_volumes,
        "pair_counts": pair_counts,
        "guis": guis
    }


def filter_swaps_coins(data, taker_coin=None, maker_coin=None):
    if taker_coin:
        data = data.filter(taker_coin=taker_coin)
    if maker_coin:
        data = data.filter(maker_coin=maker_coin)
    return data


def filter_swaps_gui(data, taker_gui=None, maker_gui=None):
    if taker_gui:
        data = data.filter(taker_gui=taker_gui)
    if maker_gui:
        data = data.filter(maker_gui=maker_gui)
    return data


def filter_swaps_version(data, taker_version=None, maker_version=None):
    if taker_version:
        data = data.filter(taker_version=taker_version)
    if maker_version:
        data = data.filter(maker_version=maker_version)
    return data


def filter_swaps_pubkey(data, taker_pubkey=None, maker_pubkey=None):
    if taker_pubkey:
        data = data.filter(taker_pubkey=taker_pubkey)
    if maker_pubkey:
        data = data.filter(maker_pubkey=maker_pubkey)
    return data


def filter_swaps_error(data, taker_error_type=None, maker_error_type=None):
    if taker_error_type:
        data = data.filter(taker_error_type=taker_error_type)
    if maker_error_type:
        data = data.filter(maker_error_type=maker_error_type)
    return data


def filter_swaps_timespan(data, from_time=None, to_time=None):
    if from_time:
        data = data.filter(time_stamp__gte=from_time)
    if to_time:
        data = data.filter(time_stamp__lte=to_time)
    return data
