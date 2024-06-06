#!/usr/bin/env python3
import time
import requests
from django.shortcuts import render
from django.contrib import messages
from datetime import datetime as dt

from kmd_ntx_api.const import SINCE_INTERVALS, SMARTCHAINS
from kmd_ntx_api.cache_data import launch_params_cache
from kmd_ntx_api.logger import logger
from kmd_ntx_api.based_58 import convert_addresses, decode_opret, \
    validate_pubkey, calc_addr_tool
from kmd_ntx_api.context import get_base_context
from kmd_ntx_api.explorers import get_explorers, get_dexstats_utxos
from kmd_ntx_api.helper import get_or_none, \
    has_error, get_notary_list
from kmd_ntx_api.raw_transaction import send_raw_tx, raw_tx
from kmd_ntx_api.info import get_base_58_coin_params, get_coin_icons, \
    get_daemon_cli
from kmd_ntx_api.notary_seasons import get_page_season


def convert_addresses_view(request):
    context = get_base_context(request)
    context.update({
        "page_title":"Address Conversion",
        "endpoint": "/api/tools/address_conversion/"
    })

    if "address" in request.GET:
        address = request.GET["address"]
        if address == "":
            messages.error(request, f"No address input!")
        else:
            address_rows = []
            addresses = convert_addresses(address)["results"]

            for item in addresses:
                for coin in item:

                    # TODO: Handle segwit addresses
                    # TODO: Explorers for protocol coins
                    if coin.lower().find('segwit') == -1:
                        address_rows.append({
                            "coin":coin, "address":item[coin]
                        })

            context.update({
                "address": address,
                "address_rows": address_rows,
            })

    return render(request, 'views/tools/tool_convert_addresses.html', context)


def create_raw_transaction_view(request):
    coin = get_or_none(request, "coin", "KMD")
    address = get_or_none(request, "address")
    inputs = get_or_none(request, "inputs")
    context = get_base_context(request)

    context.update({
        "page_title":"Create Raw Transaction from Address",
        "reqget":request.GET,
        "coin":coin,
        "address": address,
        "now":int(time.time()),
        "locktime":int(time.time())-30*60,
        "30_min_ago":int(time.time()-30*60),
        "smartchain_coins_list": SMARTCHAINS
    })

    # Step one: get UTXOs for selection and show form for destination and amount
    if address:
        context.update({
            "utxos": get_dexstats_utxos(coin, address)
        })

    # Step two, construct the raw hex
    if inputs:
        output_amounts = request.GET.getlist("output_amount")
        to_addresses = request.GET.getlist("to_address")
        locktime = request.GET["locktime"]
        expiry_height = request.GET["expiry_height"]

        test_tx = raw_tx()
        tx_inputs = []
        for vin in inputs.split(","):
            elements = vin.split("|")
            tx_inputs.append({
                "tx_hash":elements[0],
                "tx_pos":int(elements[1]),
                "value":float(elements[2]),
                "scriptPubKey":elements[3]
                })
        test_tx.inputs = tx_inputs

        outputs = []
        for i in range(len(to_addresses)):
            outputs.append({
                "address":to_addresses[i],
                "amount":output_amounts[i]
            })
        test_tx.outputs = outputs
        test_tx.locktime = locktime
        raw_hex = test_tx.construct()

        context.update({
            "tx_inputs": tx_inputs,
            "outputs": outputs,
            "raw_tx": raw_hex
        })

    return render(request, 'views/tools/tool_create_raw_transaction.html', context)


def daemon_cli_view(request):

    daemon_cli = get_daemon_cli(request)
    coin_icons = get_coin_icons(request)

    daemon_cli_rows = []
    for coin in daemon_cli:
        daemon_cli_rows.append({"coin":coin, "daemon_cli":daemon_cli[coin]})

    context = get_base_context(request)
    context.update({
        "daemon_cli_rows": daemon_cli_rows,
        "page_title":"Daemon CLIs"
    })

    return render(request, 'views/tools/tool_daemon_cli.html', context)


def decode_op_return_view(request):
    context = get_base_context(request)
    context.update({
        "page_title":"Decode OP_RETURN Tool"
    })

    op_return = get_or_none(request, "OP_RETURN")

    if op_return:
        try:
            decoded = decode_opret(op_return)
        except Exception as e:
            decoded = {"error": e}

        if not "error" in decoded:
            opret_rows = []
            for item in decoded:
                key_val = item.replace("_", " ").title()
                opret_rows.append({"key":key_val, "value":decoded[item]})

            context.update({
                "OP_RETURN": op_return,
                "opret_rows": opret_rows,
            })

        else:
            messages.error(request, f"Invalid OP_RETURN: {op_return}")

    return render(request, 'views/tools/tool_decode_opret.html', context)


def faucet_view(request):
    context = get_base_context(request)
    faucet_balances = requests.get(f"https://faucet.komodo.earth/faucet_balances").json()
    pending_tx_resp = requests.get(f"https://faucet.komodo.earth/show_pending_tx").json()
    pending_tx_list = []
    tx_rows = []
    pending_index = []
    if "result" in pending_tx_resp:
        if "message" in pending_tx_resp["result"]:
            pending_tx_list = pending_tx_resp["result"]["message"]
    for item in pending_tx_list:
        tx_rows.append({
            "index": item[0],    
            "coin": item[1], 
            "address": item[2], 
            "time_sent": "n/a",
            "timestamp": 99999999999999,
            "amount": "n/a",
            "txid": "n/a",
            "status": item[6]
        })
        pending_index.append(item[0])
        if len(tx_rows) >= 250:
            break
    sent_tx_resp = requests.get(f"https://faucet.komodo.earth/show_faucet_db").json()
    sent_tx_list = []
    now = time.time()
    sum_24hrs = 0
    count_24hrs = 0
    if "result" in sent_tx_resp:
        if "message" in sent_tx_resp["result"]:
            sent_tx_list = sent_tx_resp["result"]["message"]
    for item in sent_tx_list:
        if item[0] not in pending_index:
            if item[3] > SINCE_INTERVALS['day']:
                sum_24hrs += item[4]
                count_24hrs += 1
            tx_rows.append({
                "index": item[0],
                "coin": item[1],
                "address": item[2],
                "timestamp": item[3],
                "time_sent": dt.utcfromtimestamp(item[3]),
                "amount": item[4],
                "txid": item[5],
                "status": item[6]
            })

    faucet_coins_list = ["DOC", "MARTY", "ZOMBIE"]
    context.update({
        "page_title":"Testcoin Faucet",
        "explorers":get_explorers(request),
        "faucet_balances":faucet_balances,
        "count_24hrs":count_24hrs,
        "sum_24hrs":sum_24hrs,
        "tx_rows": tx_rows,
        "faucet_coins_list": faucet_coins_list
    })

    if request.method == 'POST':
        if 'coin' in request.POST:
            coin = request.POST['coin'].strip()
            if coin == "TKL":
                coin = "TOKEL"
        if 'address' in request.POST:
            address = request.POST['address'].strip()
        url = f'https://faucet.komodo.earth/faucet/{coin}/{address}'
        r = requests.get(url)
        try:
            resp = r.json()
            messages.success(request, resp["result"]["message"])
            if resp['status'] == "success":
                context.update({"result": coin+"_success"})
            elif resp['status'] == "error":
                context.update({"result": "disqualified"})
            else:
                context.update({"result": "fail"})
        except Exception as e:
            logger.error(f"[faucet] Exception: {e}")
            messages.success(request, f"Something went wrong... {e}")
            context.update({"result":"fail"})

    return render(request, 'views/tools/tool_faucet.html', context)


def launch_params_view(request):
    launch_params = launch_params_cache()

    launch_param_rows = []
    coin_icons = get_coin_icons(request)
    for coin in launch_params:
        launch_param_rows.append({"coin":coin, "launch_params":launch_params[coin]})
        if coin not in coin_icons:
            coin_icons.update({coin: "/static/img/notary/icon/blank.png"})

    context = get_base_context(request)
    context.update({
        "launch_param_rows": launch_param_rows,
        "page_title":"Launch Parameters"
    })

    return render(request, 'views/tools/tool_launch_params.html', context)


def pubkey_addresses_view(request):
    context = get_base_context(request)
    context.update({
        "page_title": "Pubkey Addresses",
        "endpoint": "/api/tools/address_from_pubkey/"
    })
    if "pubkey" in request.GET:
        pubkey = request.GET["pubkey"]
        if pubkey == "":
            messages.error(request, f"No pubkey input!")
        elif not validate_pubkey(pubkey):
            messages.error(request, f"Invalid pubkey: {pubkey}")
        else:
            base_58_coins = get_base_58_coin_params(request)
            address_rows = []
            
            for coin in base_58_coins:
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

    return render(request, 'views/tools/tool_pubkey_addresses.html', context)


def scripthashes_from_pubkey_view(request):
    context = get_base_context(request)
    context.update({
        "page_title":"Get Scripthashes from Pubkey"
    })
    if "pubkey" in request.GET:
        pubkey = request.GET["pubkey"]
        url = f"http://127.0.0.1:8762/api/tools/scripthashes_from_pubkey/?pubkey={pubkey}"
        resp = requests.get(url).json()

        if has_error(resp):
            messages.error(request, f"{resp['error']}")
        else:
            resp_rows = []
            for item in resp["results"]:
                key_val = item.replace("_", " ").title()
                resp_rows.append({"key":key_val, "value":resp["results"][item]})

            context.update({
                "pubkey":pubkey,
                "resp_rows": resp_rows
            })

    return render(request, 'views/tools/tool_scripthashes_from_pubkey.html', context)


def scripthash_from_address_view(request):
    context = get_base_context(request)
    context.update({
        "page_title":"Get Scripthash from Address"
    })
    if "address" in request.GET:
        address = request.GET["address"]
        url = f"http://127.0.0.1:8762/api/tools/scripthash_from_address/?address={address}"
        resp = requests.get(url).json()

        if has_error(resp):
            messages.error(request, f"{resp['error']}")
        else:
            resp_rows = []
            for item in resp["results"]:
                key_val = item.replace("_", " ").title()
                resp_rows.append({"key":key_val, "value":resp["results"][item]})

            context.update({
                "address":address,
                "resp_rows": resp_rows
            })

    return render(request, 'views/tools/tool_scripthash_from_address.html', context)


def send_raw_tx_view(request):
    context = get_base_context(request)
    context.update({
        "page_title":"Send Raw Transaction (experimental!)",
        "smartchain_coins_list": SMARTCHAINS
    })

    if "coin" in request.GET or "tx_hex" in request.GET:
        resp = send_raw_tx(request)

        if has_error(resp):
            messages.error(request, f"{resp['error']}")
        else:
            messages.success(request, f"{resp}")

    return render(request, 'views/tools/tool_send_raw_transaction.html', context)


def explorer_status_view(request):
    context = get_base_context(request)
    context.update({
        "page_title":"Insight Explorer Status"
    })

    return render(request, 'views/tools/tool_insight_status.html', context)

