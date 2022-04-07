#!/usr/bin/env python3
import requests
from django.shortcuts import render

from kmd_ntx_api.lib_const import *
import kmd_ntx_api.lib_base58 as b58
import kmd_ntx_api.lib_info as info
import kmd_ntx_api.lib_helper as helper
import kmd_ntx_api.lib_table as table
import kmd_ntx_api.lib_atomicdex as dex
import kmd_ntx_api.api_tools as api_tools


def convert_addresses_view(request):
    context = helper.get_base_context(request)
    context.update({
        "page_title":"Address Conversion",
        "explorers": info.get_explorers(request)
    })
    if "address" in request.GET:
        address = request.GET["address"]
        if address == "":
            messages.error(request, f"No address input!")
        else:
            address_rows = []
            addresses = b58.convert_addresses(address)["results"]
            for item in addresses:
                for chain in item:
                    address_rows.append({
                        "chain":chain, "address":item[chain]
                    })
            context.update({
                "address": address,
                "address_rows": address_rows,
            })

    return render(request, 'views/tools/tool_convert_addresses.html', context)


def create_raw_transaction_view(request):
    chain = helper.get_or_none(request, "chain", "KMD")
    context = helper.get_base_context(request)
    context.update({
        "chain":chain,
        "now":int(time.time()),
        "locktime":int(time.time())-30*60,
        "20_min_ago":int(time.time()-30*60),
        "reqget":request.GET,
        "page_title":"Create Raw Transaction from Address",
        "mm2_coins":info.get_mm2_coins_list()
    })

    if "address" in request.GET:
        address = request.GET["address"]
        rewards_resp = requests.get(f"{THIS_SERVER}/api/tools/kmd_rewards/?address={address}").json()
        resp = requests.get(f"https://{chain}.explorer.dexstats.info/insight-api-komodo/addr/{address}/utxo")
        utxos = resp.json()
        if "error" in resp:
            messages.error(request, resp["error"])
        else:
            for utxo in utxos:
                if utxo["txid"] in rewards_resp["utxos"]:
                    txid = utxo["txid"]
                    rewards = rewards_resp["utxos"][txid]["kmd_rewards"]
                    utxo.update({"rewards":rewards})
                
            context.update({
                "address": address,
                "utxos": utxos
            })

    if "inputs" in request.GET:
        inputs = request.GET["inputs"]
        output_amounts = request.GET.getlist("output_amount")
        to_addresses = request.GET.getlist("to_address")
        locktime = request.GET["locktime"]
        expiry_height = request.GET["expiry_height"]

        test_tx = b58.raw_tx()
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

    url = f"{THIS_SERVER}/api/info/daemon_cli"
    daemon_cli = requests.get(url).json()["results"]

    daemon_cli_rows = []
    for chain in daemon_cli:
        daemon_cli_rows.append({"chain":chain, "daemon_cli":daemon_cli[chain]})

    context = helper.get_base_context(request)
    context.update({
        "daemon_cli_rows": daemon_cli_rows,
        "page_title":"Daemon CLIs"
    })

    return render(request, 'views/tools/tool_daemon_cli.html', context)


def decode_opret_view(request):
    context = helper.get_base_context(request)
    context.update({
        "page_title":"Decode OP_RETURN Tool"
    })

    if "OP_RETURN" in request.GET:
        OP_RETURN = request.GET["OP_RETURN"].replace("OP_RETURN ", "")

        if OP_RETURN == "":
            messages.error(request, f"No OP_RETURN input!")

        elif api_tools.validate_opret(OP_RETURN):

            url = f"{THIS_SERVER}/api/tools/decode_opreturn/?OP_RETURN={OP_RETURN}"
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

    return render(request, 'views/tools/tool_decode_opret.html', context)


def kmd_rewards_view(request):
    context = helper.get_base_context(request)
    context.update({
        "page_title":"KMD Rewards Tool"
    })
    if "address" in request.GET:
        address = request.GET["address"]
        url = f"{THIS_SERVER}/api/tools/kmd_rewards"
        resp = requests.get(f"{url}/?address={address}").json()
        if "error" in resp:
            messages.error(request, resp["error"])
        else:
            kmd_rewards_rows = []
            for utxo in resp["utxos"]:
                row = {"txid":utxo}
                row.update(resp["utxos"][utxo])
                kmd_rewards_rows.append(row)

            context.update({
                "address": address,
                "kmd_balance": resp["kmd_balance"],
                "total_rewards": round(resp["total_rewards"],6),
                "utxo_count": resp["utxo_count"],
                "eligible_utxo_count": resp["eligible_utxo_count"],
                "oldest_utxo_block": resp["oldest_utxo_block"],
                "kmd_rewards_rows": kmd_rewards_rows,
            })

    return render(request, 'views/tools/tool_kmd_rewards.html', context)


def launch_params_view(request):

    url = f"{THIS_SERVER}/api/info/launch_params"
    launch_params = requests.get(url).json()["results"]

    launch_param_rows = []
    for chain in launch_params:
        launch_param_rows.append({"chain":chain, "launch_params":launch_params[chain]})

    context = helper.get_base_context(request)
    context.update({
        "launch_param_rows": launch_param_rows,
        "page_title":"Launch Parameters"
    })

    return render(request, 'views/tools/tool_launch_params.html', context)


def pubkey_addresses_view(request):
    context = helper.get_base_context(request)
    context.update({
        "page_title": "Pubkey Addresses",
        "explorers": info.get_explorers(request)
    })
    if "pubkey" in request.GET:
        pubkey = request.GET["pubkey"]
        if pubkey == "":
            messages.error(request, f"No pubkey input!")
        elif b58.validate_pubkey(pubkey):
            base_58_coins = requests.get(f"{THIS_SERVER}/api/info/base_58/").json()["results"]
            base_58_coins_list = list(base_58_coins.keys())
            address_rows = []
            
            for coin in base_58_coins_list:
                pubtype = base_58_coins[coin]["pubtype"]
                p2shtype = base_58_coins[coin]["p2shtype"]
                wiftype = base_58_coins[coin]["wiftype"]
                address_row = b58.calc_addr_tool(pubkey, pubtype, p2shtype, wiftype)
                address_row.update({"coin":coin})
                address_rows.append(address_row)
            context.update({
                "pubkey": pubkey,
                "address_rows": address_rows,
            })
        else:
            messages.error(request, f"Invalid pubkey: {pubkey}")

    return render(request, 'views/tools/tool_pubkey_addresses.html', context)


def scripthashes_from_pubkey_view(request):
    context = helper.get_base_context(request)
    context.update({
        "page_title":"Get Scripthashes from Pubkey"
    })
    if "pubkey" in request.GET:
        pubkey = request.GET["pubkey"]
        url = f"{THIS_SERVER}/api/tools/scripthashes_from_pubkey/?pubkey={pubkey}"
        resp = requests.get(url).json()

        if "error" in resp:
            messages.error(request, f"{resp['error']}")
        else:
            resp_rows = []
            for item in resp:
                key_val = item.replace("_", " ").title()
                resp_rows.append({"key":key_val, "value":resp[item]})

            context.update({
                "pubkey":pubkey,
                "resp_rows": resp_rows
            })

    return render(request, 'views/tools/tool_scripthashes_from_pubkey.html', context)


def scripthash_from_address_view(request):
    context = helper.get_base_context(request)
    context.update({
        "page_title":"Get Scripthash from Address"
    })
    if "address" in request.GET:
        address = request.GET["address"]
        url = f"{THIS_SERVER}/api/tools/scripthash_from_address/?address={address}"
        resp = requests.get(url).json()

        if "error" in resp:
            messages.error(request, f"{resp['error']}")
        else:
            resp_rows = []
            for item in resp:
                key_val = item.replace("_", " ").title()
                resp_rows.append({"key":key_val, "value":resp[item]})

            context.update({
                "address":address,
                "resp_rows": resp_rows
            })

    return render(request, 'views/tools/tool_scripthash_from_address.html', context)


def send_raw_tx_view(request):
    context = helper.get_base_context(request)
    context.update({
        "page_title":"Get Scripthashes from Pubkey",
        "mm2_coins":info.get_mm2_coins_list()
    })

    if "coin" in request.GET or "tx_hex" in request.GET:
        mm2_resp = dex.send_raw_tx(request)

        if "error" in mm2_resp:
            messages.error(request, f"{mm2_resp['error']}")
        else:
            messages.success(request, f"{mm2_resp}")


    return render(request, 'views/tools/tool_send_raw_transaction.html', context)
