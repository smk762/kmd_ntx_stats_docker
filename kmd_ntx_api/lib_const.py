import requests
from django.contrib import messages

MESSAGE_TAGS = {
    messages.DEBUG: 'alert-info',
    messages.INFO: 'alert-info',
    messages.SUCCESS: 'alert-success',
    messages.WARNING: 'alert-warning',
    messages.ERROR: 'alert-danger',
}
SEASONS_INFO = {
    "Season_1": {
            "start_block":1,
            "end_block":813999,
            "start_time":1473793441,
            "end_time":1530921600,
            "notaries":[]
        },
    "Season_2": {
            "start_block":814000,
            "end_block":1443999,
            "start_time":1530921600,
            "end_time":1563148799,
            "notaries":[]
        },
    "Season_3": {
            "start_block":1444000,
            "end_block":1921999,
            "start_time":1563148800,
            "end_time":1592146799,
            "notaries":[]
        },
    "Season_4": {
            "start_block":1922000, # https://github.com/KomodoPlatform/komodo/blob/master/src/komodo_globals.h#L47 (block_time 1592172139)
            "end_block":2436999,
            "start_time":1592146800, # https://github.com/KomodoPlatform/komodo/blob/master/src/komodo_globals.h#L48
            "end_time":1617364800, # April 2nd 2021 12pm
            "post_season_end_time":1623682799,
            "notaries":[]
        },
    "Season_5": {
            "start_block":2437000,
            "end_block":3437000,
            "start_time":1623682800,
            "end_time":1773682800,
            "notaries":[]
        },
    "Season_5_Testnet": {
            "start_block":2299140,
            "end_block":2436999,
            "start_time":1615367302,
            "end_time":1618660800, # April 17th 2021 12pm,
            "notaries":[]
        }
}
# set at post season to use "post_season_end_time" for aggreagates (e.g. mining)
POSTSEASON = True


# convert timestamp to human time 
intervals = (
    ('wks', 604800),  # 60 * 60 * 24 * 7
    ('days', 86400),    # 60 * 60 * 24
    ('hrs', 3600),    # 60 * 60
    ('mins', 60),
    ('sec', 1),
    )

noMoM = ['CHIPS', 'GAME', 'HUSH3', 'EMC2', 'GIN', 'AYA', 'MCL', 'VRSC']

EXCLUDE_DECODE_OPRET_COINS = []

url = "https://raw.githubusercontent.com/gcharang/data/master/info/ecosystem.json"
r = requests.get(url)
ECO_DATA = r.json()

#TESTNET_CHAINS = ["RICK", "MORTY", "LTC"]

# COLORS

BLACK = "#000"
RED = "#DC0333"
LT_GREEN = "#2FEA8B"
LT_PURPLE = "#B541EA"
LT_BLUE = "#00E2FF"
LT_ORANGE = "#F7931A"