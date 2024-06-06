
import time
from kmd_ntx_api.const import SINCE_INTERVALS, INTERVALS

# Time related functions
def now():
    return int(time.time())


def days_ago(days=1):
    return now() - SINCE_INTERVALS['day'] * days


def get_time_since(timestamp):
    if timestamp == 0:
        return -1, "Never"
    sec_since = now() - int(timestamp)
    dms_since = day_hr_min_sec(sec_since)
    return sec_since, dms_since


def day_hr_min_sec(seconds, granularity=2):
    '''Not used outside this file'''
    result = []
    for name, count in INTERVALS:
        value = seconds // count
        if value:
            seconds -= value * count
            if value == 1:
                name = name.rstrip('s')
            result.append("{} {}".format(value, name))
    return ', '.join(result[:granularity])

