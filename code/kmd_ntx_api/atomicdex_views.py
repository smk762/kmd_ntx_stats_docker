#!/usr/bin/env python3
import json
from django.contrib import messages
from django.shortcuts import render
from kmd_ntx_api.cache_data import activation_commands_cache
from kmd_ntx_api.helper import get_or_none
from kmd_ntx_api.context import get_base_context
from kmd_ntx_api.forms import EnableCommandForm, MakerbotForm
from kmd_ntx_api.swaps import format_gui_os_version, get_last_200_swaps


def activation_commands_view(request):
    context = get_base_context(request)
    context.update({
        "page_title": "Generate AtomicDEX-API Enable Command",
        "mm2_coins": True
    })
    return render(request, 'views/atomicdex/activation_commands.html', context)


def batch_activation_form_view(request):
    context = get_base_context(request)
    activation_commands = activation_commands_cache()
    context.update({
        "page_title":"Generate AtomicDEX-API Batch Activation Commands",
        "mm2_coins": True
    })
    if not request.GET:
        form = EnableCommandForm() 
        context.update({"form":form})
    else:
        try:
            coin = request.GET["coin"]
            form = EnableCommandForm(request.GET)
            context.update({"form":form})
            command_str = activation_commands[coin]
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
            context.update({"form_resp":form_resp})
        except Exception as e:
            messages.error(request, e)
    return render(request, 'views/atomicdex/batch_activation_form.html', context)


def bestorders_view(request):
    context = get_base_context(request)
    context.update({
        "page_title": "AtomicDEX Best Orders",
        "mm2_coins": True
    })

    return render(request, 'views/atomicdex/bestorders.html', context)


def electrum_status_view(request):
    context = get_base_context(request)
    context.update({"page_title": "Electrum Status"})
    return render(request, 'components/tables/atomicdex/table_electrum_status.html', context)


def last_200_swaps_view(request):
    context = get_base_context(request)
    last_200_swaps = get_last_200_swaps(request)
    last_200_swaps = format_gui_os_version(last_200_swaps)

    context.update({
        "last_200_swaps": last_200_swaps,
        "mm2_coins": True,
        "taker_coin": get_or_none(request, "taker_coin", "All"),
        "maker_coin": get_or_none(request, "maker_coin", "All"),
        "page_title": "Last 200 Swaps"
    })

    return render(request, 'views/atomicdex/last_200_swaps.html', context)


def makerbot_config_form_view(request):
    context = get_base_context(request)
    context.update({
        "page_title": "Generate Simple Market Maker Configuration",
        "mm2_coins": True
    })
    if request.GET: 
        try:
            form = MakerbotForm(request.GET)
            context.update({"form": form})
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
                    logger.info(e)
                context.update({"form_resp":form_resp})
            return render(request, 'views/atomicdex/makerbot_config_form.html', context)
        except Exception as e:
            logger.info(e)
        
    form = MakerbotForm() 
    context.update({"form": form})
    return render(request, 'views/atomicdex/makerbot_config_form.html', context)


def orderbook_view(request):
    context = get_base_context(request)
    context.update({
        "page_title": "AtomicDEX Orderbook",
        "mm2_coins": True,
        "base": get_or_none(request, "base", "KMD"),
        "rel": get_or_none(request, "rel", "DGB")
    })
    return render(request, 'views/atomicdex/orderbook.html', context)
