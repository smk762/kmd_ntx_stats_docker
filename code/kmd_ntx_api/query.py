#!/usr/bin/env python3
import datetime
from datetime import datetime as dt
from django.db.models import Count, Sum


from kmd_ntx_api.models import notarised, kmd_supply, mined_count_daily, \
    notary_last_ntx, nn_ltc_tx, nn_social, notarised_coin_daily, \
    notarised_count_daily, notary_ntx_season, notarised_tenure, \
    scoring_epochs, mined_count_season, mined, notary_candidates, \
    notary_vote, addresses, balances, rewards_tx, coins, coin_social, \
    coin_last_ntx, coin_ntx_season, swaps, swaps_failed, seednode_version_stats
from kmd_ntx_api.serializers import seednodeVersionStatsSerializer
from kmd_ntx_api.notary_seasons import get_seasons_info
from kmd_ntx_api.logger import logger

def filter_data_basic(data, **kwargs):
    for i in kwargs:
        if kwargs[i] is not None:
            data = data.filter(i=kwargs[i])
    return data

def get_notarised_data(season=None, server=None, epoch=None, coin=None,
                        notary=None, address=None, txid=None, exclude_epoch=None,
                        min_blocktime=None, max_blocktime=None):
    logger.info("get_notarised_data")
    if txid:
        return notarised.objects.filter(txid=txid)
    else:
        data = notarised.objects.all()
    if season:
        data = data.filter(season=season)
    if server:
        data = data.filter(server=server)
    if epoch:
        data = data.filter(epoch=epoch)
    if coin:
        data = data.filter(coin=coin)
    if min_blocktime:
        data = data.filter(block_time__gte=min_blocktime)
    if max_blocktime:
        data = data.filter(block_time__lte=max_blocktime)
    if notary:
        data = data.filter(notaries__contains=[notary])
    if address:
        data = data.filter(notary_addresses__contains=[address])
    if exclude_epoch:
        data = data.exclude(epoch=exclude_epoch)
    return data


def get_kmd_supply_data(season=None, name=None, address=None):
    data = kmd_supply.objects.all()
    if season:
        data = data.filter(season=season)
    if name:
        data = data.filter(name=name)
    if address:
        data = data.filter(address=address)
    return data


# Table: Mining related tables
def get_mined_count_daily_data(season=None, notary=None, mined_date=None):
    data = mined_count_daily.objects.all()
    if mined_date:
        data = data.filter(mined_date=mined_date)
    if season:
        data = data.filter(season=season)
    if notary:
        data = data.filter(notary=notary)
    return data


def apply_filters_api(request, serializer, queryset, table=None, filter_kwargs=None):
    if not filter_kwargs:
        filter_kwargs = {}

    # handle standard column fields
    for field in serializer.Meta.fields:
        # handle both standard 'WSGIRequest' object and DRF request object
        if hasattr(request, 'query_params'):
            val = request.query_params.get(field, None)
        else:
            val = request.GET.get(field, None)
        if val is not None:
            filter_kwargs.update({field:val}) 

    # Handle extended fields
    if 'from_block' in request.GET:
        filter_kwargs.update({'block_height__gte':request.GET['from_block']}) 

    if 'to_block' in request.GET:
        filter_kwargs.update({'block_height__lte':request.GET['to_block']})  

    if 'from_timestamp' in request.GET:
        filter_kwargs.update({'block_time__gte':request.GET['from_timestamp']}) 

    if 'to_timestamp' in request.GET:
        filter_kwargs.update({'block_time__lte':request.GET['to_timestamp']})

    if table in ['mined', 'rewards_tx', 'notarised' 'kmd_supply']:
        if 'date' in request.GET:
            date = request.GET['date']
            if not date or date == 'Today':
                date = f"{datetime.date.today()}"
            date_obj = dt.strptime(date, "%Y-%m-%d")
            start = dt.timestamp(date_obj)
            end = start + 86400
            filter_kwargs.update({'block_time__gte': start }) 
            filter_kwargs.update({'block_time__lte': end })

    if table in ['notarised_coin_daily', 'notarised_count_daily']:
        if 'year' in request.GET:
            filter_kwargs.update({'notarised_date__year':request.GET['year']})  
        if 'month' in request.GET:
            months = ['January', 'February', 'March', 'April', 'May', 'June', 'July',
                      'August', 'September', 'October', 'November', 'December']
            month = months.index(request.GET['month']) + 1
            filter_kwargs.update({'notarised_date__month': month})

    if table in ['mined_count_daily']:
        if 'from_date' in request.GET:
            filter_kwargs.update({'mined_date__gte':request.GET['from_date']})  
        if 'to_date' in request.GET:
            filter_kwargs.update({'mined_date__lte':request.GET['to_date']})   

    if table in ['daily_notarised_coin', 'daily_notarised_count']:
        if 'from_date' in request.GET:
            filter_kwargs.update({'notarised_date__gte':request.GET['from_date']}) 
        if 'to_date' in request.GET:
            filter_kwargs.update({'notarised_date__lte':request.GET['to_date']})  

    if 'season' in filter_kwargs:
        if filter_kwargs["season"].isnumeric():
            filter_kwargs["season"] = f"Season_{filter_kwargs['season']}"

    if len(filter_kwargs) > 0:
        queryset = queryset.filter(**filter_kwargs)
    return queryset


def get_distinct_filters(queryset, filters=None, exclude=None, season=None):
    if not exclude:
        exclude = []
    if not filters:
        filters = []

    distinct = {}

    # Get distinct season values before filtering out other seasons
    if season and 'season' in filters:
        y = list(queryset.values_list('season', flat=True).distinct())
        distinct.update({'season': y})
        queryset = queryset.filter(season=season)

    for x in filters:
        if x not in exclude and x != 'season':
            logger.debug(f"Distinct filter: {x}")
            if x == "year":
                y = ['2022', "2021", "2020", "2019", "2018", "2017", "2016"]
            elif x == "month":
                y = ['January', 'February', 'March', 'April', 'May', 'June', 'July',
                     'August', 'September', 'October', 'November','December']
            else:                    
                y = list(queryset.values_list(x, flat=True).distinct())
                y.sort()
            distinct.update({x: y})

    return distinct



# Table: Notary/Notarisation related 
def get_notary_last_ntx_data(season=None, server=None, notary=None, coin=None):
    data = notary_last_ntx.objects.all()
    if season:
        data = data.filter(season=season)
    if server:
        data = data.filter(server=server)
    if notary:
        data = data.filter(notary=notary)
    if coin:
        data = data.filter(coin=coin)
    return data



def get_nn_ltc_tx_data(season=None, notary=None, category=None, address=None, txid=None):
    if txid:
        data = nn_ltc_tx.objects.filter(txid=txid)
    else:
        data = nn_ltc_tx.objects.all()
    if season:
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
        data = data.filter(season=season)
    if notary:
        data = data.filter(notary=notary)
    return data


def get_notarised_coins_data(season=None, server=None, epoch=None):
    data = notarised.objects.all()
    if season:
        data = data.filter(season=season)
    if server:
        data = data.filter(server=server)
    if epoch:
        data = data.filter(epoch=epoch)
    return data


def get_notarised_coin_daily_data(notarised_date=None, coin=None):
    data = notarised_coin_daily.objects.all()
    if notarised_date:
        data = data.filter(notarised_date=notarised_date)
    if coin:
        data = data.filter(coin=coin)
    return data


def get_notarised_count_daily_data(notarised_date=None, notary=None):
    data = notarised_count_daily.objects.all()
    if notarised_date:
        data = data.filter(notarised_date=notarised_date)
    if notary:
        data = data.filter(notary=notary)
    return data


def get_notary_ntx_season_data(season=None, notary=None):
    data = notary_ntx_season.objects.all()
    if season:
        data = data.filter(season=season)
    if notary:
        data = data.filter(notary=notary)
    return data


def get_notarised_tenure_data(season=None, server=None, coin=None):
    data = notarised_tenure.objects.all()

    if season:
        data = data.filter(season=season)

    if server:
        data = data.filter(server=server)

    if coin:
        data = data.filter(coin=coin)

    return data



def get_scoring_epochs_data(season=None, server=None, coin=None, epoch=None, timestamp=None):
    data = scoring_epochs.objects.all()

    if season:
        data = data.filter(season=season)

    if server:
        data = data.filter(server=server)

    if coin:
        data = data.filter(epoch_coins__contains=[coin])

    if epoch:
        data = data.filter(epoch=epoch)

    if timestamp:
        data = data.filter(epoch_start__lte=timestamp)
        data = data.filter(epoch_end__gte=timestamp)

    return data


def get_mined_count_season_data(season=None, name=None, address=None):
    data = mined_count_season.objects.all()
    if season:
        data = data.filter(season=season)
    if name:
        data = data.filter(name=name)
    if address:
        data = data.filter(address=address)
    return data


def get_mined_data(season=None, name=None, address=None, min_block=None,
                   max_block=None, min_blocktime=None, max_blocktime=None):
    data = mined.objects.all()
    if season:
        data = data.filter(season=season)
    if name:
        data = data.filter(name=name)
    if address:
        data = data.filter(address=address)
    if min_block:
        data = data.filter(block_height__gte=min_block)
    if max_block:
        data = data.filter(block_height__lte=max_block)
    if min_blocktime:
        data = data.filter(block_time__gte=min_blocktime)
    if max_blocktime:
        data = data.filter(block_time__lte=max_blocktime)
    return data


# Table: Election/Testnet tables

def get_notary_candidates_data(year=None, season=None, name=None):
    data = notary_candidates.objects.all()

    if year:
        data = data.filter(year=year)

    if season:
        data = data.filter(season=season)

    if name:
        data = data.filter(name=name)

    return data


def get_notary_vote_data(year=None, candidate=None, block=None, txid=None,
                      max_block=None, max_blocktime=None,
                      max_locktime=None, mined_by=None, valid=None,
                      min_block=None, min_blocktime=None, min_locktime=None):
    data = notary_vote.objects.all()

    if year:
        data = data.filter(year=year)

    if valid is not None:
        data = data.filter(valid=valid)

    if candidate:
        data = data.filter(candidate=candidate)

    if block:
        data = data.filter(block=block)

    if txid:
        data = data.filter(txid=txid)

    if mined_by:
        data = data.filter(mined_by=mined_by)

    if min_block:
        data = data.filter(block_height__gte=min_block)

    if min_blocktime:
        data = data.filter(block_time__gte=min_blocktime)

    if min_locktime:
        data = data.filter(lock_time__gte=min_locktime)

    if max_block:
        data = data.filter(block_height__lte=max_block)

    if max_blocktime:
        data = data.filter(block_time__lte=max_blocktime)

    if max_locktime:
        data = data.filter(lock_time__lte=max_locktime)

    return data


# Table: Wallet related

def get_addresses_data(season=None, server=None, coin=None, notary=None, address=None):
    data = addresses.objects.all()
    if season:
        data = data.filter(season=season)

    if server:
        data = data.filter(server=server)

    if notary:
        data = data.filter(notary=notary)

    if coin:
        data = data.filter(coin=coin)

    if address:
        data = data.filter(address=address)

    return data


def get_balances_data(season=None, server=None, coin=None, notary=None, address=None):
    data = balances.objects.all()
    if season:
        data = data.filter(season=season)

    if server:
        data = data.filter(server=server)

    if notary:
        data = data.filter(notary=notary)

    if coin:
        data = data.filter(coin=coin)

    if address:
        data = data.filter(address=address)

    return data


def get_rewards_data(season=None, address=None, min_value=None, min_block=None, max_block=None,
                     min_blocktime=None, max_blocktime=None, exclude_coinbase=True):
    logger.calc("get_rewards_data")
    data = rewards_tx.objects.all()

    if address:
        data = data.filter(address=address)

    if season:
        seasons_info = get_seasons_info()
        if season in seasons_info:
            data = data.filter(block_time__gte=seasons_info[season]["start_time"])
            data = data.filter(block_time__lte=seasons_info[season]["end_time"])

    if min_value:
        data = data.filter(rewards_value__gte=min_value)

    if min_block:
        data = data.filter(block_height__gte=min_block)

    if max_block:
        data = data.filter(block_height__lte=max_block)

    if min_blocktime:
        data = data.filter(block_time__gte=min_blocktime)

    if max_blocktime:
        data = data.filter(block_time__lte=max_blocktime)

    if exclude_coinbase:
        data = data.exclude(address='coinbase')

    data = data.exclude(block_height=1)

    return data


# Table: Coins related

def get_coins_data(coin=None, mm2_compatible=None, dpow_active=None):
    data = coins.objects.all()
    if coin:
        data = data.filter(coin=coin)
    if mm2_compatible:
        data = data.filter(mm2_compatible=mm2_compatible)
    if dpow_active:
        data = data.filter(dpow_active=dpow_active)
    return data


def get_coin_social_data(coin=None, season=None):
    data = coin_social.objects.all()
    if coin:
        data = data.filter(coin=coin)
    if season:
        data = data.filter(season=season)
    return data


def get_coin_last_ntx_data(season=None, server=None, coin=None):
    data = coin_last_ntx.objects.all()
    if season:
        data = data.filter(season=season)
    if server:
        data = data.filter(server=server)
    if coin:
        data = data.filter(coin=coin)
    return data


def get_coin_ntx_season_data(season=None, coin=None):
    data = coin_ntx_season.objects.all()
    if season:
        data = data.filter(season=season)
    if coin:
        data = data.filter(coin=coin)
    return data

def get_server_ntx_season_data(season=None, server=None):
    data = coin_ntx_season.objects.all()
    if season:
        data = data.filter(season=season)
    if server:
        data = data.filter(server=server)
    return data


# Table: Atomicdex swaps, swaps_failed (and extra filtering)

def get_swaps_failed_data(uuid=None):
    data = swaps_failed.objects.all()
    if uuid:
        data = data.filter(uuid=uuid)
    return data


def get_swaps_data(uuid=None):
    data = swaps.objects.all()
    if uuid:
        data = data.filter(uuid=uuid)
    return data


def get_swaps_counts(swaps_data):
    q_pairs_counts = swaps_data.values('maker_coin', 'taker_coin').annotate(
        count=Count('taker_coin')
    )

    q_pairs_volumes = swaps_data.values('maker_coin', 'taker_coin').annotate(
        swap_count=Count('maker_coin'),
        maker_amount=Sum('maker_amount'),
        taker_amount=Sum('taker_amount')
    )
    q_maker_guis = swaps_data.values(
        'maker_gui').annotate(count=Count('maker_gui'))
    q_taker_guis = swaps_data.values(
        'taker_gui').annotate(count=Count('taker_gui'))

    guis = {}

    for i in q_taker_guis:
        guis.update(
            {
                i["taker_gui"]: {
                    "taker_swaps": i["count"],
                    "maker_swaps": 0
                }
            }
        )

    for i in q_maker_guis:
        if i["maker_gui"] not in guis:
            guis.update(
                {
                    i["maker_gui"]: {
                        "maker_swaps": i["count"],
                        "taker_swaps": 0
                    }
                }
            )
        else:
            guis[i["maker_gui"]].update({"maker_swaps": i["count"]})

    pair_counts = [
        {"maker": i['maker_coin'], "taker":i['taker_coin'], "count":i['count']}
        for i in q_pairs_counts  # if i["count"] >= 10
    ]

    pair_volumes = [
        {
            "maker": i['maker_coin'],
            "taker":i['taker_coin'],
            "swap_count":i['swap_count'],
            "maker_volume":i['maker_amount'],
            "taker_volume":i['taker_amount']
        }
        for i in q_pairs_volumes  # if i["count"] >= 10
    ]

    return {
        "pair_volumes": pair_volumes,
        "pair_counts": pair_counts,
        "guis": guis
    }


def filter_swaps_coins(data, taker_coin=None, maker_coin=None):
    if taker_coin:
        data = data.filter(taker_coin=taker_coin)
    if maker_coin:
        data = data.filter(maker_coin=maker_coin)
    return data


def filter_swaps_gui(data, taker_gui=None, maker_gui=None):
    if taker_gui:
        data = data.filter(taker_gui=taker_gui)
    if maker_gui:
        data = data.filter(maker_gui=maker_gui)
    return data


def filter_swaps_version(data, taker_version=None, maker_version=None):
    if taker_version:
        data = data.filter(taker_version=taker_version)
    if maker_version:
        data = data.filter(maker_version=maker_version)
    return data


def filter_swaps_pubkey(data, taker_pubkey=None, maker_pubkey=None):
    if taker_pubkey:
        data = data.filter(taker_pubkey=taker_pubkey)
    if maker_pubkey:
        data = data.filter(maker_pubkey=maker_pubkey)
    return data


def filter_swaps_error(data, taker_error_type=None, maker_error_type=None):
    if taker_error_type:
        data = data.filter(taker_error_type=taker_error_type)
    if maker_error_type:
        data = data.filter(maker_error_type=maker_error_type)
    return data


def filter_swaps_timespan(data, from_time=None, to_time=None):
    if from_time:
        data = data.filter(timestamp__gte=from_time)
    if to_time:
        data = data.filter(timestamp__lte=to_time)
    return data



# Table: seednode_version_stats 

def get_seednode_version_stats_data(**kwargs):
    data = seednode_version_stats.objects.all()
    data = filter_kwargs(data, seednodeVersionStatsSerializer, **kwargs)
    return data


def filter_kwargs(data, serializer, **kwargs):
    std_fields = {}
    meta_fields = {}

    for i in kwargs:
        if kwargs[i]:
            if i in serializer.Meta.fields:
                std_fields.update({i:kwargs[i]})
            else:
                meta_fields.update({i:kwargs[i]})

    if len(std_fields) > 0:
        data = data.filter(**std_fields)

    if len(meta_fields) > 0:
        if 'limit' in meta_fields:
            data = data[:meta_fields['limit']]

        if 'start' in meta_fields:
            if 'end' in meta_fields:
                data = data.filter(timestamp__range=(int(meta_fields['start']), int(meta_fields['end']-1)))
            else:
                end = start + 86400
                data = data.filter(timestamp__range=(int(meta_fields['start']), int(end-1)))
        elif 'end' in meta_fields:
            start = end - 86400
            data = data.filter(timestamp__range=(int(start), int(meta_fields['end']-1)))

    return data