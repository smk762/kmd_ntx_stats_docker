#!/usr/bin/env python3
import requests
from django.http import JsonResponse


def faucet_balance_status(request):
    resp = requests.get(f"https://faucet.komodo.earth/rm_faucet_balances").json()
    return JsonResponse(resp)


def faucet_pending_tx_status(request):
    resp = requests.get(f"https://faucet.komodo.earth/show_pending_tx").json()
    return JsonResponse(resp)


def faucet_show_db_status(request):
    resp = requests.get(f"https://faucet.komodo.earth/show_faucet_db").json()
    return JsonResponse(resp)


def faucet_address_payments_status(request):
    if "address" in request.GET:
        address = request.GET["address"]
        resp = requests.get(f"https://faucet.komodo.earth/show_db_addr/{address}").json()
    else:
        resp = {
        "error": "You need to specify an address like `?address=RVoEJTxKqBkW9KLFiQHrahxYmcJNtEu2Ui`"
        }
    return JsonResponse(resp)


def notaryfaucet_balance_status(request):
    resp = requests.get("https://notaryfaucet.dragonhound.tools/rm_notaryfaucet_balances").json()
    return JsonResponse(resp)


def notaryfaucet_pending_tx_status(request):
    resp = requests.get("https://notaryfaucet.dragonhound.tools/show_pending_tx").json()
    return JsonResponse(resp)


def notaryfaucet_show_db_status(request):
    resp = requests.get("https://notaryfaucet.dragonhound.tools/show_notaryfaucet_db").json()
    return JsonResponse(resp)


def notaryfaucet_address_payments_status(request):
    if "address" in request.GET:
        address = request.GET["address"]
        resp = requests.get(f"https://notaryfaucet.dragonhound.tools/show_db_addr/{address}").json()
    else:
        resp = {
        "error": "You need to specify an address like `?address=RVoEJTxKqBkW9KLFiQHrahxYmcJNtEu2Ui`"
        }
    return JsonResponse(resp)
