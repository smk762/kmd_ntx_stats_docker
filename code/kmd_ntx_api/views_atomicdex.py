#!/usr/bin/env python3
import requests
from django.shortcuts import render
from .lib_helper import get_or_none

from kmd_ntx_api.lib_info import *
from kmd_ntx_api.lib_atomicdex import *
from kmd_ntx_api.forms import *


def activation_commands_view(request):
    season = get_page_season(request)
    scheme_host = get_current_host(request)
    url = f"{scheme_host}api/atomicdex/activation_commands/"
    data = requests.get(url).json()["commands"]
    activation_data = {}
    for protocol in data:
        if len(data[protocol]) != 0:
            activation_data.update({protocol:data[protocol]})

    context = {
        "season":season,
        "page_title":"Generate AtomicDEX-API Enable Command",
        "scheme_host": scheme_host,
        "sidebar_links":get_sidebar_links(season),
        "activation_data":activation_data,
        "eco_data_link":get_eco_data_link()
    }
    return render(request, 'atomicdex/activation_commands.html', context)


def batch_activation_form_view(request):
    context = get_context(request)
    context.update({
        "page_title":"Generate AtomicDEX-API Batch Activation Commands",
        "sidebar_links":get_sidebar_links(season)
    })

    if request.GET:
        try:
            coin = request.GET["coin"]
            form = EnableCommandForm(request.GET)
            context.update({
                "form":form
            })
            url = f"{scheme_host}api/atomicdex/activation_commands"
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
            return render(request, 'atomicdex/batch_activation_form.html', context)
        except Exception as e:
            print(e)
        
    form = EnableCommandForm() 
    context.update({
        "form":form
    })

    return render(request, 'atomicdex/batch_activation_form.html', context)


def bestorders_view(request):
    coin = "KMD"
    if "coin" in request.GET:
        coin = request.GET["coin"]
    season = get_page_season(request)
    context = {
        "coin": coin,
        "season": season,
        "mm2_coins": get_mm2_coins(),
        "scheme_host": get_current_host(request),
        "sidebar_links": get_sidebar_links(season),
        "eco_data_link": get_eco_data_link()
    }
    bestorders = get_bestorders(request)["result"]
    rows = []
    for coin in bestorders:
        rows.append({
            "coin": coin,
            "price": bestorders[coin][0]["price"],
            "maxvolume": bestorders[coin][0]["maxvolume"],
            "min_volume": bestorders[coin][0]["min_volume"],
        })

    context.update({
        "bestorders": rows
    })

    return render(request, 'atomicdex/bestorders.html', context)


def gui_stats_view(request):
    swaps_data = get_swaps_data()
    since = "week"
    to_time = int(time.time())
    from_time = int(to_time - 60*60*24*14)
    if "from_time" in request.GET:
        from_time = int(request.GET["from_time"])
    if "to_time" in request.GET:
        to_time = int(request.GET["to_time"])
    if "since" in request.GET:
        since = request.GET["since"]
    swaps_data = filter_swaps_timespan(swaps_data, from_time, to_time)
    season = get_page_season(request)
    context = {
        "from_time": from_time,
        "to_time": to_time,
        "from_time_dt": dt.fromtimestamp(from_time),
        "to_time_dt": dt.fromtimestamp(to_time),
        "since_options": list(SINCE_INTERVALS.keys()),
        "since": since,
        "season": season,
        "swaps_counts": get_swaps_counts(swaps_data),
        "scheme_host": get_current_host(request),
        "sidebar_links": get_sidebar_links(season),
        "eco_data_link": get_eco_data_link()
    }

    return render(request, 'atomicdex/gui_stats.html', context)


def last_200_swaps_view(request):
    season = get_page_season(request)
    last_200_swaps = get_last_200_swaps(request)
    last_200_swaps = format_gui_os_version(last_200_swaps)
    context = {
        "last_200_swaps": last_200_swaps,
        "season": season,
        "mm2_coins": get_mm2_coins(),
        "taker_coin": get_or_none(request, "taker_coin"),
        "maker_coin": get_or_none(request, "maker_coin"),
        "page_title": "Last 200 Swaps",
        "scheme_host": get_current_host(request),
        "sidebar_links": get_sidebar_links(season),
        "eco_data_link": get_eco_data_link()
    }

    return render(request, 'atomicdex/last_200_swaps.html', context)


def last_200_failed_swaps_view(request):
    season = get_page_season(request)
    last_200_failed_swaps = get_last_200_failed_swaps(request)
    last_200_failed_swaps = format_gui_os_version(last_200_failed_swaps)

    context = {
        "last_200_failed_swaps": last_200_failed_swaps,
        "season": season,
        "mm2_coins": get_mm2_coins(),
        "taker_coin": get_or_none(request, "taker_coin"),
        "maker_coin": get_or_none(request, "maker_coin"),
        "page_title": "Last 200 Failed Swaps",
        "scheme_host": get_current_host(request),
        "sidebar_links": get_sidebar_links(season),
        "eco_data_link": get_eco_data_link()
    }

    return render(request, 'atomicdex/last_200_failed_swaps.html', context)


def makerbot_config_form_view(request):
    mm2_coins = list(get_dexstats_explorers().keys())
    season = get_page_season(request)
    context = {
        "season":season,
        "page_title":"Generate Simple Market Maker Configuration",
        "scheme_host": get_current_host(request),
        "sidebar_links":get_sidebar_links(season),
        "mm2_coins":mm2_coins,
        "eco_data_link":get_eco_data_link()
    }

    if request.GET: 
        try:
            form = MakerbotForm(request.GET)
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
                print(form_resp)
                context.update({
                    "form_resp":form_resp
                })
            return render(request, 'atomicdex/makerbot_config_form.html', context)
        except Exception as e:
            print(e)
        
    form = MakerbotForm() 
    context.update({
        "form": form
    })
    return render(request, 'atomicdex/makerbot_config_form.html', context)


def orderbook_view(request):
    season = get_page_season(request)
    context = {
        "season": get_page_season(request),
        "mm2_coins": get_mm2_coins(),
        "scheme_host": get_current_host(request),
        "sidebar_links": get_sidebar_links(season),
        "eco_data_link": get_eco_data_link()
    }
    orderbook = get_orderbook(request)

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

    return render(request, 'atomicdex/orderbook.html', context)


def seednode_version_stats_view(request):
    season = get_page_season(request)
    start = time.time()- 24*60*60
    end = time.time()
    if 'start' in request.GET:
        start = request.GET["start"]
    if 'end' in request.GET:
        end = request.GET["end"]
    context = {
        "season": season,
        "start": int(start),
        "end": int(end),
        "start_str": datetime.fromtimestamp(int(start)).strftime("%m/%d/%Y, %H:%M:%S"),
        "end_str": datetime.fromtimestamp(int(end)).strftime("%m/%d/%Y, %H:%M:%S"),
        "scheme_host": get_current_host(request),
        "sidebar_links": get_sidebar_links(season),
        "eco_data_link": get_eco_data_link()
    }

    return render(request, 'atomicdex/seednode_version_stats.html', context)

