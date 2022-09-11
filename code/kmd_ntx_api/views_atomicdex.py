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

    context.update({
        "page_title": "Generate AtomicDEX-API Enable Command",
        "endpoint": "/api/table/coin_activation/"
    })

    return render(request, 'views/atomicdex/activation_commands.html', context)


def recreate_swap_data_view(request):
    context = helper.get_base_context(request)

    context.update({
        "page_title": "Recreate failed swap data"
    })

    return render(request, 'views/atomicdex/recreate_swap_data.html', context)


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
    context.update({
        "page_title": "AtomicDEX Best Orders",
        "endpoint": f"/api/table/bestorders/",
        "mm2_coins": info.get_mm2_coins_list()
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
        "page_title": "AtomicDEX GUI Stats",
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
        "endpoint": f"/api/atomicdex/last_200_swaps",
        "mm2_coins": info.get_mm2_coins_list(),
        "taker_coin": helper.get_or_none(request, "taker_coin", "All"),
        "maker_coin": helper.get_or_none(request, "maker_coin", "All"),
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
        "page_title": "AtomicDEX Orderbook",
        "endpoint": "/api/table/orderbook/",
        "mm2_coins": info.get_mm2_coins_list(),
        "base": helper.get_or_none(request, "base", "KMD"),
        "rel": helper.get_or_none(request, "rel", "BTC")
    })


    return render(request, 'views/atomicdex/orderbook.html', context)


############################################

def seednode_version_view(request):
    context = helper.get_base_context(request)
    active_version = " & ".join(dex.get_active_mm2_versions(time.time()))
    day_version_scores = dex.get_seednode_version_date_table(request)
    month_version_scores = dex.get_seednode_version_month_table(request)

    context.update({
        "page_title": "AtomicDEX Seednode Stats",
        "active_version": active_version,
        "day_date": day_version_scores["date"],
        "day_start": int(day_version_scores["start"]),
        "day_end": int(day_version_scores["end"]),
        "day_date_ts": int(day_version_scores["start"]*1000),
        "day_table_data": day_version_scores["table_data"],
        "day_headers": day_version_scores["headers"],
        "day_scores": day_version_scores["scores"],
        "month_date": month_version_scores["date"],
        "month_date_ts": month_version_scores["date_ts"],
        "month_table_data": month_version_scores["table_data"],
        "month_headers": month_version_scores["headers"],
        "month_scores": month_version_scores["scores"]
    })

    return render(request, 'views/atomicdex/seednode_version_stats.html', context)



