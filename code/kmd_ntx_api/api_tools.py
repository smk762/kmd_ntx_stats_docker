#!/usr/bin/env python3
import kmd_ntx_api.lib_helper as helper
import kmd_ntx_api.lib_tools as tools
import kmd_ntx_api.serializers as serializers


def addr_from_base58_tool(request):
    params = serializers.addrFromBase58Serializer.Meta.fields
    resp = tools.get_addr_from_base58(request)
    return helper.json_resp(resp, None, params)


def address_conversion_tool(request):
    params = ["address"]
    resp = tools.get_address_conversion(request)
    return helper.json_resp(resp, None, params)


def address_from_pubkey_tool(request):
    params = ["coin", "pubkey"]
    resp = tools.get_address_from_pubkey(request)
    return helper.json_resp(resp, None, params)


def decode_op_return_tool(request):
    params = ["OP_RETURN"]
    resp = tools.get_decode_op_return(request)
    return helper.json_resp(resp, None, params)


def kmd_rewards_tool(request):
    resp = tools.get_kmd_rewards(request)
    filters = ["address"]
    if 'ignore_errors' in request.GET:
        return helper.json_resp(resp, filters, None, True)
    return helper.json_resp(resp, filters)


def pubkey_utxos_tool(request):
    filters = ["coin", "pubkey"]
    resp = tools.get_pubkey_utxos(request)
    return helper.json_resp(resp, filters)


def send_raw_tx_tool(request):
    params = ["coin", "raw_hex"]
    resp = tools.get_send_raw_tx(request)
    return helper.json_resp(resp, None, params)


def scripthash_from_address_tool(request):
    filters = ["address"]
    resp = tools.get_scripthash_from_address(request)
    return helper.json_resp(resp, filters)


def scripthashes_from_pubkey_tool(request):
    resp = tools.get_scripthashes_from_pubkey(request)
    filters = ["pubkey"]
    return helper.json_resp(resp, filters)
