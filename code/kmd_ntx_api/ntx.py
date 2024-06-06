import time
from kmd_ntx_api.query import get_notarised_data, get_notarised_tenure_data
from kmd_ntx_api.cron import days_ago
from kmd_ntx_api.cache_data import get_from_memcache, refresh_cache
from kmd_ntx_api.logger import logger

def get_notarised_date(season=None, server=None, coin=None, notary=None, last_24hrs=True):
    logger.info("get_notarised_date")
    try:
        return get_notarised_data(season, server, None, coin, notary).filter(block_time__gt=str(days_ago(1))).order_by('-block_time')
    except Exception as e:
        logger.warning(e)

def get_ntx_tenure_table(request):
    tenure_data = get_notarised_tenure_data().values()
    data = []
    for item in tenure_data:
        start_time = item["official_start_block_time"]
        end_time = item["official_end_block_time"]
        now = time.time()
        if end_time > now:
            end_time = now
        ntx_days = (end_time - start_time) / 86400
        item.update({
            "ntx_days": ntx_days
        })
        data.append(item)
    return data

def get_ntx_count_season(notarised_data):
    cache_key = "ntx_count_season"
    data = get_from_memcache(cache_key, expire=300)
    if data is None:
        data = notarised_data.count()
        refresh_cache(data={"val": data}, force=True, key=cache_key, expire=300)
        return data
    else:
        return data["val"]

def get_ntx_count_24hr(notarised_data):
    cache_key = "ntx_count_season"
    data = get_from_memcache(cache_key, expire=300)
    if data is None:
        data = notarised_data.filter(block_time__gt=str(days_ago(1))).count()
        refresh_cache(data={"val": data}, force=True, key=cache_key, expire=300)
        return data
    else:
        return data["val"]