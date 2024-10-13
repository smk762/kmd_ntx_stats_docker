#!/usr/bin/env python3.12
import requests
import time
import lib_urls as urls
from notary_pubkeys import NOTARY_PUBKEYS
from functools import cached_property, lru_cache
from logger import logger


### Const Vars


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
            "THC",
        ],
        "Third_Party": ["AYA", "EMC2", "MCL", "SFUSD", "TOKEL"],
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
            "THC",
        ],
        "Third_Party": ["AYA", "CHIPS", "EMC2", "MCL", "MIL", "TOKEL", "VRSC"],
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
            "THC",
        ],
        "Third_Party": ["MCL", "TOKEL"],
    },
    "VOTE2023_Testnet": {"Main": ["DOC", "MARTY"]},
}

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

EXCLUDED_SEASONS = [
    "Season_1",
    "Season_2",
    "Season_3",
    "Unofficial",
    "Season_4",
    "Season_5",
    "Season_5_Testnet",
    "VOTE2022_Testnet",
]

class Seasons:
    def __init__(self) -> None:
        self.INFO = SEASONS_INFO
        self.START_COINS = SEASON_START_COINS
        self.NEXT_COINS = NEXT_SEASON_COINS
        self.POSTSEASON = False
        self.EXCLUDED = EXCLUDED_SEASONS
        self.populate_info()

    

    @cached_property
    def coins(self):
        data = {}
        for season in self.INFO:
            coins = []
            if season in self.START_COINS:
                for server in self.START_COINS[season]:
                    coins += self.START_COINS[season][server]
            if season in self.epochs_repo_data:
                for server in self.epochs_repo_data[season]["Servers"]:
                    for coin in self.epochs_repo_data[season]["Servers"][server]:
                        if coin not in coins:
                            coins.append(coin)
            coins = list(set(coins))
            coins.sort()
            data.update({season: coins})
        return data
    
    def season_coins(self, season):
        if season in self.coins:
            return self.coins[season]
        return []
    

    @cached_property
    def epochs_repo_data(self):
        url = urls.get_scoring_epochs_repo_url()
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
        except requests.RequestException as e:
            logger.error(f"Failed to fetch epochs repo data: {e}")
            return {}
        except ValueError as e:
            logger.error(f"Invalid JSON response: {e}")
            return {}
    
        for _season in data:
            _servers = list(data[_season]["Servers"].keys())[:]
            for _server in _servers:
                # Rename the dict keys.
                if _server == "dPoW-Mainnet":
                    data[_season]["Servers"].update(
                        {"Main": data[_season]["Servers"]["dPoW-Mainnet"]}
                    )
                    del data[_season]["Servers"]["dPoW-Mainnet"]

                elif _server == "dPoW-3P":
                    data[_season]["Servers"].update(
                        {"Third_Party": data[_season]["Servers"]["dPoW-3P"]}
                    )
                    del data[_season]["Servers"]["dPoW-3P"]
        return data

    @cached_property
    def epochs(self):
        epoch_dict = {}
        for season in self.INFO:
            epoch = 0
            season_epochs_dict = {}
            if season in self.epochs_repo_data:
                for server in self.epochs_repo_data[season]["Servers"]:
                    season_epochs_dict.update({server: {}})
                    time_breaks = self.get_epoch_time_breaks(season, server)

                    for i in range(len(time_breaks) - 1):
                        epoch = f"Epoch_{i}"
                        season_epochs_dict[server].update(
                            {
                                epoch: {
                                    "start_time": time_breaks[i],
                                    "end_time": time_breaks[i + 1] - 1,
                                    "start_event": self.get_epoch_events(
                                        season, time_breaks[i]
                                    ),
                                    "end_event": self.get_epoch_events(
                                        season, time_breaks[i + 1]
                                    ),
                                }
                            }
                        )
                        epoch_coins = self.coins_between(season, server, time_breaks[i], time_breaks[i + 1] - 1)
                        logger.calc(f"{season} {server} {epoch}")
                        season_epochs_dict[server][epoch].update(
                            {
                                "coins": epoch_coins,
                                "num_epoch_coins": len(epoch_coins),
                                "score_per_ntx": self.get_epoch_score(
                                    server, len(epoch_coins)
                                ),
                            }
                        )
                for server in ["KMD", "LTC"]:
                    season_epochs_dict.update(
                        {
                            server: {
                                server: {
                                    "start_time": self.INFO[season]["start_time"],
                                    "end_time": self.INFO[season]["end_time"],
                                    "start_event": "season start",
                                    "end_event": "season end",
                                    "coins": [server],
                                    "num_epoch_coins": 1,
                                    "score_per_ntx": self.get_epoch_score(server, 1),
                                }
                            }
                        }
                    )
            epoch_dict.update({season: season_epochs_dict})
        return epoch_dict

    @cached_property
    def notaries(self):
        notaries_dict = {}
        for season in self.INFO:
            if season in NOTARY_PUBKEYS:
                notaries = sorted(list(NOTARY_PUBKEYS[season]["Main"].keys()))
                notaries.sort()
                notaries_dict.update({season: notaries})
        return notaries_dict

    def season_notaries(self, season):
        if season in self.notaries:
            return self.notaries[season]
        return []

    def season_epochs(self, season):
        if season in self.epochs:
            return self.epochs[season]
        return {}


    def get_season_server_coins(self, season, server):
        coins = []
        if season in self.START_COINS:
            if server in self.START_COINS[season]:
                coins += self.START_COINS[season][server]
        if season in self.epochs_repo_data:
            if server in self.epochs_repo_data[season]["Servers"]:
                for coin in self.epochs_repo_data[season]["Servers"][server]:
                    if coin not in coins:
                        coins.append(coin)
        coins = list(set(coins))
        coins.sort()
        return coins

    @lru_cache(maxsize=None)
    def get_epoch_time_breaks(self, season, server):
        """Get time breaks for epochs in a season."""
        time_breaks = [self.INFO[season]["start_time"], self.INFO[season]["end_time"]]
        server_data = self.epochs_repo_data[season]["Servers"].get(server, {})
        for _, coin_data in server_data.items():
            if "start_time" in coin_data:
                time_breaks.append(coin_data["start_time"])
            if "end_time" in coin_data:
                time_breaks.append(coin_data["end_time"])
        return sorted(list(set(time_breaks)))

    @lru_cache(maxsize=None)
    def get_coin_time_ranges(self, season):
        """Determine the valid epochs for each server's coins."""
        coin_ranges = {}
        start_time = self.INFO[season]["start_time"]
        end_time = self.INFO[season]["end_time"]

        for server, coins in self.START_COINS.get(season, {}).items():
            coin_ranges[server] = {
                coin: {"start": start_time, "end": end_time}
                for coin in coins
            }

        for server, server_data in self.epochs_repo_data.get(season, {}).get("Servers", {}).items():
            for coin, coin_data in server_data.items():
                if server not in coin_ranges:
                    coin_ranges[server] = {}

                coin_ranges[server][coin] = {
                    "start": coin_data.get("start_time", start_time),
                    "end": coin_data.get("end_time", end_time),
                }
        return coin_ranges

    @lru_cache(maxsize=None)
    def get_epoch_events(self, season, timestamp):
        events = []
        for server in self.epochs_repo_data[season]["Servers"]:
            for coin in self.epochs_repo_data[season]["Servers"][server]:
                if (
                    "start_time"
                    in self.epochs_repo_data[season]["Servers"][server][coin]
                ):
                    if (
                        timestamp
                        == self.epochs_repo_data[season]["Servers"][server][coin][
                            "start_time"
                        ]
                    ):
                        events.append(f"{coin} start")
                if "end_time" in self.epochs_repo_data[season]["Servers"][server][coin]:
                    if (
                        timestamp
                        == self.epochs_repo_data[season]["Servers"][server][coin][
                            "end_time"
                        ]
                    ):
                        events.append(f"{coin} end")
                if timestamp == self.epochs_repo_data[season]["season_start"]:
                    events.append(f"season start")
                if timestamp == self.epochs_repo_data[season]["season_end"]:
                    events.append(f"season end")
        events = list(set(events))
        return ", ".join(events)

    @lru_cache(maxsize=None)
    def coins_between(self, season, server, start_time, end_time):
        """Return the valid coins for a specific epoch."""
        coin_ranges = self.get_coin_time_ranges(season).get(server, {})

        return [
            coin for coin, timespan in coin_ranges.items()
            if timespan["start"] <= start_time and timespan["end"] >= end_time
        ]


    def get_season_from_ts(self, timestamp=None):
        # Use the provided timestamp or current time
        if timestamp is None:
            timestamp = int(time.time())
        timestamp = int(timestamp)

        # Detect & convert JavaScript timestamps (in milliseconds)
        if round((timestamp / 1000) / time.time()) == 1:
            timestamp = timestamp / 1000

        current_season = "Unofficial"
        is_postseason = False

        for season in self.INFO:
            if "Testnet" not in season:  # Improved check for "Testnet"
                season_info = self.INFO[season]
                start_time = season_info["start_time"]

                # Determine the end time based on postseason availability
                end_time = season_info.get(
                    "post_season_end_time", season_info["end_time"]
                )

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

    def current(self):
        return self.get_season_from_ts()["season"]

    def get_dpow_active_info(self):
        """Get current dpow coins from repo"""
        data = requests.get(urls.get_dpow_active_coins_url()).json()["results"]
        current_season = self.current()
        current_dpow_coins = {current_season: {}}
        for _coin in data:
            if data[_coin]["dpow"]["server"] not in current_dpow_coins[current_season]:
                current_dpow_coins[current_season].update(
                    {data[_coin]["dpow"]["server"]: []}
                )
            current_dpow_coins[current_season][data[_coin]["dpow"]["server"]].append(
                _coin
            )
        return current_season, data, current_dpow_coins

    def get_epoch_score(self, server, num_coins):
        if num_coins == 0:
            logger.warning(f"Attempted to calculate score for {server} with no coins.")
            return 0
        score_map = {
            "Main": 0.8698,
            "Third_Party": 0.0977,
            "KMD": 0.0325,
            "Testnet": 1
        }
        return round(score_map.get(server, 0) / num_coins, 8)

    def populate_info(self):
        """Populate season info with notaries, coins, and servers."""
        self.populate_notary_info()
        self.populate_coin_and_server_info()
        self.set_postseason_status()
        self.set_excluded_seasons()


    def set_excluded_seasons(self):
        """Exclude future seasons until 96 hours (4 days) before start."""
        self.EXCLUDED += [
            _season for _season in self.INFO
            if self.INFO[_season]["start_time"] > time.time() - 96 * 60 * 60
        ]
        self.EXCLUDED = sorted(list(set(self.EXCLUDED)))

    def populate_notary_info(self):
        """Update season info with notary details."""
        for _season in self.INFO:
            self.INFO[_season].update({"notaries": self.notaries.get(_season, [])})


    def populate_coin_and_server_info(self):
        """Update season info with coin and server details."""
        for _season in self.INFO:
            self.INFO[_season].update({"coins": self.season_coins(_season)})
            self.update_season_servers(_season)

    def update_season_servers(self, season):
        """Helper method to update servers for a season."""
        server_ranges = self.get_coin_time_ranges(season)
        for server, ranges in server_ranges.items():
            if server in self.epochs.get(season, {}):
                self.INFO[season]["servers"].update({
                    server: {
                        "addresses": {},
                        "coins": self.get_season_server_coins(season, server),
                        "epochs": self.epochs[season][server],
                        "tenure": ranges,
                    }
                })

    def set_postseason_status(self):
        """Determine the current season and whether it's postseason."""
        current_time = time.time()
        for _season, info in self.INFO.items():
            if "Testnet" not in _season:
                if info["start_time"] < current_time:
                    if "post_season_end_time" in info:
                        if info["post_season_end_time"] > current_time:
                            self.POSTSEASON = True
                            break

SEASONS = Seasons()
