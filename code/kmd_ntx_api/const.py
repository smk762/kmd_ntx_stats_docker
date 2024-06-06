import os
import os
import sys
import json
from dotenv import load_dotenv
from django.contrib import messages
from os.path import expanduser, dirname, realpath
from pymemcache.client.base import Client

load_dotenv()
OTHER_SERVER = os.getenv("OTHER_SERVER") # IP / domain of the remote server
BASIC_PW = os.getenv("BASIC_PW")         # Simple pw for restricting views during testing

MEMCACHE_LIMIT = 250 * 1024 * 1024  # 250 MB

MM2_USERPASS = os.getenv("MM2_USERPASS")
MM2_IP = "http://mm2:7783"


MESSAGE_TAGS = {
    messages.DEBUG: 'alert-info',
    messages.INFO: 'alert-info',
    messages.SUCCESS: 'alert-success',
    messages.WARNING: 'alert-warning',
    messages.ERROR: 'alert-danger',
}


HOME = expanduser('~')
SCRIPT_PATH = dirname(realpath(sys.argv[0]))


# OPCODES CONST
OP_DUP = '76'
OP_HASH160 = 'a9'
OP_EQUALVERIFY = '88'
OP_CHECKSIG = 'ac'


# DPOW CONST
noMoM = ['CHIPS', 'GAME', 'HUSH3', 'EMC2', 'GIN', 'GLEEC-OLD', 'AYA', 'MCL', 'VRSC']
RETIRED_COINS = ["HUSH3", "RFOX", "PGT", "STBL", "PBC"]
EXCLUDE_DECODE_OPRET_COINS = []


# TEMPORAL CONST
INTERVALS = (
    ('wks', 604800),    # 60 * 60 * 24 * 7
    ('days', 86400),    # 60 * 60 * 24
    ('hrs', 3600),      # 60 * 60
    ('mins', 60),
    ('sec', 1),
)

SINCE_INTERVALS = {
    "hour": 60 * 60,
    "day": 24 * 60 * 60,
    "week": 7 * 24 * 60 * 60,
    "fortnight": 14 * 24 * 60 * 60,
    "month": 31 * 24 * 60 * 60,
    "year": 365 * 24 * 60 * 60,
}

SMARTCHAINS = ["BET", "BOTS", "CCL", "CHIPS", "CLC", "CRYPTO", "DEX",
                  "DP", "GLEEC", "HODL", "ILN", "JUMBLR", "KMD", "KOIN",
                  "LABS", "MCL", "MESH", "MGW", "MARTY", "MSHARK", "NINJA",
                  "PANGEA", "PIRATE", "REVS", "DOC", "SOULJA", "SPACE",
                  "SUPERNET", "THC", "TOKEL", "VRSC", "WSB", "ZILLA"]