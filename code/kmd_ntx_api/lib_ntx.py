
from kmd_ntx_api.lib_const import *
import kmd_ntx_api.lib_query as query

def get_notarised_date(season=None, server=None, coin=None, notary=None, last_24hr=False):
    if last_24hr:
        day_ago = int(time.time()) - SINCE_INTERVALS['day']
    else:
        day_ago = int(time.time()) - SINCE_INTERVALS['day']
    return query.get_notarised_data(season, server, None, coin, notary).filter(block_time__gt=str(day_ago)).order_by('-block_time')
