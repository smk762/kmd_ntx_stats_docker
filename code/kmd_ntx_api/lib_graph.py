import time
import datetime as dt
from kmd_ntx_api.lib_const import *
import kmd_ntx_api.lib_helper as helper
import kmd_ntx_api.lib_query as query
import kmd_ntx_api.lib_atomicdex as dex

GENESIS = 1479333240

def est_blocks(time):
    return (time - GENESIS) / 60

def est_mined(time):
    return est_blocks(time) * 3

def get_rewards_xy_data(request):
    data = query.get_rewards_data().order_by("block_height")
    x_axis = [1473724800000]
    y_axis = [100000000]
    cumulative = 0
    grouped = {}
    for i in data.values():
        day = dt.date(*i["block_datetime"].timetuple()[:3])
        if day not in grouped:
            grouped.update({day:0})
        grouped[day] += i["rewards_value"]

    for day in grouped:
        timestamp = int(dt.datetime(*day.timetuple()[:-4]).timestamp())
        cumulative += grouped[day]
        x_axis.append(timestamp*1000)
        y_axis.append(cumulative+100000000+est_mined(timestamp))
        
    return {
        "x": x_axis,
        "y": y_axis
    }

def get_supply_xy_data(request):
    data = query.get_kmd_supply_data().order_by("block_height")
    x_axis = [1473724800000]
    y_axis = [100000000]
    for i in data.values():
        if i["block_height"] % 1000 == 0:
            x_axis.append(i["block_time"]*1000)
            y_axis.append(i["total_supply"])
        
    return {
        "x": x_axis,
        "y": y_axis
    }


def get_mined_xy_data(request):
    data = query.get_mined_count_daily_data()
    x_axis = [1473724800000]
    y_axis = [100000000]
    cumulative = 0
    grouped = {}
    for i in data.order_by("mined_date").values():
        if i["mined_date"] not in grouped:
            grouped.update({i["mined_date"]: 0})
        grouped[i["mined_date"]] += float(i["sum_value_mined"])

    for day in grouped:
        cumulative += grouped[day]
        x_axis.append(int(dt.datetime(*day.timetuple()[:-4]).timestamp())*1000)
        y_axis.append(cumulative)
    
    return {
        "x": x_axis,
        "y": y_axis
    }


def get_balances_graph_data(request, notary=None, coin=None):

    season = helper.get_page_season(request)
    server = helper.get_page_server(request)
    coin = helper.get_or_none(request, "coin", coin)
    notary = helper.get_or_none(request, "notary", notary)

    if not season or (not notary and not coin):
        return {
            "error": "You need to specify the following filter parameter: ['season'] and either of ['notary', 'coin']"
        }

    data = query.get_balances_data(season, server, coin, notary).values()
    if server in ["KMD", "LTC", "BTC"]:
        server = "Main"

    chartLabel = ""
    labels = []
    bg_color = []
    chartdata = []
    coin_list = []
    notary_list = []
    border_color = []
    balances_dict = {}

    for item in data:
        helper.append_unique(notary_list, item['notary'])
        helper.append_unique(coin_list, item['coin'])
        helper.update_unique(balances_dict, item['coin'], {})
        helper.update_unique(balances_dict, item['notary'], {})
        helper.update_unique(balances_dict[item['notary']], item['coin'], 0)

        bal = balances_dict[item['notary']][item['coin']] + item['balance']
        balances_dict[item['notary']].update({item['coin']: bal})

    coin_list.sort()
    notary_list.sort()
    notary_list = helper.region_sort(notary_list)

    coins_dict = helper.get_dpow_server_coins_dict(season)
    main_coins = helper.get_mainnet_coins(coins_dict)
    third_coins = helper.get_third_party_coins(coins_dict)

    if len(coin_list) == 1:
        coin = coin_list[0]
        labels = notary_list
        chartLabel = coin + " Notary Balances"
        for notary in notary_list:
            if notary.endswith("_AR"):
                bg_color.append(COLORS["AR_REGION"])
            elif notary.endswith("_EU"):
                bg_color.append(COLORS["EU_REGION"])
            elif notary.endswith("_NA"):
                bg_color.append(COLORS["NA_REGION"])
            elif notary.endswith("_SH"):
                bg_color.append(COLORS["SH_REGION"])
            else:
                bg_color.append(COLORS["DEV_REGION"])
            border_color.append(COLORS["BLACK"])

    elif len(notary_list) == 1:
        notary = notary_list[0]
        labels = coin_list
        chartLabel = notary + " Notary Balances"
        for coin in coin_list:
            if coin in third_coins:
                bg_color.append(COLORS["THIRD_PARTY_COLOR"])
            elif coin in main_coins:
                bg_color.append(COLORS["MAIN_COLOR"])
            else:
                bg_color.append(COLORS["OTHER_COIN_COLOR"])
            border_color.append(COLORS["BLACK"])

    for notary in notary_list:
        for coin in coin_list:
            chartdata.append(float(balances_dict[notary][coin]))

    return {
        "labels": labels,
        "chartLabel": chartLabel,
        "chartdata": chartdata,
        "bg_color": bg_color,
        "border_color": border_color,
    }


def get_daily_ntx_graph_data(request):
    labels = []
    bg_color = []
    chartdata = []
    coin_list = []
    main_coins = []
    notary_list = []
    border_color = []
    third_coins = []
    ntx_dict = {}
    filter_kwargs = {}

    notarised_date = helper.get_or_none(request, "notarised_date")
    season = helper.get_page_season(request)
    coin = helper.get_or_none(request, "coin")
    notary = helper.get_or_none(request, "notary")

    if not notarised_date or not season or (not coin and not notary):
        return {
            "error": "You need to specify both of the following \
                      filter parameters: ['notarised_date', 'season'] \
                      and at least one of the following \
                      ['notary', 'coin']"
        }

    coins_dict = helper.get_dpow_server_coins_dict(season)
    main_coins = helper.get_mainnet_coins(coins_dict)
    third_coins = helper.get_third_party_coins(coins_dict)

    data = query.get_notarised_count_daily_data(notarised_date, notary)
    data = data.values('notary', 'notarised_date', 'coin_ntx_counts')

    for item in data:
        helper.append_unique(notary_list, item['notary'])
        coin_list += list(item['coin_ntx_counts'].keys())
        ntx_dict.update({item['notary']: item['coin_ntx_counts']})

    coin_list = helper.get_or_none(request, "coin", list(set(coin_list)))
    
    coin_list.sort()
    notary_list.sort()
    notary_list = helper.region_sort(notary_list)

    if len(coin_list) == 1:
        coin = coin_list[0]
        labels = notary_list
        chartLabel = coin + " Notarisations"
        for notary in notary_list:
            if notary.endswith("_AR"):
                bg_color.append(COLORS["AR_REGION"])
            elif notary.endswith("_EU"):
                bg_color.append(COLORS["EU_REGION"])
            elif notary.endswith("_NA"):
                bg_color.append(COLORS["NA_REGION"])
            elif notary.endswith("_SH"):
                bg_color.append(COLORS["SH_REGION"])
            else:
                bg_color.append(COLORS["DEV_REGION"])
            border_color.append(COLORS["BLACK"])

    elif len(notary_list) == 1:
        notary = notary_list[0]
        labels = coin_list
        chartLabel = notary + " Notarisations"
        for coin in coin_list:
            if coin in third_coins:
                bg_color.append(COLORS["THIRD_PARTY_COLOR"])
            elif coin in main_coins:
                bg_color.append(COLORS["MAIN_COLOR"])
            else:
                bg_color.append(COLORS["THIRD_PARTY_COLOR"])
            border_color.append(COLORS["LT_BLUE"])

    for notary in notary_list:
        for coin in coin_list:
            if coin in ntx_dict[notary]:
                chartdata.append(ntx_dict[notary][coin])
            else:
                chartdata.append(0)

    return {
        "labels": labels,
        "chartLabel": chartLabel,
        "chartdata": chartdata,
        "bg_color": bg_color,
        "border_color": border_color,
    }


def get_mm2gui_piechart(request):
    resp = {}
    # TODO: This is broken, realign wth new API output
    '''
    stats_type = ["swap_total", "swap_pct", "pubkey_total"]
    swaps_gui_stats = dex.get_swaps_gui_stats(request)
    stats = {
        "taker": swaps_gui_stats["taker"],
        "maker": swaps_gui_stats["maker"]
    }

    for side in ["taker", "maker"]:
        for x in stats_type:
            data = []
            total = 0
            axis_labels = []

            for category in stats[side]:
                if category not in stats_type:
                    print("-----------------------")
                    print(side)
                    print(category)
                    print(x)
                    print(stats[side][category][x])
                    data.append(stats[side][category][x])
                    axis_labels.append(f"{category}")
                    total += stats[side][category][x]

            base_label = " ".join([i.title() for i in x.split("_")])
            chart_label = f"{side.title()} {base_label}"

            resp.update({
                f"{side}_{x}": helper.get_chart_json(data, axis_labels, chart_label, total)
            })
    '''

    return resp
