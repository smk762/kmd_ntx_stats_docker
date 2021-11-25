import requests
import logging
import os
import time
import json
from dotenv import load_dotenv
from django.contrib import messages

# ENV VARS
load_dotenv()
MM2_USERPASS = os.getenv("MM2_USERPASS")
MM2_IP = "http://mm2:7783"
# set to IP or domain to allow for external imports of data to avoid API limits
OTHER_SERVER = os.getenv("OTHER_SERVER")
THIS_SERVER = os.getenv("THIS_SERVER")  # IP / domain of the local server


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
        "start_block": 1,
        "end_block": 813999,
        "start_time": 1473793441,
        "end_time": 1530921600,
        "notaries": []
    },
    "Season_2": {
        "start_block": 814000,
        "end_block": 1443999,
        "start_time": 1530921600,
        "end_time": 1563148799,
        "notaries": []
    },
    "Season_3": {
        "start_block": 1444000,
        "end_block": 1921999,
        "start_time": 1563148800,
        "end_time": 1592146799,
        "notaries": []
    },
    "Season_4": {
        # github.com/KomodoPlatform/komodo/blob/master/src/komodo_globals.h#L47
        # (block_time 1592172139)
        "start_block": 1922000,
        "end_block": 2436999,
        # github.com/KomodoPlatform/komodo/blob/master/src/komodo_globals.h#L48
        "start_time": 1592146800,
        "end_time": 1617364800,  # April 2nd 2021 12pm
        "post_season_end_time": 1623682799,
        "notaries": []
    },
    "Season_5": {
        "start_block": 2437000,
        "end_block": 3437000,
        "start_time": 1623682800,
        "end_time": 1773682800,
        "notaries": []
    }
}


# set as true to use "post_season_end_time" for aggreagates (e.g. mining)
POSTSEASON = True


# convert timestamp to human time
INTERVALS = (
    ('wks', 604800),  # 60 * 60 * 24 * 7
    ('days', 86400),    # 60 * 60 * 24
    ('hrs', 3600),    # 60 * 60
    ('mins', 60),
    ('sec', 1),
)

SINCE_INTERVALS = {
    "day": 24*3600,
    "week": 7*24*3600,
    "fortnight": 14*24*3600,
    "month": 30*24*3600,
    "year": 365*24*3600,
}


noMoM = ['CHIPS', 'GAME', 'HUSH3', 'EMC2', 'GIN', 'AYA', 'MCL', 'VRSC']
RETIRED_CHAINS = ["HUSH3", "RFOX", "PGT", "STBL", "PBC"]

EXCLUDE_DECODE_OPRET_COINS = []

# Links to ecosystem sites
url = "https://raw.githubusercontent.com/"
url += "gcharang/data/master/info/ecosystem.json"
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


# MM2 Swap contract addresses

SWAP_CONTRACTS = {
    "ETH": {
        "mainnet": {
            "swap_contract": "0x24ABE4c71FC658C91313b6552cd40cD808b3Ea80",
            "fallback_contract": "0x8500AFc0bc5214728082163326C2FF0C73f4a871",
            "gas_station": "https://ethgasstation.info/json/ethgasAPI.json"
        },
        "testnet": {
            "swap_contract": "0x6b5A52217006B965BB190864D62dc3d270F7AaFD",
            "fallback_contract": "0x7Bc1bBDD6A0a722fC9bffC49c921B685ECB84b94"
        }
    },
    "ETHR": {
        "mainnet": {
            "swap_contract": "0x24ABE4c71FC658C91313b6552cd40cD808b3Ea80",
            "fallback_contract": "0x8500AFc0bc5214728082163326C2FF0C73f4a871",
            "gas_station": "https://ethgasstation.info/json/ethgasAPI.json"
        },
        "testnet": {
            "swap_contract": "0x6b5A52217006B965BB190864D62dc3d270F7AaFD",
            "fallback_contract": "0x7Bc1bBDD6A0a722fC9bffC49c921B685ECB84b94"
        }
    },
    "MOVR": {
        "mainnet": {
            "swap_contract": "0x9130b257D37A52E52F21054c4DA3450c72f595CE",
            "fallback_contract": "0x9130b257D37A52E52F21054c4DA3450c72f595CE"
        },
        "testnet": {
            "swap_contract": "0x9130b257D37A52E52F21054c4DA3450c72f595CE",
            "fallback_contract": "0x9130b257D37A52E52F21054c4DA3450c72f595CE"
        }
    },
    "FTM": {
        "mainnet": {
            "swap_contract": "0x9130b257D37A52E52F21054c4DA3450c72f595CE",
            "fallback_contract": "0x9130b257D37A52E52F21054c4DA3450c72f595CE"
        },
        "testnet": {
            "swap_contract": "0x9130b257D37A52E52F21054c4DA3450c72f595CE",
            "fallback_contract": "0x9130b257D37A52E52F21054c4DA3450c72f595CE"
        }
    },
    "FTMT": {
        "mainnet": {
            "swap_contract": "0x9130b257D37A52E52F21054c4DA3450c72f595CE",
            "fallback_contract": "0x9130b257D37A52E52F21054c4DA3450c72f595CE"
        },
        "testnet": {
            "swap_contract": "0x9130b257D37A52E52F21054c4DA3450c72f595CE",
            "fallback_contract": "0x9130b257D37A52E52F21054c4DA3450c72f595CE"
        }
    },
    "ONE": {
        "mainnet": {
            "swap_contract": "0x9130b257D37A52E52F21054c4DA3450c72f595CE",
            "fallback_contract": "0x9130b257D37A52E52F21054c4DA3450c72f595CE"
        },
        "testnet": {
            "swap_contract": "0x9130b257D37A52E52F21054c4DA3450c72f595CE",
            "fallback_contract": "0x9130b257D37A52E52F21054c4DA3450c72f595CE"
        }
    },
    "MATIC": {
        "mainnet": {
            "swap_contract": "0x9130b257D37A52E52F21054c4DA3450c72f595CE",
            "fallback_contract": "0x9130b257D37A52E52F21054c4DA3450c72f595CE",
            "gas_station": "https://gasstation-mainnet.matic.network/"
        },
        "testnet": {
            "swap_contract": "0x73c1Dd989218c3A154C71Fc08Eb55A24Bd2B3A10",
            "fallback_contract": "0x73c1Dd989218c3A154C71Fc08Eb55A24Bd2B3A10",
            "gas_station": "https://gasstation-mumbai.matic.today/"
        }
    },
    "MATICTEST": {
        "mainnet": {
            "swap_contract": "0x9130b257D37A52E52F21054c4DA3450c72f595CE",
            "fallback_contract": "0x9130b257D37A52E52F21054c4DA3450c72f595CE",
            "gas_station": "https://gasstation-mainnet.matic.network/"
        },
        "testnet": {
            "swap_contract": "0x73c1Dd989218c3A154C71Fc08Eb55A24Bd2B3A10",
            "fallback_contract": "0x73c1Dd989218c3A154C71Fc08Eb55A24Bd2B3A10",
            "gas_station": "https://gasstation-mumbai.matic.today/"
        }
    },
    "AVAX": {
        "mainnet": {
            "swap_contract": "0x9130b257D37A52E52F21054c4DA3450c72f595CE",
            "fallback_contract": "0x9130b257D37A52E52F21054c4DA3450c72f595CE"
        },
        "testnet": {
            "swap_contract": "0x9130b257D37A52E52F21054c4DA3450c72f595CE",
            "fallback_contract": "0x9130b257D37A52E52F21054c4DA3450c72f595CE"
        }
    },
    "AVAXT": {
        "mainnet": {
            "swap_contract": "0x9130b257D37A52E52F21054c4DA3450c72f595CE",
            "fallback_contract": "0x9130b257D37A52E52F21054c4DA3450c72f595CE"
        },
        "testnet": {
            "swap_contract": "0x9130b257D37A52E52F21054c4DA3450c72f595CE",
            "fallback_contract": "0x9130b257D37A52E52F21054c4DA3450c72f595CE"
        }
    },
    "BNB": {
        "mainnet": {
            "swap_contract": "0xcCD17C913aD7b772755Ad4F0BDFF7B34C6339150",
            "fallback_contract": "0xeDc5b89Fe1f0382F9E4316069971D90a0951DB31"
        },
        "testnet": {
            "swap_contract": "0xeDc5b89Fe1f0382F9E4316069971D90a0951DB31",
            "fallback_contract": "0xcCD17C913aD7b772755Ad4F0BDFF7B34C6339150"
        }
    },
    "BNBT": {
        "mainnet": {
            "swap_contract": "0xcCD17C913aD7b772755Ad4F0BDFF7B34C6339150",
            "fallback_contract": "0xeDc5b89Fe1f0382F9E4316069971D90a0951DB31"
        },
        "testnet": {
            "swap_contract": "0xeDc5b89Fe1f0382F9E4316069971D90a0951DB31",
            "fallback_contract": "0xcCD17C913aD7b772755Ad4F0BDFF7B34C6339150"
        }
    },
    "ETH-ARB20": {
        "mainnet": {
            "swap_contract": "0x9130b257d37a52e52f21054c4da3450c72f595ce",
            "fallback_contract": "0x9130b257d37a52e52f21054c4da3450c72f595ce"
        },
        "testnet": {
            "swap_contract": "0x9130b257d37a52e52f21054c4da3450c72f595ce",
            "fallback_contract": "0x9130b257d37a52e52f21054c4da3450c72f595ce"
        }
    },
    "UBIQ": {
        "mainnet": {
            "swap_contract": "0x9130b257D37A52E52F21054c4DA3450c72f595CE",
            "fallback_contract": "0x9130b257D37A52E52F21054c4DA3450c72f595CE"
        },
        "testnet": {
            "swap_contract": "0x9130b257D37A52E52F21054c4DA3450c72f595CE",
            "fallback_contract": "0x9130b257D37A52E52F21054c4DA3450c72f595CE"
        }
    },
    "KCS": {
        "mainnet": {
            "swap_contract": "0x9130b257D37A52E52F21054c4DA3450c72f595CE",
            "fallback_contract": "0x9130b257D37A52E52F21054c4DA3450c72f595CE"
        },
        "testnet": {
            "swap_contract": "0x9130b257D37A52E52F21054c4DA3450c72f595CE",
            "fallback_contract": "0x9130b257D37A52E52F21054c4DA3450c72f595CE"
        }
    },
    "HT": {
        "mainnet": {
            "swap_contract": "0x9130b257D37A52E52F21054c4DA3450c72f595CE",
            "fallback_contract": "0x9130b257D37A52E52F21054c4DA3450c72f595CE"
        },
        "testnet": {
            "swap_contract": "0x9130b257D37A52E52F21054c4DA3450c72f595CE",
            "fallback_contract": "0x9130b257D37A52E52F21054c4DA3450c72f595CE"
        }
    },
    "OPTIMISM": {
        "mainnet": {
            "swap_contract": "0x9130b257d37a52e52f21054c4da3450c72f595ce",
            "fallback_contract": "0x9130b257d37a52e52f21054c4da3450c72f595ce"
        },
        "testnet": {
            "swap_contract": "0x9130b257d37a52e52f21054c4da3450c72f595ce",
            "fallback_contract": "0x9130b257d37a52e52f21054c4da3450c72f595ce"
        }
    },
    "QTUM": {
        "mainnet": {
            "swap_contract": "0x2f754733acd6d753731c00fee32cb484551cc15d",
            "fallback_contract": "0x2f754733acd6d753731c00fee32cb484551cc15d"
        },
        "testnet": {
            "swap_contract": "0xba8b71f3544b93e2f681f996da519a98ace0107a",
            "fallback_contract": "0xba8b71f3544b93e2f681f996da519a98ace0107a"
        }
    },
    "tQTUM": {
        "mainnet": {
            "swap_contract": "0x2f754733acd6d753731c00fee32cb484551cc15d",
            "fallback_contract": "0x2f754733acd6d753731c00fee32cb484551cc15d"
        },
        "testnet": {
            "swap_contract": "0xba8b71f3544b93e2f681f996da519a98ace0107a",
            "fallback_contract": "0xba8b71f3544b93e2f681f996da519a98ace0107a"
        }
    },
    "ARB": {
        "mainnet": {
            "swap_contract": "0x9130b257d37a52e52f21054c4da3450c72f595ce",
            "fallback_contract": "0x9130b257d37a52e52f21054c4da3450c72f595ce"
        },
        "testnet": {
            "swap_contract": "0x9130b257d37a52e52f21054c4da3450c72f595ce",
            "fallback_contract": "0x9130b257d37a52e52f21054c4da3450c72f595ce"
        }
    },
    "OPT": {
        "mainnet": {
            "swap_contract": "0x9130b257d37a52e52f21054c4da3450c72f595ce",
            "fallback_contract": "0x9130b257d37a52e52f21054c4da3450c72f595ce"
        },
        "testnet": {
            "swap_contract": "0x9130b257d37a52e52f21054c4da3450c72f595ce",
            "fallback_contract": "0x9130b257d37a52e52f21054c4da3450c72f595ce"
        }
    },
    "SBCH": {
        "mainnet": {
            "swap_contract": "0x25bF2AAB8749AD2e4360b3e0B738f3Cd700C4D68",
            "fallback_contract": "0x25bF2AAB8749AD2e4360b3e0B738f3Cd700C4D68"
        },
        "testnet": {
            "swap_contract": "0x25bF2AAB8749AD2e4360b3e0B738f3Cd700C4D68",
            "fallback_contract": "0x25bF2AAB8749AD2e4360b3e0B738f3Cd700C4D68"
        }
    }
}
