#!/usr/bin/env python3
from kmd_ntx_api.tools import get_addr_from_base58, get_address_conversion, \
    get_address_from_pubkey, get_decode_op_return, get_pubkey_utxos, \
    get_scripthash_from_address, get_scripthashes_from_pubkey, get_explorer_status
from kmd_ntx_api.serializers import addrFromBase58Serializer
from kmd_ntx_api.raw_transaction import send_raw_tx
from kmd_ntx_api.helper import json_resp, \
    get_notary_list, safe_div, \
    get_or_none, get_page_server, \
    pad_dec_to_hex, get_mainnet_coins, get_third_party_coins, items_row_to_dict
from kmd_ntx_api.cron import get_time_since

def addr_from_base58_tool(request):
    params = addrFromBase58Serializer.Meta.fields
    resp = get_addr_from_base58(request)
    return json_resp(resp, None, params)


def address_conversion_tool(request):
    params = ["address"]
    resp = get_address_conversion(request)
    return json_resp(resp, None, params)


def address_from_pubkey_tool(request):
    params = ["coin", "pubkey"]
    resp = get_address_from_pubkey(request)
    return json_resp(resp, None, params)


def decode_op_return_tool(request):
    params = ["OP_RETURN"]
    resp = get_decode_op_return(request)
    return json_resp(resp, None, params)


def pubkey_utxos_tool(request):
    filters = ["coin", "pubkey"]
    resp = get_pubkey_utxos(request)
    return json_resp(resp, filters)


def send_raw_tx_tool(request):
    params = ["coin", "raw_hex"]
    resp = send_raw_tx(request)
    return json_resp(resp, None, params)


def scripthash_from_address_tool(request):
    filters = ["address"]
    resp = get_scripthash_from_address(request)
    return json_resp(resp, filters)


def scripthashes_from_pubkey_tool(request):
    resp = get_scripthashes_from_pubkey(request)
    filters = ["pubkey"]
    return json_resp(resp, filters)


def explorer_status_tool(request):
    resp = get_explorer_status()
    filters = []
    return json_resp(resp, filters)
