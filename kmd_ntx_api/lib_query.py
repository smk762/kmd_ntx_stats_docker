#!/usr/bin/env python3
import os
import time
import logging
import datetime
import random
from datetime import datetime as dt
from .models import *
from .lib_helper import *

from dotenv import load_dotenv
from django.db.models import Count, Min, Max, Sum
from kmd_ntx_api.serializers import *


load_dotenv()


def get_addresses_data(season=None, server=None, chain=None, notary=None, address=None):
    data = addresses.objects.all()
    if season:
        season = season.title()
        data = data.filter(season=season)

    if server:
        data = data.filter(server=server)

    if notary:
        data = data.filter(notary=notary)

    if chain:
        data = data.filter(chain=chain)

    if address:
        data = data.filter(address=address)

    return data.order_by('-season', 'server', 'chain', 'notary')


def get_balances_data(season=None, server=None, chain=None, notary=None, address=None):
    data = balances.objects.all()
    if season:
        season = season.title()
        data = data.filter(season=season)

    if server:
        data = data.filter(server=server)

    if notary:
        data = data.filter(notary=notary)

    if chain:
        data = data.filter(chain=chain)
    if address:
        data = data.filter(address=address)

    return data.order_by('-season', 'server', 'chain', 'notary')


# TODO: Awaiting delegation to crons / db table
def get_chain_sync_data(chain=None):
    data = chain_sync.objects.all()
    if chain:
        data = data.filter(chain=chain)
    return data


def get_coins_data(chain=None, mm2_compatible=None, dpow_active=None):
    data = coins.objects.all()
    if chain:
        data = data.filter(chain=chain)
    if mm2_compatible:
        data = data.filter(mm2_compatible=mm2_compatible)
    if dpow_active:
        data = data.filter(dpow_active=dpow_active)
    return data


def get_coin_social_data(chain=None):
    data = coin_social.objects.all()
    if chain:
        data = data.filter(chain=chain)
    return data


def get_funding_transactions_data(season=None, notary=None, category=None, chain=None):
    data = funding_transactions.objects.all()
    if season:
        season = season.title()
        data = data.filter(season=season)
    if notary:
        data = data.filter(notary=notary)
    if category:
        data = data.filter(category=category)
    if address:
        data = data.filter(chain=chain)
    return data


def get_last_notarised_data(season=None, server=None, notary=None, chain=None):
    data = last_notarised.objects.all()
    if season:
        season = season.title()
        data = data.filter(season=season)
    if server:
        data = data.filter(server=server)
    if notary:
        data = data.filter(notary=notary)
    if chain:
        data = data.filter(chain=chain)
    return data


def get_mined_count_daily_data(season=None, notary=None, mined_date=None):
    data = mined_count_daily.objects.all()
    if mined_date:
        data = data.filter(mined_date=mined_date)
    if season:
        season = season.title()
        data = data.filter(season=season)
    if notary:
        data = data.filter(notary=notary)
    return data


def get_mined_count_season_data(season=None, name=None, address=None):
    data = mined_count_season.objects.all()
    if season:
        season = season.title()
        data = data.filter(season=season)
    if name:
        data = data.filter(name=name)
    if address:
        data = data.filter(address=address)
    return data


def get_mined_data(season=None, name=None, address=None):
    data = mined.objects.all()
    if season:
        season = season.title()
        data = data.filter(season=season)
    if name:
        data = data.filter(name=name)
    if address:
        data = data.filter(address=address)
    return data


def get_nn_btc_tx_data(season=None, notary=None, category=None, address=None, txid=None):
    if txid:
        data = nn_btc_tx.objects.filter(txid=txid)
    else:
        data = nn_btc_tx.objects.all()
    if season:
        season = season.title()
        data = data.filter(season=season)
    if notary:
        data = data.filter(notary=notary)
    if category:
        data = data.filter(category=category)
    if address:
        data = data.filter(address=address)
    logger.info(data.count())
    return data


def get_nn_ltc_tx_data(season=None, notary=None, category=None, address=None, txid=None):
    if txid:
        data = nn_ltc_tx.objects.filter(txid=txid)
    else:
        data = nn_ltc_tx.objects.all()
    if season:
        season = season.title()
        data = data.filter(season=season)
    if notary:
        data = data.filter(notary=notary)
    if category:
        data = data.filter(category=category)
    if address:
        data = data.filter(address=address)
    return data


def get_nn_social_data(season=None, notary=None):
    data = nn_social.objects.all()
    if season:  
        season = season.title()
        data = data.filter(season=season)
    if notary:
        data = data.filter(notary=notary)
    return data


def get_notarised_data(season=None, server=None, epoch=None, chain=None, notary=None, address=None, txid=None):
    if txid:
        data = notarised.objects.filter(txid=txid)
    else:
        data = notarised.objects.exclude(season="Season_1").exclude(season="Season_2").exclude(season="Season_3")
    if season:
        season = season.title()
        data = data.filter(season=season)
    if server:
        data = data.filter(server=server)
    if chain:
        data = data.filter(chain=chain)
    if epoch:
        data = data.filter(epoch=epoch)
    if notary:
        data = data.filter(notaries__contains=[notary])
    if address:
        data = data.filter(notary_addresses__contains=[address])
    return data


# TODO: Is this still in use?
def get_notarised_btc_data(season=None):
    data = notarised_btc.objects.all()
    if season:
        season = season.title()
        data = data.filter(season=season)
    return data


def get_notarised_chain_daily_data(notarised_date=None, chain=None):
    data = notarised_chain_daily.objects.all()
    if notarised_date:
        data = data.filter(notarised_date=notarised_date)
    if chain:
        data = data.filter(chain=chain)
    return data


def get_notarised_chain_season_data(season=None, server=None, chain=None):
    data = notarised_chain_season.objects.all()
    if season:
        season = season.title()
        data = data.filter(season=season)
    if server:
        data = data.filter(server=server)
    if chain:
        data = data.filter(chain=chain)
    return data


def get_notarised_count_daily_data(notarised_date=None, notary=None):
    data = notarised_count_daily.objects.all()
    if notarised_date:
        data = data.filter(notarised_date=notarised_date)
    if notary:
        data = data.filter(notary=notary)
    return data


def get_notarised_count_season_data(season=None, notary=None):
    data = notarised_count_season.objects.all()
    if season:
        season = season.title()
        data = data.filter(season=season)
    if notary:
        data = data.filter(notary=notary)
    return data


def get_notarised_tenure_data(season=None, server=None, chain=None):
    data = notarised_tenure.objects.all()

    if season:
        season = season.title()
        data = data.filter(season=season)

    if server:
        data = data.filter(server=server)

    if chain:
        data = data.filter(chain=chain)

    return data


def get_rewards_data(notary=None):
    data = rewards.objects.all()

    if notary:
        data = data.filter(notary=notary)

    return data


def get_scoring_epochs_data(season=None, server=None, chain=None, epoch=None, timestamp=None):
    data = scoring_epochs.objects.all()

    if season:
        season = season.title()
        data = data.filter(season=season)

    if server:
        data = data.filter(server=server)

    if chain:
        data = data.filter(epoch_chains__contains=[chain])

    if epoch:
        data = data.filter(epoch=epoch)

    if timestamp:
        data = data.filter(epoch_start__lte=timestamp)
        data = data.filter(epoch_end__gte=timestamp)

    return data



def get_vote2021_data(candidate=None, block=None, txid=None,
                      max_block=None, max_blocktime=None,
                      max_locktime=None, mined_by=None):
    data = vote2021.objects.all()

    if candidate:
        data = data.filter(candidate=candidate)

    if block:
        data = data.filter(block=block)

    if txid:
        data = data.filter(txid=txid)

    if mined_by:
        data = data.filter(mined_by=mined_by)

    if max_block:
        data = data.filter(block_height__lte=max_block)

    if max_blocktime:
        data = data.filter(block_time__lte=max_blocktime)

    if max_locktime:
        data = data.filter(lock_time__lte=max_locktime)

    return data


