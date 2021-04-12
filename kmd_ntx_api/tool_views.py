#!/usr/bin/env python3
import requests
from django.shortcuts import render

from kmd_ntx_api.lib_info import *
from kmd_ntx_api.api_tools import *

def pubkey_addresses_view(request):
    context = {
        "sidebar_links":get_sidebar_links(),
        "eco_data_link":get_eco_data_link()
    }
    if "pubkey" in request.GET:
        pubkey = request.GET["pubkey"]
        if pubkey == "":
            messages.error(request, f"No pubkey input!")
        elif validate_pubkey(pubkey):
            base_58_coins = requests.get("http://116.203.120.91:8762/api/info/base_58/").json()["results"]
            base_58_coins_list = list(base_58_coins.keys())
            address_rows = []
            
            for coin in base_58_coins_list:
                pubtype = base_58_coins[coin]["pubtype"]
                p2shtype = base_58_coins[coin]["p2shtype"]
                wiftype = base_58_coins[coin]["wiftype"]
                address_row = calc_addr_tool(pubkey, pubtype, p2shtype, wiftype)
                address_row.update({"coin":coin})
                address_rows.append(address_row)
            context.update({
                "pubkey": pubkey,
                "address_rows": address_rows,
            })
        else:
            messages.error(request, f"Invalid pubkey: {pubkey}")

    return render(request, 'tool_pubkey_addresses.html', context)

def decode_opret_view(request):
    context = {
        "sidebar_links":get_sidebar_links(),
        "eco_data_link":get_eco_data_link()
    }

    if "OP_RETURN" in request.GET:
        OP_RETURN = request.GET["OP_RETURN"].replace("OP_RETURN ", "")

        if OP_RETURN == "":
            messages.error(request, f"No OP_RETURN input!")

        elif validate_opret(OP_RETURN):

            url = f"http://116.203.120.91:8762/api/tools/decode_opreturn/?OP_RETURN={OP_RETURN}"
            decoded = requests.get(url).json()

            opret_rows = [{"key":"OP_RETURN", "value":OP_RETURN}]
            for item in decoded:
                key_val = item.replace("_", " ").title()
                opret_rows.append({"key":key_val, "value":decoded[item]})

            context.update({
                "OP_RETURN": OP_RETURN,
                "opret_rows": opret_rows,
            })

        else:
            messages.error(request, f"Invalid OP_RETURN: {OP_RETURN}")

    return render(request, 'tool_opret.html', context)



