#!/usr/bin/env python3
import math
import requests
from django.shortcuts import render

from datetime import datetime as dt

from kmd_ntx_api.lib_const import *
import kmd_ntx_api.lib_helper as helper
import kmd_ntx_api.lib_query as query
import kmd_ntx_api.lib_info as info
import kmd_ntx_api.lib_atomicdex as dex
import kmd_ntx_api.api_atomicdex as dex_api
import kmd_ntx_api.forms as forms



def activation_commands_view(request):
    context = helper.get_base_context(request)

    activation_data = {}
    url = f"{context['scheme_host']}api/atomicdex/activation_commands/"
    data = requests.get(url).json()["commands"]
    for protocol in data:
        if len(data[protocol]) != 0:
            activation_data.update({protocol:data[protocol]})

    context.update({
        "page_title": "Generate AtomicDEX-API Enable Command",
        "activation_data": activation_data
    })

    return render(request, 'views/atomicdex/activation_commands.html', context)


def batch_activation_form_view(request):
    context = helper.get_base_context(request)
    context.update({
        "page_title":"Generate AtomicDEX-API Batch Activation Commands",
    })

    if request.GET:
        try:
            coin = request.GET["coin"]
            form = forms.EnableCommandForm(request.GET)
            context.update({
                "form":form
            })

            url = f"{context['scheme_host']}api/atomicdex/activation_commands"
            r = requests.get(f'{url}/?coin={coin}')
            command_str = r.json()
            command_str["userpass"] = "'$userpass'"
            form_resp = [command_str]

            try:
                if request.GET['add_to_batch_command'] == "True":
                    if len(request.GET['existing_command']) > 0:
                        command_str = request.GET['existing_command']
                        command_str = command_str.replace("'$userpass'", "$userpass")
                        command_str = command_str.replace("\'", "\"")
                        command_str = command_str.replace("True", "true")
                        command_str = command_str.replace("False", "false")
                        existing_commands = json.loads(command_str)
                        for i in existing_commands:
                            if i["coin"] != coin:
                                i['userpass'] = "'$userpass'"
                                form_resp.append(i)

            except Exception as e:
                messages.error(request, e)

            context.update({
                "form_resp":form_resp
            })
            return render(request, 'views/atomicdex/batch_activation_form.html', context)

        except Exception as e:
            print(e)
        
    form = forms.EnableCommandForm() 
    context.update({
        "form":form
    })

    return render(request, 'views/atomicdex/batch_activation_form.html', context)


def bestorders_view(request):
    context = helper.get_base_context(request)
    coin = helper.get_or_none(request, "coin", "KMD")
    context.update({
        "coin": coin,
        "mm2_coins": info.get_mm2_coins_list()
    })

    rows = []
    bestorders = dex.get_bestorders(request)["result"]
    for _coin in bestorders:
        rows.append({
            "coin": _coin,
            "price": bestorders[_coin][0]["price"],
            "maxvolume": bestorders[_coin][0]["maxvolume"],
            "min_volume": bestorders[_coin][0]["min_volume"],
        })

    context.update({
        "bestorders": rows
    })

    return render(request, 'views/atomicdex/bestorders.html', context)


def gui_stats_view(request):
    context = helper.get_base_context(request)
    since = helper.get_or_none(request, "since", "week")
    to_time = helper.get_or_none(request, "to_time", int(time.time()))
    from_time = helper.get_or_none(request, "from_time", int(to_time - SINCE_INTERVALS[since]))
    swaps_data = query.get_swaps_data()
    swaps_data = query.filter_swaps_timespan(swaps_data, from_time, to_time)

    context.update({
        "since": since,
        "since_options": list(SINCE_INTERVALS.keys()),
        "from_time": from_time,
        "from_time_dt": dt.fromtimestamp(from_time),
        "to_time": to_time,
        "to_time_dt": dt.fromtimestamp(to_time),
        "swaps_counts": query.get_swaps_counts(swaps_data)
    })

    return render(request, 'views/atomicdex/gui_stats.html', context)


def last_200_swaps_view(request):
    context = helper.get_base_context(request)
    last_200_swaps = dex.get_last_200_swaps(request)
    last_200_swaps = dex.format_gui_os_version(last_200_swaps)

    context.update({
        "last_200_swaps": last_200_swaps,
        "mm2_coins": info.get_mm2_coins_list(),
        "taker_coin": helper.get_or_none(request, "taker_coin"),
        "maker_coin": helper.get_or_none(request, "maker_coin"),
        "page_title": "Last 200 Swaps"
    })

    return render(request, 'views/atomicdex/last_200_swaps.html', context)


def last_200_failed_swaps_view(request):
    context = helper.get_base_context(request)
    last_200_failed_swaps = dex.get_last_200_failed_swaps(request)
    last_200_failed_swaps = dex.format_gui_os_version(last_200_failed_swaps)

    context.update({
        "last_200_failed_swaps": last_200_failed_swaps,
        "mm2_coins": info.get_mm2_coins_list(),
        "taker_coin": helper.get_or_none(request, "taker_coin"),
        "maker_coin": helper.get_or_none(request, "maker_coin"),
        "page_title": "Last 200 Failed Swaps"
    })

    return render(request, 'views/atomicdex/last_200_failed_swaps.html', context)


def makerbot_config_form_view(request):
    context = helper.get_base_context(request)
    context.update({
        "page_title": "Generate Simple Market Maker Configuration",
        "mm2_coins": info.get_mm2_coins_list()
    })

    if request.GET: 
        try:
            form = forms.MakerbotForm(request.GET)
            context.update({
                "form": form
            })
            if request.GET['base'] == request.GET['rel']:
                messages.error(request, 'Sell and Buy coins need to be different')
            else:
                form_resp = {
                     f"{request.GET['base']}/{request.GET['rel']}": {
                        "base": request.GET['base'],
                        "rel": request.GET['rel'],
                        "min_volume": {request.GET['min_trade_type']:request.GET['min_trade']},
                        "max_volume": {request.GET['max_trade_type']:request.GET['max_trade']},
                        "spread": str(1+float(request.GET['spread'])/100),
                        "base_confs": int(request.GET['base_confs']),
                        "base_nota": request.GET['base_nota'] == "True",
                        "rel_confs": int(request.GET['rel_confs']),
                        "rel_nota": request.GET['rel_nota'] == "True",
                        "enable": request.GET['enable'] == "True",
                        "price_elapsed_validity": int(request.GET['price_elipsed_validity']),
                        "check_last_bidirectional_trade_thresh_hold": request.GET['check_last_bidirectional_trade_thresh_hold'] == "True"
                    }

                }
                if request.GET['min_trade_type'] == 'pct':
                    form_resp[f"{request.GET['base']}/{request.GET['rel']}"].update({
                        "min_volume": {request.GET['min_trade_type']:float(request.GET['min_trade'])/100},
                    })
                if request.GET['max_trade_type'] == 'pct':
                    form_resp[f"{request.GET['base']}/{request.GET['rel']}"].update({
                        "max_volume": {request.GET['max_trade_type']:float(request.GET['max_trade'])/100},
                    })
                context.update({
                    "bot_refresh_rate":request.GET['bot_refresh_rate'],
                    "price_url":request.GET['price_url']
                })   

                if request.GET['create_bidirectional_config'] == "True":
                    form_resp.update({
                         f"{request.GET['rel']}/{request.GET['base']}": {
                            "base": request.GET['rel'],
                            "rel": request.GET['base'],
                            "min_volume": {request.GET['min_trade_type']:request.GET['min_trade']},
                            "max_volume": {request.GET['max_trade_type']:request.GET['max_trade']},
                            "spread": str(1+float(request.GET['spread'])/100),
                            "base_confs": int(request.GET['rel_confs']),
                            "base_nota": request.GET['rel_nota'] == "True",
                            "rel_confs": int(request.GET['base_confs']),
                            "rel_nota": request.GET['base_nota'] == "True",
                            "enable": request.GET['enable'] == "True",
                            "price_elapsed_validity": int(request.GET['price_elipsed_validity']),
                            "check_last_bidirectional_trade_thresh_hold": request.GET['check_last_bidirectional_trade_thresh_hold'] == "True"
                        }
                    })
                    if request.GET['min_trade_type'] == 'pct':
                        form_resp[f"{request.GET['rel']}/{request.GET['base']}"].update({
                            "min_volume": {request.GET['min_trade_type']:float(request.GET['min_trade'])/100},
                        })
                    if request.GET['max_trade_type'] == 'pct':
                        form_resp[f"{request.GET['rel']}/{request.GET['base']}"].update({
                            "max_volume": {request.GET['max_trade_type']:float(request.GET['max_trade'])/100},
                        })

                try:
                    if request.GET['add_to_existing_config'] == "True":
                        if len(request.GET['existing_config']) > 0:
                            existing_cfg = json.loads(request.GET['existing_config'].replace("\'", "\"").replace("True", "true").replace("False", "false"))
                            form_resp.update(existing_cfg)
                except Exception as e:
                    messages.error(request, 'e')
                    print(e)
                context.update({
                    "form_resp":form_resp
                })
            return render(request, 'views/atomicdex/makerbot_config_form.html', context)
        except Exception as e:
            print(e)
        
    form = forms.MakerbotForm() 
    context.update({
        "form": form
    })
    return render(request, 'views/atomicdex/makerbot_config_form.html', context)


def orderbook_view(request):
    context = helper.get_base_context(request)
    context.update({
        "mm2_coins": info.get_mm2_coins_list(),
        "base": helper.get_or_none(request, "base", "KMD"),
        "rel": helper.get_or_none(request, "rel", "BTC")
    })

    orderbook = dex.get_orderbook(request)

    if "bids" in orderbook:
        base = orderbook["base"]
        rel = orderbook["rel"]
        context.update({
            "base": base,
            "rel": rel
        })
        bids = []
        for bid in orderbook["bids"]:
            price = bid["price"]
            maxvolume = bid["maxvolume"]
            min_volume = bid["min_volume"]
            bids.append({
                "base": base,
                "rel": rel,
                "price": price,
                "maxvolume": maxvolume,
                "min_volume": min_volume,
                "base_total": float(maxvolume)/float(price)
            })

        context.update({
            "bids": bids
        })

    if "asks" in orderbook:
        base = orderbook["base"]
        rel = orderbook["rel"]
        context.update({
            "base": base,
            "page_title": f"AtomicDEX {base}/{rel} Orderbook",
            "rel": rel
        })

        asks = []
        for ask in orderbook["asks"]:
            price = ask["price"]
            maxvolume = ask["maxvolume"]
            min_volume = ask["min_volume"]
            asks.append({
                "base": base,
                "rel": rel,
                "price": price,
                "maxvolume": maxvolume,
                "min_volume": min_volume,
                "rel_total": float(maxvolume)*float(price)
            })

        context.update({
            "asks": asks
        })

    return render(request, 'views/atomicdex/orderbook.html', context)

def testnet_seednode_version_stats_hourly_table_view(request):
    context = helper.get_base_context(request)
    active_version = " & ".join(dex.get_active_mm2_versions(time.time()))
    version_scores = dex.get_testnet_nn_seed_version_scores_hourly_table(request)

    context.update({
        "active_version": active_version,
        "date": version_scores["date"],
        "end": int(version_scores["end"]),
        "start": int(version_scores["start"]),
        "date_ts": int(version_scores["start"]*1000),
        "table_data": version_scores["table_data"],
        "headers": version_scores["headers"],
        "scores": version_scores["scores"]
    })
    print(version_scores["date"])

    return render(request, 'views/atomicdex/seednode_version_stats_hourly_table.html', context)



def seednode_version_stats_hourly_table_view(request):
    context = helper.get_base_context(request)
    stats_date = helper.get_or_none(request, "date", "Today")

    date_ts = helper.floor_to_utc_day(time.time())
    date_ts = int(helper.get_or_none(request, "date_ts", date_ts))
    # Normalise if in ms instead of sec
    if date_ts > time.time()*10: date_ts /= 1000

    start = helper.floor_to_utc_day(date_ts)
    end = start + SINCE_INTERVALS["day"]

    active_version = " & ".join(dex.get_active_mm2_versions(time.time()))
    version_scores = dex.get_nn_seed_version_scores_hourly_table(request, start, end)

    context.update({
        "date": helper.get_or_none(request, "date", "Today"),
        "date_ts": date_ts,
        "stats_date": stats_date,
        "active_version": active_version,
        "headers": version_scores["headers"],
        "scores": version_scores["scores"]
    })

    return render(request, 'views/atomicdex/seednode_version_stats_hourly_table.html', context)


def seednode_version_stats_daily_table_view(request):
    context = helper.get_base_context(request)

    start = time.time() + (SINCE_INTERVALS["day"])
    start = helper.get_or_none(request, "start", start)
    start = helper.floor_to_utc_day(start)
    end = start + (SINCE_INTERVALS["day"])

    prev_ts = start - 1 * (SINCE_INTERVALS["day"])
    next_ts = end + (SINCE_INTERVALS["day"])

    from_date  = helper.date_hour(start - (SINCE_INTERVALS["day"])).split(" ")[0]
    to_date = helper.date_hour(end - (SINCE_INTERVALS["day"])).split(" ")[0]
    active_version = " & ".join(dex.get_active_mm2_versions(time.time()))

    version_scores = query.get_nn_seed_version_scores_daily_table(request, start, end)
    context.update({
        "to_date": to_date,
        "from_date": from_date,
        "prev_ts": prev_ts,
        "next_ts": next_ts,
        "active_version": active_version,
        "headers": version_scores["headers"],
        "scores": version_scores["scores"]
    })

    return render(request, 'views/atomicdex/seednode_version_stats_daily_table.html', context)


def seednode_version_stats_month_table_view(request):
    context = helper.get_base_context(request)
    start = SEASONS_INFO[context["season"]]["start_time"]
    end = SEASONS_INFO[context["season"]]["end_time"]
    version_scores = query.get_nn_seed_version_scores_month_table(request, start, end)

    context.update({
        "active_version": " & ".join(dex.get_active_mm2_versions(time.time())),
        "headers": version_scores["headers"],
        "scores": version_scores["scores"]
    })

    return render(request, 'views/atomicdex/seednode_version_stats_month_table.html', context)

