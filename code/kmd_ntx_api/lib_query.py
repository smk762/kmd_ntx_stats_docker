#!/usr/bin/env python3
import os
import time
import logging
import datetime
import random
from dotenv import load_dotenv
from datetime import datetime as dt
from django.db.models import Count, Min, Max, Sum

from kmd_ntx_api.lib_const import *
from kmd_ntx_api.models import *
import kmd_ntx_api.lib_helper as helper


load_dotenv()


def get_timespan_season(start, end):
    season = SEASON
    if not start:
        start = time.time() - SINCE_INTERVALS['day']
    if not end:
        end = time.time()
    else:
        season = helper.get_season((end+start)/2)
    return int(float(start)), int(float(end)), season


def get_mm2_version_stats_data(start, end, notary):
    return mm2_version_stats.objects.filter(
        timestamp__range=(start, end), name=notary
    )

def get_nn_seed_version_scores(start, end, notary=None):
    start, end, season = get_timespan_season(start, end)
    data = mm2_version_stats.objects.filter(
        timestamp__range=(start, end-1)
    )

    if notary:
        data = data.filter(name=notary)

    data = data.order_by("-timestamp")
    helper.date_hour_notary_scores = {}

    for i in data.values():
        i["date"], i["hour"] = helper.date_hour(i["timestamp"]).split(" ")

        if i["date"] not in helper.date_hour_notary_scores:
            helper.date_hour_notary_scores.update({
                i["date"]: {
                        i["hour"]: {
                            i["name"]: {
                                "versions": [],
                                "score": i["score"]
                            }
                        }
                    }
                })

        elif i["hour"] not in helper.date_hour_notary_scores[i["date"]]:
            helper.date_hour_notary_scores[i["date"]].update({
                i["hour"]: {
                    i["name"]: {
                        "versions": [],
                        "score": i["score"]
                    }
                }
            })

        elif i["name"] not in helper.date_hour_notary_scores[i["date"]][i["hour"]]:
            helper.date_hour_notary_scores[i["date"]][i["hour"]].update({
                i["name"]: {
                    "versions": [],
                    "score": i["score"]
                }
            })
        if i["version"] not in helper.date_hour_notary_scores[i["date"]][i["hour"]][i["name"]]["versions"]:
            helper.date_hour_notary_scores[i["date"]][i["hour"]][i["name"]]["versions"].append(i["version"])

    return helper.date_hour_notary_scores


def get_nn_seed_version_scores_daily(start, end, notary=None):
    start, end, season = get_timespan_season(start, end)
    start = helper.floor_to_utc_day(start)
    end = helper.floor_to_utc_day(end)
    data = mm2_version_stats.objects.filter(
        timestamp__range=(start, end)
    )

    if notary:
        data = data.filter(name=notary)

    data = data.order_by("-timestamp")
    date_notary_scores = {}

    for i in data.values():
        i["date"], i["hour"] = helper.date_hour(i["timestamp"]).split(" ")
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
    start, end, season = get_timespan_season(start, end)
    start = helper.floor_to_utc_day(start)
    end = helper.floor_to_utc_day(end)
    data = mm2_version_stats.objects.filter(
        timestamp__range=(start, end)
    )

    if notary:
        data = data.filter(name=notary)

    data = data.order_by("-timestamp")
    date_notary_scores = {}

    for i in data.values():
        i["date"], i["hour"] = helper.date_hour(i["timestamp"]).split(" ")
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




def get_nn_seed_version_scores_daily_table(request, start=None, end=None):
    # TODO: Views for day (by hour), month (by day), season (by month)
    # Season view: click on month, goes to month view
    # Month view: click on day, goes to day view
    # TODO: Incorporate these scores into overall NN score, and profile stats.
    if not start:
        start = helper.get_or_none(request, "start")
    if not end:
        end = helper.get_or_none(request, "end")

    if not start:
        end = time.time() + SINCE_INTERVALS["day"]
        start = end - 14 * (SINCE_INTERVALS["day"])
    notary_list = helper.get_notary_list(SEASON)
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
    notary_list = helper.get_notary_list(SEASON)
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

    notary_list = helper.get_notary_list(season)

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
        
        i["date"], i["hour"] = helper.date_hour(i["timestamp"]).split(" ")
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


def get_addresses_data(season=None, server=None, coin=None, notary=None, address=None):
    data = addresses.objects.all()
    if season:
        data = data.filter(season=season)

    if server:
        data = data.filter(server=server)

    if notary:
        data = data.filter(notary=notary)

    if coin:
        data = data.filter(coin=coin)

    if address:
        data = data.filter(address=address)

    return data.order_by('-season', 'server', 'coin', 'notary')


def get_balances_data(season=None, server=None, coin=None, notary=None, address=None):
    data = balances.objects.all()
    if season:
        data = data.filter(season=season)

    if server:
        data = data.filter(server=server)

    if notary:
        data = data.filter(notary=notary)

    if coin:
        data = data.filter(coin=coin)

    if address:
        data = data.filter(address=address)

    return data.order_by('-season', 'server', 'coin', 'notary')


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


def get_coins_data(coin=None, mm2_compatible=None, dpow_active=None):
    data = coins.objects.all()
    if coin:
        data = data.filter(coin=coin)
    if mm2_compatible:
        data = data.filter(mm2_compatible=mm2_compatible)
    if dpow_active:
        data = data.filter(dpow_active=dpow_active)
    return data


def get_coin_social_data(coin=None, season=None):
    data = coin_social.objects.all()
    if coin:
        data = data.filter(coin=coin)
    if season:
        data = data.filter(season=season)
    return data


def get_funding_transactions_data(season=None, notary=None, category=None, coin=None):
    data = funding_transactions.objects.all()
    if season:
        data = data.filter(season=season)
    if notary:
        data = data.filter(notary=notary)
    if category:
        data = data.filter(category=category)
    if address:
        data = data.filter(coin=coin)
    return data


def get_notary_last_ntx_data(season=None, server=None, notary=None, coin=None):
    data = notary_last_ntx.objects.all()
    if season:
        data = data.filter(season=season)
    if server:
        data = data.filter(server=server)
    if notary:
        data = data.filter(notary=notary)
    if coin:
        data = data.filter(coin=coin)
    return data


def get_mined_count_daily_data(season=None, notary=None, mined_date=None):
    data = mined_count_daily.objects.all()
    if mined_date:
        data = data.filter(mined_date=mined_date)
    if season:
        data = data.filter(season=season)
    if notary:
        data = data.filter(notary=notary)
    return data


def get_mined_count_season_data(season=None, name=None, address=None):
    data = mined_count_season.objects.all()
    if season:
        data = data.filter(season=season)
    if name:
        data = data.filter(name=name)
    if address:
        data = data.filter(address=address)
    return data


def get_mined_data(season=None, name=None, address=None, min_block=None,
                   max_block=None, min_blocktime=None, max_blocktime=None):
    data = mined.objects.all()
    if season:
        data = data.filter(season=season)
    if name:
        data = data.filter(name=name)
    if address:
        data = data.filter(address=address)
    if min_block:
        data = data.filter(block_height__gte=min_block)
    if max_block:
        data = data.filter(block_height__lte=max_block)
    if min_blocktime:
        data = data.filter(block_time__gte=min_blocktime)
    if max_blocktime:
        data = data.filter(block_time__lte=max_blocktime)
    return data


def get_seed_version_data(season=None, name=None):
    data = mm2_version_stats.objects.all()
    if season:
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
        data = data.filter(season=season)
    if notary:
        data = data.filter(notary=notary)
    return data


def get_notarised_data(season=None, server=None, epoch=None, coin=None,
                        notary=None, address=None, txid=None, exclude_epoch=None,
                        min_blocktime=None, max_blocktime=None):
    if txid:
        data = notarised.objects.filter(txid=txid)
    else:
        data = notarised.objects.all()
    if season:
        data = data.filter(season=season)
    if server:
        data = data.filter(server=server)
    if coin:
        data = data.filter(coin=coin)
    if epoch:
        data = data.filter(epoch=epoch)
    if min_blocktime:
        data = data.filter(block_time__gte=min_blocktime)
    if max_blocktime:
        data = data.filter(block_time__lte=max_blocktime)
    if notary:
        data = data.filter(notaries__contains=[notary])
    if address:
        data = data.filter(notary_addresses__contains=[address])
    if exclude_epoch:
        data = data.exclude(epoch=exclude_epoch)
    return data


def get_notarised_coins_data(season=None, server=None, epoch=None):
    data = notarised.objects.all()
    if season:
        data = data.filter(season=season)
    if server:
        data = data.filter(server=server)
    if epoch:
        data = data.filter(epoch=epoch)
    return data


# TODO: Is this still in use?
def get_notarised_btc_data(season=None):
    data = notarised_btc.objects.all()
    if season:
        data = data.filter(season=season)
    return data


def get_notarised_coin_daily_data(notarised_date=None, coin=None):
    data = notarised_coin_daily.objects.all()
    if notarised_date:
        data = data.filter(notarised_date=notarised_date)
    if coin:
        data = data.filter(coin=coin)
    return data


def get_coin_last_ntx_data(season=None, server=None, coin=None):
    data = coin_last_ntx.objects.all()
    if season:
        data = data.filter(season=season)
    if server:
        data = data.filter(server=server)
    if coin:
        data = data.filter(coin=coin)
    return data


def get_notarised_count_daily_data(notarised_date=None, notary=None):
    data = notarised_count_daily.objects.all()
    if notarised_date:
        data = data.filter(notarised_date=notarised_date)
    if notary:
        data = data.filter(notary=notary)
    return data


def get_notary_ntx_season_data(season=None, notary=None):
    data = notary_ntx_season.objects.all()
    if season:
        data = data.filter(season=season)
    if notary:
        data = data.filter(notary=notary)
    return data


def get_coin_ntx_season_data(season=None, coin=None):
    data = coin_ntx_season.objects.all()
    if season:
        data = data.filter(season=season)
    if coin:
        data = data.filter(coin=coin)
    return data

def get_server_ntx_season_data(season=None, server=None):
    data = coin_ntx_season.objects.all()
    if season:
        data = data.filter(season=season)
    if server:
        data = data.filter(server=server)
    return data


def get_notarised_tenure_data(season=None, server=None, coin=None):
    data = notarised_tenure.objects.all()

    if season:
        data = data.filter(season=season)

    if server:
        data = data.filter(server=server)

    if coin:
        data = data.filter(coin=coin)

    return data


def get_rewards_data(season=None, address=None, min_value=None, min_block=None, max_block=None,
                     min_blocktime=None, max_blocktime=None, exclude_coinbase=True):
    data = rewards_tx.objects.all()

    if address:
        data = data.filter(input_addresses__contains=[address])

    if season:
        if season in SEASONS_INFO:
            data = data.filter(block_time__gte=SEASONS_INFO[season]["start_time"])
            data = data.filter(block_time__lte=SEASONS_INFO[season]["end_time"])

    if min_value:
        data = data.filter(rewards_value__gte=min_value)

    if min_block:
        data = data.filter(block_height__gte=min_block)

    if max_block:
        data = data.filter(block_height__lte=max_block)

    if min_blocktime:
        data = data.filter(block_time__gte=min_blocktime)

    if max_blocktime:
        data = data.filter(block_time__lte=max_blocktime)

    if exclude_coinbase:
        data = data.exclude(input_addresses__contains=['coinbase'])

    data = data.exclude(block_height=1)

    return data


def get_scoring_epochs_data(season=None, server=None, coin=None, epoch=None, timestamp=None):
    data = scoring_epochs.objects.all()

    if season:
        data = data.filter(season=season)

    if server:
        data = data.filter(server=server)

    if coin:
        data = data.filter(epoch_coins__contains=[coin])

    if epoch:
        data = data.filter(epoch=epoch)

    if timestamp:
        data = data.filter(epoch_start__lte=timestamp)
        data = data.filter(epoch_end__gte=timestamp)

    return data


def get_notary_vote_data(year=None, candidate=None, block=None, txid=None,
                      max_block=None, max_blocktime=None,
                      max_locktime=None, mined_by=None):
    data = notary_vote.objects.all()

    if year:
        data = data.filter(year=year)

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

