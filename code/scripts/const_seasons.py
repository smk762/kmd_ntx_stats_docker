#!/usr/bin/env python3.12
import requests
import time
import lib_urls as urls
from notary_pubkeys import NOTARY_PUBKEYS


def get_season_from_ts(timestamp=None):
    # Use the provided timestamp or current time
    if timestamp is None:
        timestamp = int(time.time())
    timestamp = int(timestamp)

    # Detect & convert JavaScript timestamps (in milliseconds)
    if round((timestamp / 1000) / time.time()) == 1:
        timestamp = timestamp / 1000

    current_season = "Unofficial"
    is_postseason = False

    for season in SEASONS_INFO:
        if "Testnet" not in season:  # Improved check for "Testnet"
            season_info = SEASONS_INFO[season]
            start_time = season_info["start_time"]

            # Determine the end time based on postseason availability
            end_time = season_info.get("post_season_end_time", season_info["end_time"])

            if start_time < timestamp <= end_time:
                current_season = season
                if (
                    "post_season_end_time" in season_info
                    and timestamp > season_info["end_time"]
                ):
                    is_postseason = True
                break  # Exit loop if season is found

    result = {"season": current_season, "is_postseason": is_postseason}

    return result


## Unused functions, kept for future reference


def get_season_start_end(season):
    if season in SEASONS_INFO:
        start_time = SEASONS_INFO[season]["start_time"]
        end_time = SEASONS_INFO[season]["end_time"]
        if "post_season_end_time" in SEASONS_INFO[season]:
            end_time = SEASONS_INFO[season]["post_season_end_time"]
        return start_time, end_time
    return 0, 0



def get_scoring_epochs_repo_data(branch="update/s8-pubkeys"):
    url = urls.get_scoring_epochs_repo_url(branch)
    repo_data = requests.get(url).json()
    for _season in repo_data:
        _servers = list(repo_data[_season]["Servers"].keys())[:]
        for _server in _servers:
            # Rename the dict keys.
            if _server == "dPoW-Mainnet":
                repo_data[_season]["Servers"].update(
                    {"Main": repo_data[_season]["Servers"]["dPoW-Mainnet"]}
                )
                del repo_data[_season]["Servers"]["dPoW-Mainnet"]

            elif _server == "dPoW-3P":
                repo_data[_season]["Servers"].update(
                    {"Third_Party": repo_data[_season]["Servers"]["dPoW-3P"]}
                )
                del repo_data[_season]["Servers"]["dPoW-3P"]
    return repo_data


def get_dpow_active_info(seasons):
    """Get current dpow coins from repo"""
    data = requests.get(urls.get_dpow_active_coins_url()).json()["results"]
    current_season = get_season_from_ts()["season"]
    current_dpow_coins = {current_season: {}}
    for _coin in data:
        if data[_coin]["dpow"]["server"] not in current_dpow_coins[current_season]:
            current_dpow_coins[current_season].update(
                {data[_coin]["dpow"]["server"]: []}
            )
        current_dpow_coins[current_season][data[_coin]["dpow"]["server"]].append(_coin)
    return current_season, data, current_dpow_coins


def populate_epochs():
    epoch_dict = {}
    for season in SEASONS_INFO:
        epoch_dict.update({season: get_season_epochs(season)})
    return epoch_dict


## 2023 Updates


def get_epoch_score(server, num_coins):
    if num_coins == 0:
        return 0
    if server == "Main":
        return round(0.8698 / num_coins, 8)
    elif server == "Third_Party":
        return round(0.0977 / num_coins, 8)
    elif server == "KMD":
        return 0.0325
    elif server == "Testnet":
        return 1
    else:
        return 0


def get_coin_time_ranges(season):
    """
    Gets scoring epochs data from dpow repo, then determines the epochs
    for each server and the coins valid during that epoch.
    """
    coin_ranges = {}
    if season in SEASON_START_COINS:
        # Initialise with full season timespan
        for server in SEASON_START_COINS[season]:
            coin_ranges.update({server: {}})
            for coin in SEASON_START_COINS[season][server]:
                coin_ranges[server].update(
                    {
                        coin: {
                            "start": SEASONS_INFO[season]["start_time"],
                            "end": SEASONS_INFO[season]["end_time"],
                        }
                    }
                )

        # Refine timespan for partial season coins
        repo_data = get_scoring_epochs_repo_data()
        if season in repo_data:
            repo_data = repo_data[season]
            for server in SEASON_START_COINS[season]:
                if server in repo_data["Servers"]:
                    for coin in repo_data["Servers"][server]:
                        if coin not in coin_ranges[server]:
                            coin_ranges[server].update(
                                {
                                    coin: {
                                        "start": SEASONS_INFO[season]["start_time"],
                                        "end": SEASONS_INFO[season]["end_time"],
                                    }
                                }
                            )
                        if "start_time" in repo_data["Servers"][server][coin]:
                            coin_ranges[server][coin].update(
                                {
                                    "start": repo_data["Servers"][server][coin][
                                        "start_time"
                                    ]
                                }
                            )
                        if "end_time" in repo_data["Servers"][server][coin]:
                            coin_ranges[server][coin].update(
                                {"end": repo_data["Servers"][server][coin]["end_time"]}
                            )

    return coin_ranges


def get_epoch_time_breaks(repo_data, season, server):
    time_breaks = [SEASONS_INFO[season]["start_time"], SEASONS_INFO[season]["end_time"]]
    for coin in repo_data["Servers"][server]:
        if "start_time" in repo_data["Servers"][server][coin]:
            time_breaks.append(repo_data["Servers"][server][coin]["start_time"])
        if "end_time" in repo_data["Servers"][server][coin]:
            time_breaks.append(repo_data["Servers"][server][coin]["end_time"])
    time_breaks = list(set(time_breaks))
    time_breaks.sort()
    return time_breaks


def get_season_epochs(season):
    epoch = 0
    epoch_dict = {}
    repo_data = get_scoring_epochs_repo_data()
    if season in repo_data:
        repo_data = repo_data[season]
        coin_ranges = get_coin_time_ranges(season)

        for server in repo_data["Servers"]:
            epoch_dict.update({server: {}})
            time_breaks = get_epoch_time_breaks(repo_data, season, server)

            for i in range(len(time_breaks) - 1):
                epoch = f"Epoch_{i}"
                epoch_dict[server].update(
                    {
                        epoch: {
                            "start_time": time_breaks[i],
                            "end_time": time_breaks[i + 1] - 1,
                            "start_event": get_epoch_events(repo_data, time_breaks[i]),
                            "end_event": get_epoch_events(
                                repo_data, time_breaks[i + 1]
                            ),
                        }
                    }
                )
                epoch_coins = get_epoch_coins(season, server, epoch_dict[server][epoch])
                epoch_dict[server][epoch].update(
                    {
                        "coins": epoch_coins,
                        "num_epoch_coins": len(epoch_coins),
                        "score_per_ntx": get_epoch_score(server, len(epoch_coins)),
                    }
                )
        for server in ["KMD", "LTC"]:
            epoch_dict.update(
                {
                    server: {
                        server: {
                            "start_time": SEASONS_INFO[season]["start_time"],
                            "end_time": SEASONS_INFO[season]["end_time"],
                            "start_event": "season start",
                            "end_event": "season end",
                            "coins": [server],
                            "num_epoch_coins": 1,
                            "score_per_ntx": get_epoch_score(server, 1),
                        }
                    }
                }
            )
    return epoch_dict


def get_epoch_events(repo_data, timestamp):
    events = []
    for server in repo_data["Servers"]:
        for coin in repo_data["Servers"][server]:
            if "start_time" in repo_data["Servers"][server][coin]:
                if timestamp == repo_data["Servers"][server][coin]["start_time"]:
                    events.append(f"{coin} start")
            if "end_time" in repo_data["Servers"][server][coin]:
                if timestamp == repo_data["Servers"][server][coin]["end_time"]:
                    events.append(f"{coin} end")
            if timestamp == repo_data["season_start"]:
                events.append(f"season start")
            if timestamp == repo_data["season_end"]:
                events.append(f"season end")

    events = list(set(events))
    return ", ".join(events)


def get_epoch_coins(season, server, epoch):
    epoch_coins = []
    coin_ranges = get_coin_time_ranges(season)
    if server in coin_ranges:
        coin_ranges = coin_ranges[server]
        for coin in coin_ranges:
            coin_start = coin_ranges[coin]["start"]
            coin_end = coin_ranges[coin]["end"]
            start_time = epoch["start_time"]
            end_time = epoch["end_time"]
            if coin_start <= start_time:
                if coin_end >= end_time:
                    epoch_coins.append(coin)
    return epoch_coins


def get_season_notaries(season):
    notaries = []
    if season in SEASONS_INFO and season in NOTARY_PUBKEYS:
        notaries = list(NOTARY_PUBKEYS[season]["Main"].keys())
        notaries.sort()
    return notaries


def get_season_coins(season):
    
    coins = []
    if season in SEASON_START_COINS:
        for server in SEASON_START_COINS[season]:
            coins += SEASON_START_COINS[season][server]
    if season in SCORING_EPOCHS_REPO_DATA:
        for server in SCORING_EPOCHS_REPO_DATA[season]["Servers"]:
            for coin in SCORING_EPOCHS_REPO_DATA[season]["Servers"][server]:
                if coin not in coins:
                    coins.append(coin)
    coins = list(set(coins))
    coins.sort()
    return coins


def get_season_server_coins(season, server):
    coins = []
    if season in SEASON_START_COINS:
        if server in SEASON_START_COINS[season]:
            coins += SEASON_START_COINS[season][server]
    if season in SCORING_EPOCHS_REPO_DATA:
        if server in SCORING_EPOCHS_REPO_DATA[season]["Servers"]:
            for coin in SCORING_EPOCHS_REPO_DATA[season]["Servers"][server]:
                if coin not in coins:
                    coins.append(coin)
    coins = list(set(coins))
    coins.sort()
    return coins

### Const Vars


SCORING_EPOCHS_REPO_DATA = get_scoring_epochs_repo_data()
EXCLUDED_SEASONS = ["Season_1", "Season_2", "Season_3", "Unofficial", "Season_4", "Season_5", "Season_5_Testnet", "VOTE2022_Testnet"]
SEASONS_INFO = {
    "Season_1": {
        "start_block": 1,
        "end_block": 813999,
        "start_time": 1473793441,
        "end_time": 1530921600,
        "servers": {},
    },
    "Season_2": {
        "start_block": 814000,
        "end_block": 1443999,
        "start_time": 1530921600,
        "end_time": 1563148799,
        "servers": {},
    },
    "Season_3": {
        "start_block": 1444000,
        "end_block": 1921999,
        "start_time": 1563148800,
        "end_time": 1592146799,
        "servers": {},
    },
    "Season_4": {
        "start_block": 1922000,
        "end_block": 2436999,
        "start_time": 1592146800,
        "end_time": 1617364800,
        "servers": {},
    },
    "Season_5": {
        "start_block": 2437000,
        "end_block": 2893460,
        "post_season_end_block": 2963329,
        "start_time": 1623682800,
        "end_time": 1651622400,
        "post_season_end_time": 1656077852,
        "servers": {},
    },
    "Season_6": {
        "start_block": 2963330,
        "end_block": 3368762,
        "start_time": 1656077853,
        "end_time": 1680911999,
        "post_season_end_time": 1688169599,
        "servers": {},
    },
    "Season_7": {
        "start_block": 3484958,
        "end_block": 4125958,
        "start_time": 1688132253,
        "end_time": 1717199999,
        "post_season_end_time": 1728049052,
        "servers": {},
    },
    "Season_8": {
        "start_block": 4125988,
        "end_block": 8888888,
        "start_time": 1728049053,
        "end_time": 1999999999,
        "post_season_end_time": 1999999999,
        "servers": {},
    },
    "VOTE2022_Testnet": {
        "start_block": 2903777,
        "end_block": 2923160,
        "start_time": 1651622400,
        "end_time": 1653436800,
        "coins": ["DOC", "MARTY"],
        "servers": {
            "Main": {
                "coins": ["DOC", "MARTY"],
                "addresses": {"DOC": {}, "MARTY": {}},
                "epochs": {
                    "Epoch_0": {
                        "start_event": "testnet start",
                        "end_event": "testnet end",
                        "start_block": 2903777,
                        "end_block": 2923160,
                        "start_time": 1651622400,
                        "end_time": 1653436800,
                        "coins": ["DOC", "MARTY"],
                    }
                },
            }
        },
    },
    "VOTE2023_Testnet": {
        "start_block": 2903777,
        "end_block": 2923160,
        "start_time": 1651622400,
        "end_time": 1653436800,
        "coins": ["DOC", "MARTY"],
        "servers": {
            "Main": {
                "coins": ["DOC", "MARTY"],
                "addresses": {"DOC": {}, "MARTY": {}},
                "epochs": {
                    "Epoch_0": {
                        "start_event": "testnet start",
                        "end_event": "testnet end",
                        "start_block": 2903777,
                        "end_block": 2923160,
                        "start_time": 1651622400,
                        "end_time": 1653436800,
                        "coins": ["DOC", "MARTY"],
                        "score_per_ntx": 1,
                    }
                },
            }
        },
    },
}


SEASON_START_COINS = {
    "Season_6": {
        "LTC": ["LTC"],
        "KMD": ["KMD"],
        "Main": [
            "BET",
            "BOTS",
            "CLC",
            "CCL",
            "CRYPTO",
            "DEX",
            "GLEEC",
            "HODL",
            "ILN",
            "JUMBLR",
            "KOIN",
            "MGW",
            "MARTY",
            "MSHARK",
            "NINJA",
            "PANGEA",
            "PIRATE",
            "REVS",
            "DOC",
            "SUPERNET",
            "THC"
        ],
        "Third_Party": [
            "AYA",
            "EMC2",
            "MCL",
            "SFUSD",
            "TOKEL"
        ]
    },
    "Season_7": {
        "LTC": ["LTC"],
        "KMD": ["KMD"],
        "Main": [
            "CLC",
            "CCL",
            "DOC",
            "GLEEC",
            "ILN",
            "KOIN",
            "MARTY",
            "NINJA",
            "PIRATE",
            "SUPERNET",
            "THC"
        ],
        "Third_Party": [
            "AYA",
            "CHIPS",
            "EMC2",
            "MCL",
            "MIL",
            "TOKEL",
            "VRSC"
        ]
    },
    "Season_8": {
        "LTC": ["LTC"],
        "KMD": ["KMD"],
        "Main": [
            "CLC",
            "CCL",
            "DOC",
            "GLEEC",
            "GLEEC-OLD",
            "ILN",
            "KOIN",
            "MARTY",
            "NINJA",
            "PIRATE",
            "SUPERNET",
            "THC"
        ],
        "Third_Party": [
            "MCL",
            "TOKEL"
        ]
    },
    "VOTE2023_Testnet": {
        "Main": [
            "DOC",
            "MARTY"
        ]
    }
}

# Exclude future seasons until about to happen.
for _season in SEASONS_INFO:
    if SEASONS_INFO[_season]["start_time"] > time.time() - 96 * 60 * 60:
        EXCLUDED_SEASONS.append(_season)




EPOCHS = populate_epochs()

# Add season coins & notaries
for _season in SEASONS_INFO:
    SEASONS_INFO[_season].update({"notaries": get_season_notaries(_season)})

for _season in SEASONS_INFO:
    SEASONS_INFO[_season].update({"coins": get_season_coins(_season)})
    _ranges = get_coin_time_ranges(_season)
    for _server in _ranges:
        if _server in EPOCHS[_season]:
            SEASONS_INFO[_season]["servers"].update(
                {
                    _server: {
                        "addresses": {},
                        "coins": get_season_server_coins(_season, _server),
                        "epochs": EPOCHS[_season][_server],
                        "teunre": _ranges[_server],
                    }
                }
            )


# Set season and if postseason
POSTSEASON = True
for _season in SEASONS_INFO:
    if _season.find("Testnet") == -1:
        if SEASONS_INFO[_season]["start_time"] < time.time():
            if "post_season_end_time" in SEASONS_INFO[_season]:
                if SEASONS_INFO[_season]["post_season_end_time"] > time.time():
                    POSTSEASON = True
                    SEASON = _season
            elif SEASONS_INFO[_season]["end_time"] > time.time():
                SEASON = _season

NEXT_SEASON_COINS = {
    "LTC": ["LTC"],
    "KMD": ["KMD"],
    "Main": [
        "CCL",
        "CLC",
        "DOC",
        "GLEEC",
        "GLEEC-OLD",
        "ILN",
        "KMD",
        "KOIN",
        "MARTY",
        "NINJA",
        "PIRATE",
        "SUPERNET",
        "THC",
    ],
    "Third_Party": ["MCL", "TKL"],
}
