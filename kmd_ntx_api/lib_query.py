#!/usr/bin/env python3
import os
import time
import logging
import datetime
import random
from datetime import datetime as dt
from .models import *
from .lib_const import *

from dotenv import load_dotenv
from django.db.models import Count, Min, Max, Sum
from kmd_ntx_api.serializers import *

logger = logging.getLogger("mylogger")

load_dotenv()


def get_addresses_data(season=None, chain=None, notary=None):
    data = addresses.objects.all()
    if season:
        data = data.filter(season=season)

    if notary:
        data = data.filter(notary=notary)

    if chain:
        data = data.filter(chain=chain)

    return data


def get_balances_data(season=None, chain=None, notary=None):
    data = balances.objects.all()
    if season:
        data = data.filter(season=season)

    if notary:
        data = data.filter(notary=notary)

    if chain:
        data = data.filter(chain=chain)

    return data


# TODO: Awaiting delegation to crons / db table
def get_chain_sync_data(chain=None):
    data = chain_sync.objects.all()
    if chain:
        data = data.filter(chain=chain)
    return data


def get_coins_data(dpow_active=None):
    data = coins.objects.all()
    if dpow_active:
        data = data.filter(dpow_active=1)
    return data


def get_coin_social_data(season=None, chain=None):
    data = coin_social.objects.all()
    if season:
        data = data.filter(season=season)
    if chain:
        data = data.filter(chain=chain)
    return data


def get_funding_transactions_data(season=None, notary=None, category=None, chain=None):
    data = funding_transactions.objects.all()
    if season:
        data = data.filter(season=season)
    if notary:
        data = data.filter(notary=notary)
    if category:
        data = data.filter(category=category)
    if address:
        data = data.filter(chain=chain)
    return data


def get_last_btc_notarised_data(season=None, notary=None):
    data = last_notarised.objects.all()
    if season:
        data = data.filter(season=season)
    if notary:
        data = data.filter(notary=notary)
    return data


def get_last_notarised_data(season=None, notary=None, chain=None):
    data = last_notarised.objects.all()
    if season:
        data = data.filter(season=season)
    if notary:
        data = data.filter(notary=notary)
    if chain:
        data = data.filter(chain=chain)
    return data


def get_mined_data(season=None, notary=None):
    data = mined.objects.all()
    if season:
        data = data.filter(season=season)
    if notary:
        data = data.filter(name=notary)
    return data


def get_mined_count_daily_data(season=None, notary=None, mined_date=None):
    data = mined_count_daily.objects.all()
    if mined_date:
        data = data.filter(mined_date=mined_date)
    if season:
        data = data.filter(season=season)
    if notary:
        data = data.filter(notary=notary)
    return data


def get_mined_count_season_data(season=None, notary=None):
    data = mined_count_season.objects.all()
    if season:
        data = data.filter(season=season)
    if notary:
        data = data.filter(notary=notary)
    return data


def get_nn_btc_tx_data(season=None, notary=None, category=None, address=None):
    data = nn_btc_tx.objects.all()
    if season:
        data = data.filter(season=season)
    if notary:
        data = data.filter(notary=notary)
    if category:
        data = data.filter(category=category)
    if address:
        data = data.filter(address=address)
    return data


def get_nn_ltc_tx_data(season=None, notary=None, category=None):
    data = nn_ltc_tx.objects.all()
    if season:
        data = data.filter(season=season)
    if notary:
        data = data.filter(notary=notary)
    if category:
        data = data.filter(category=category)
    return data


def get_nn_social_data(season=None, notary=None):
    data = nn_social.objects.all()
    if season:
        data = data.filter(season=season)
    if notary:
        data = data.filter(notary=notary)
    return data


def get_notarised_data(season=None, chain=None):
    data = notarised.objects.all()
    if season:
        data = data.filter(season=season)
    if chain:
        data = data.filter(chain=chain)
    return data


def get_notarised_btc_data(season=None):
    data = notarised_btc.objects.all()
    if season:
        data = data.filter(season=season)
    return data


def get_notarised_chain_daily_data(notarised_date=None, chain=None):
    data = notarised_chain_daily.objects.all()
    if notarised_date:
        data = data.filter(notarised_date=notarised_date)
    if chain:
        data = data.filter(chain=chain)
    return data


def get_notarised_chain_season_data(season=None, chain=None):
    data = notarised_chain_season.objects.all()
    if season:
        data = data.filter(season=season)
    if chain:
        data = data.filter(chain=chain)
    return data


def get_notarised_count_daily_data(notarised_date=None, notary=None, chain=None):
    data = notarised_count_daily.objects.all()
    if notarised_date:
        data = data.filter(notarised_date=notarised_date)
    if notary:
        data = data.filter(notary=notary)
    if chain:
        data = data.filter(chain=chain)
    return data


def get_notarised_count_season_data(season=None, notary=None):
    data = notarised_count_season.objects.all()
    if season:
        data = data.filter(season=season)
    if notary:
        data = data.filter(notary=notary)
    return data


def get_notarised_tenure_data(season=None, server=None, chain=None):
    data = notarised_tenure.objects.all()

    if season:
        data = scoring_epochs.objects.filter(season=season)

    if server:
        data = scoring_epochs.objects.filter(server=server)

    if chain:
        data = scoring_epochs.objects.filter(chain=chain)

    return data


def get_rewards_data(notary=None):
    data = rewards.objects.all()

    if notary:
        data = scoring_epochs.objects.filter(notary=notary)

    return data


def get_scoring_epochs_data(season=None, server=None, epoch=None):
    data = scoring_epochs.objects.all()

    if season:
        data = scoring_epochs.objects.filter(season=season)

    if server:
        data = scoring_epochs.objects.filter(server=server)

    if epoch:
        data = scoring_epochs.objects.filter(epoch=epoch)

    return data


