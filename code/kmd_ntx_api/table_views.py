#!/usr/bin/env python3
import datetime
import random
from django.shortcuts import render
from kmd_ntx_api.logger import logger
from kmd_ntx_api.context import get_base_context

def addresses_table_view(request):
    context = get_base_context(request)
    context.update({
        "page_title": f"Source: Addresses",
        "table": f"addresses",
        "endpoint": "/api/table/addresses/",
        "filters": ["season", "server", "notary", "coin"],
        "required": {
            "season": context['season'],
            "server": "Main"
        },
        "hidden": [],
        "columns": {
            "season": "",
            "server": "Server",
            "notary": "Notary",
            "coin": "Coin",
            "address": "Address / Pubkey"
        }
    })
    return render(request, 'components/tables/generic_source/addresses_table.html', context)
 

def balances_table_view(request):
    context = get_base_context(request)
    context.update({
        "page_title": f"Source: Balances",
        "table": f"balances",
        "endpoint": "/api/table/balances/",
        "filters": ["season", "server", "notary", "coin"],
        "required": {
            "season": context['season'],
            "server": "Main"
        },
        "order": [[ 1, "asc" ], [ 3, "asc" ]],
        "columns": {
            "season": "",
            "coin": "Coin",
            "server": "Server",
            "notary": "Notary",
            "address": "Address",
            "balance": "Balance",
            "update_time": "Since Updated"
        }
    })
    return render(request, 'components/tables/generic_source/balances_table.html', context)
 

def coin_last_ntx_table_view(request):
    context = get_base_context(request)
    context.update({
        "page_title": f"Source: Last Coin Ntx",
        "table": f"coin_last_ntx",
        "endpoint": "/api/table/coin_last_ntx/",
        "filters": ["season", "server"],
        "required": {"season": context['season']},
        "order": [[ 3, "desc" ], [ 2, "asc" ]],
        "columns": {
            "season": "",
            "server": "",
            "coin": "Coin",
            "kmd_ntx_blockheight": "Ntx Height",
            "kmd_ntx_blockhash": "",
            "ac_ntx_height": "SC Height",
            "ac_ntx_blockhash": "",
            "kmd_ntx_txid": "Ntx Txid",
            "notaries": "Notaries",
            "opret": "OP Return",
            "kmd_ntx_blocktime": "Time Since"
        }
    })
    return render(request, 'components/tables/generic_source/coin_last_ntx_table.html', context)


def coin_ntx_season_table_view(request):
    context = get_base_context(request)
    context.update({
        "page_title": f"Source: Coin Ntx Season",
        "table": f"coin_ntx_season",
        "endpoint": "/api/table/coin_ntx_season/",
        "filters": ["season"],
        "required": {"season": context['season']},
        "order": [ 1, "asc" ],
        "columns": {
            "season": "",
            "coin": "Coin",
            "ntx_count": "Season Count",
            "ntx_score": "Season Score",
            "pct_of_season_ntx_count": "Ntx Count %",
            "pct_of_season_ntx_score": "Ntx Score %",
            "timestamp": "Since Updated"
        }
    })
    return render(request, 'components/tables/generic_source/coin_ntx_season_table.html', context)


def mined_table_view(request):
    logger.info("init")
    context = get_base_context(request)
    logger.info("got context")
    context.update({
        "page_title": f"Source: Mined",
        "table": f"mined",
        "endpoint": "/api/table/mined/",
        "filters": ["name", "category", "date"],
        "required": {"date": f"{datetime.date.today()}"},
        "order": [3, "desc"],
        "columns": {
            "name": "Mined By",
            "address": "",
            "category": "",
            "block_height": "Block Height",
            "value": "KMD Mined",
            "txid": "",
            "usd_price": "USD Value",
            "block_time": "Time Since"
        }
    })
    return render(request, 'components/tables/generic_source/mined_table.html', context)


def mined_count_daily_table_view(request):
    context = get_base_context(request)
    context.update({
        "page_title": f"Source: Mining by Date",
        "table": f"mined_count_daily",
        "endpoint": "/api/table/mined_count_daily/",
        "filters": ["mined_date"],
        "required": {"mined_date": f"{datetime.date.today()}"},
        "order": [[0, "desc"], [1, "asc"]],
        "columns": {
            "notary": "Notary",
            "blocks_mined": "Blocks Mined",
            "sum_value_mined": "KMD Mined",
            "usd_price": "USD Value",
            "mined_date": "Date Mined",
        }
    })
    return render(request, 'components/tables/generic_source/mined_count_daily_table.html', context)


def mined_count_season_table_view(request):
    context = get_base_context(request)
    context.update({
        "season": "",
        "paging": False,
        "page_title": f"Source: Mining by Season",
        "table": f"mined_count_season",
        "endpoint": "/api/table/mined_count_season/",
        "filters": ["season"],
        "required": {"season": context['season']},
        "order": [ 6, "desc" ],
        "columns": {
            "name": "Name",
            "address": "",
            "blocks_mined": "Blocks Mined",
            "sum_value_mined": "KMD Mined",
            "max_value_mined": "Biggest Block",
            "max_value_txid": "",
            "last_mined_block": "Last Block",
            "last_mined_blocktime": "Time Since"
        }
    })
    return render(request, 'components/tables/generic_source/mined_count_season_table.html', context)


def nn_ltc_tx_table_view(request):
    context = get_base_context(request)
    context.update({
        "season": "",
        "paging": False,
        "page_title": f"Source: Notary LTC Tx",
        "table": f"nn_ltc_tx",
        "endpoint": "/api/table/nn_ltc_tx/",
        "filters": ["season", "notary", "category"],
        "required": {
            "season": context['season'],
            "notary": random.choice(context['notaries']),
        },
        "order": [[4, "desc"], [7, "asc"]],
        "columns": {
            "season": "",
            "category": "Category",
            "notary": "Notary",
            "txid": "",
            "block_height": "Block Height",
            "address": "",
            "num_inputs": "Inputs",
            "input_index": "",
            "input_sats": "Sent",
            "num_outputs": "Outputs",
            "output_index": "",
            "output_sats": "Received",
            "fees": "Fees",
            "block_time": "Time Since"
        }
    })
    return render(request, 'components/tables/generic_source/nn_ltc_tx_table.html', context)


def notarised_table_view(request):
    context = get_base_context(request)
    context.update({
        "page_title": f"Source: Notarised",
        "table": f"notarised",
        "endpoint": "/api/table/notarised/",
        "filters": ["season", "coin", "date"],
        "required": {
            "season": context['season'],
            "coin": "KMD",
            "date": f"{datetime.date.today()}"
        },
        "order": [ 5, "desc" ],
        "columns": {
            "season": "",
            "server": "",
            "epoch": "",
            "txid": "",
            "coin": "Coin",
            "block_height": "Ntx Height",
            "ac_ntx_height": "SC Height",
            "notaries": "Notaries",
            "opret": "OP Return",
            "score_value": "Ntx Score",
            "block_time": "Time Since"
        }
    })
    return render(request, 'components/tables/generic_source/notarised_table.html', context)


def notary_ntx_season_table_view(request):
    context = get_base_context(request)
    context.update({
        "page_title": f"Source: Notary Ntx Season",
        "table": f"notary_ntx_season",
        "paging": 'false',
        "endpoint": "/api/table/notary_ntx_season/",
        "filters": ["season"],
        "required": {"season": context['season']},
        "order": [ 1, "asc" ],
        "columns": {
            "season": "",
            "notary": "Notary",
            "ntx_count": "Season Count",
            "ntx_score": "Season Score",
            "pct_of_season_ntx_count": "Ntx Count %",
            "pct_of_season_ntx_score": "Ntx Score %",
            "timestamp": "Since Updated"
        }
    })
    return render(request, 'components/tables/generic_source/notary_ntx_season_table.html', context)


def notarised_coin_daily_table_view(request):
    context = get_base_context(request)
    context.update({
        "page_title": f"Source: Coin Ntx (Date)",
        "table": f"notarised_coin_daily",
        "endpoint": "/api/table/notarised_coin_daily/",
        "filters": ['coin', 'year', 'month'],
        "required": {},
        "order": [[2, "desc"], [0, "asc"]],
        "columns": {
            "coin": "Coin",
            "ntx_count": "Ntx Count",
            "notarised_date": "Ntx Date"
        }
    })
    return render(request, 'components/tables/generic_source/notarised_coin_daily_table.html', context)


def notarised_count_daily_table_view(request):
    context = get_base_context(request)
    context.update({
        "page_title": f"Source: Notary Ntx (Date)",
        "table": f"notarised_count_daily",
        "endpoint": "/api/table/notarised_count_daily/",
        "filters": ['season', 'notary', 'year', 'month'],
        "required": {"season": context['season']},
        "order": [[7, "desc"], [1, "asc"]],
        "columns": {
            "season": "",
            "notary": "Notary",
            "master_server_count": "KMD to LTC",
            "main_server_count": "Main to KMD",
            "third_party_server_count": "3P to KMD",
            "other_server_count": "Unofficial",
            "total_ntx_count": "Total NTX",
            "notarised_date": "Ntx Date"
        }
    })
    return render(request, 'components/tables/generic_source/notarised_count_daily_table.html', context)


def notary_last_ntx_table_view(request):
    context = get_base_context(request)
    context.update({
        "page_title": f"Source: Last Notary Ntx",
        "table": f"notary_last_ntx",
        "endpoint": "/api/table/notary_last_ntx/",
        "filters": ["season", "server", "notary", "coin"],
        "required": {
            "season": context['season'],
            "server": "Main"
        },
        "order": [[ 4, "desc" ], [ 2, "asc" ], [ 3, "asc" ]],
        "columns": {
            "season": "",
            "server": "",
            "coin": "Coin",
            "notary": "Notary",
            "kmd_ntx_blockheight": "Ntx Height",
            "kmd_ntx_blockhash": "",
            "ac_ntx_height": "SC Height",
            "ac_ntx_blockhash": "",
            "kmd_ntx_txid": "Ntx Txid",
            "notaries": "Notaries",
            "opret": "OP Return",
            "kmd_ntx_blocktime": "Time Since"
        }
    })
    return render(request, 'components/tables/generic_source/notary_last_ntx_table.html', context)


def server_ntx_season_table_view(request):
    context = get_base_context(request)
    context.update({
        "page_title": f"Source: Server Ntx Season",
        "table": f"server_ntx_season",
        "endpoint": "/api/table/server_ntx_season/",
        "filters": ["season"],
        "required": {"season": context['season']},
        "order": [ 1, "asc" ],
        "columns": {
            "season": "",
            "server": "Server",
            "ntx_count": "Season Count",
            "ntx_score": "Season Score",
            "pct_of_season_ntx_count": "Ntx Count %",
            "pct_of_season_ntx_score": "Ntx Score %",
            "timestamp": "Since Updated"
        }
    })
    return render(request, 'components/tables/generic_source/server_ntx_season_table.html', context)


def scoring_epochs_table_view(request):
    context = get_base_context(request)
    context.update({
        "page_title": f"Source: Scoring Epochs",
        "table": f"scoring_epochs",
        "endpoint": "/api/table/scoring_epochs/",
        "filters": ['season'],
        "required": {"season": context['season']},
        "paging": False,
        "order": [[ 0, 'desc' ], [ 1, 'asc' ], [ 2, 'asc' ]],
        "columns": {
            "season": "",
            "server": "Server",
            "epoch": "Epoch",
            "epoch_start": "Start Time",
            "start_event": "Start Event",
            "epoch_end": "End Time",
            "end_event": "End Event",
            "epoch_coins": "Epoch Coins",
            "score_per_ntx": "Score per NTX"
        }
    })
    return render(request, 'components/tables/generic_source/scoring_epochs_table.html', context)

