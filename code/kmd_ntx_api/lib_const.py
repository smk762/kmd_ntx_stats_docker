import requests
import logging
import os
import time
import json
from dotenv import load_dotenv
from django.contrib import messages

# ENV VARS
load_dotenv()
OTHER_SERVER = os.getenv("OTHER_SERVER") # set to IP or domain to allow for external imports of data to avoid API limits
THIS_SERVER = os.getenv("THIS_SERVER") # IP / domain of the local server


logger = logging.getLogger("mylogger")


MESSAGE_TAGS = {
    messages.DEBUG: 'alert-info',
    messages.INFO: 'alert-info',
    messages.SUCCESS: 'alert-success',
    messages.WARNING: 'alert-warning',
    messages.ERROR: 'alert-danger',
}

if time.time() > 1592146800:
    SEASON = "Season_4"
if time.time() > 1623682800:
    SEASON = "Season_5"


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
        }
}


# set at post season to use "post_season_end_time" for aggreagates (e.g. mining)
POSTSEASON = True


# convert timestamp to human time 
INTERVALS = (
    ('wks', 604800),  # 60 * 60 * 24 * 7
    ('days', 86400),    # 60 * 60 * 24
    ('hrs', 3600),    # 60 * 60
    ('mins', 60),
    ('sec', 1),
    )


noMoM = ['CHIPS', 'GAME', 'HUSH3', 'EMC2', 'GIN', 'AYA', 'MCL', 'VRSC']
RETIRED_CHAINS = ["HUSH3", "RFOX", "PGT", "STBL", "PBC"]

EXCLUDE_DECODE_OPRET_COINS = []

# Links to ecosystem sites
url = "https://raw.githubusercontent.com/gcharang/data/master/info/ecosystem.json"
r = requests.get(url)
ECO_DATA = r.json()


# KMD REWARDS CONSTANTS
KOMODO_ENDOFERA = 7777777
LOCKTIME_THRESHOLD = 500000000
MIN_SATOSHIS = 1000000000
ONE_MONTH_CAP_HARDFORK = 1000000
ONE_HOUR = 60
ONE_MONTH = 31 * 24 * 60
ONE_YEAR = 365 * 24 * 60
DEVISOR = 10512000

DISQUALIFIED = ["etszombi_AR", "etszombi_EU",
                "fullmoon_AR", "fullmoon_NA", "fullmoon_SH",
                "chainmakers_NA", "jorian_EU", "phba2061_EU", "peer2cloud_AR",
                "pungocloud_SH", "starfleet_EU", "swisscertifiers_EU",
                "titomane_AR", "titomane_EU", "titomane_SH", "uer2_NA"]
# COLORS
BLACK = "#000"
RED = "#DC0333"
OTHER_COIN_COLOR = "#c58c47"
MAIN_COLOR = "#115621"
THIRD_PARTY_COLOR = "#2b53ad"
LT_BLUE = "#00E2FF"
AR_REGION = '#3C819D'
EU_REGION = '#B3BA41'
NA_REGION = '#13BF3E'
SH_REGION = '#B93429'
DEV_REGION = '#5D38CA'


OP_DUP = b'76'
OP_HASH160 = b'a9'
OP_EQUALVERIFY = b'88'
OP_CHECKSIG = b'ac'