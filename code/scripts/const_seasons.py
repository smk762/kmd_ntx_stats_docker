#!/usr/bin/env python3.12
import sys
import json
from pathlib import Path
import requests
import time
import lib_urls as urls
from notary_pubkeys import NOTARY_PUBKEYS
from functools import cached_property, lru_cache
from logger import logger
from lib_github import gh, GH_TOKEN

# Ensure project root is on PYTHONPATH so kmd_ntx_api imports succeed when
# running scripts directly (e.g. python scripts/cron_update_epochs.py).
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from kmd_ntx_api.cache_data import cached
import time


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
        """Fetch scoring_epochs.json; cache locally for offline fallback."""
        url = urls.get_scoring_epochs_repo_url()
        cache_path = Path(__file__).resolve().parent.parent / "cache" / "scoring_epochs.json"
        cache_path.parent.mkdir(exist_ok=True)

        data = None
        sess = gh if GH_TOKEN else requests.Session()
        if not GH_TOKEN:
            logger.warning("GITHUB_TOKEN not set; fetching scoring_epochs without auth")
        logger.info("epochs_repo_data: starting fetch/cache sequence")
        try:
            # Prefer authenticated GitHub session from lib_github
            logger.info(f"Fetching scoring_epochs from {url}")
            response = sess.get(url, timeout=15)
            response.raise_for_status()
            data = response.json()
            cache_path.write_text(json.dumps(data, indent=4))
            logger.info(f"scoring_epochs fetched ({len(data)} seasons) and cached to {cache_path}")
        except (requests.RequestException, ValueError) as e:
            logger.warning(f"Failed to fetch scoring_epochs: {e}; trying cached file at {cache_path}")
            if cache_path.exists():
                try:
                    data = json.loads(cache_path.read_text())
                    logger.info("Loaded scoring_epochs from cache")
                except Exception as ee:
                    logger.error(f"Failed to read cached scoring_epochs: {ee}")
                    data = None

        if not data:
            logger.warning("scoring_epochs data empty after fetch/cache fallback")
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
        """Compute current dPoW-active coins from season start list + scoring epochs window."""
        cache_key = cached.namespaced_key("epochs", "dpow_active_coins")
        now = int(time.time())
        current_season = self.current()
        active_details = {}
        active_by_server = {current_season: {}}

        # Start with season start coins as baseline
        start_coins = self.START_COINS.get(current_season, {})
        for server, coins in start_coins.items():
            active_by_server[current_season].setdefault(server, [])
            for coin in coins:
                if coin not in active_by_server[current_season][server]:
                    active_by_server[current_season][server].append(coin)
                active_details.setdefault(coin, {"dpow": {}})
                active_details[coin]["dpow"]["server"] = server

        # Apply epochs timing: remove coins whose epoch ended; add coins whose epoch is active now
        if current_season in self.epochs_repo_data:
            servers = self.epochs_repo_data[current_season].get("Servers", {})
            for server, coins in servers.items():
                active_by_server[current_season].setdefault(server, [])
                for coin, meta in coins.items():
                    start = meta.get("start_time", 0)
                    end = meta.get("end_time", 1999999999)
                    in_window = start <= now <= end
                    if in_window and coin not in active_by_server[current_season][server]:
                        active_by_server[current_season][server].append(coin)
                        active_details.setdefault(coin, {"dpow": {}})
                        active_details[coin]["dpow"]["server"] = server
                    if not in_window and coin in active_by_server[current_season][server]:
                        active_by_server[current_season][server].remove(coin)
                        active_details.pop(coin, None)

        # Sort lists for stability
        for server in active_by_server[current_season]:
            active_by_server[current_season][server].sort()

        # Persist computed snapshot to cache (no remote fetch)
        cached.bump_epoch("epochs")
        cache_key = cached.namespaced_key("epochs", "dpow_active_coins")
        cached.refresh(key=cache_key, data=active_details, force=True, expire=900)
        return current_season, active_details, active_by_server

    def get_epoch_score(self, server, num_coins):
        if num_coins == 0:
            # Attempt a one-shot fallback count using current season server coins.
            try:
                current_season = self.current()
                server_coins = []
                if (
                    current_season in self.INFO
                    and "servers" in self.INFO[current_season]
                    and server in self.INFO[current_season]["servers"]
                ):
                    server_coins = self.INFO[current_season]["servers"][server].get("coins", [])
                if not server_coins and current_season in self.START_COINS:
                    server_coins = self.START_COINS[current_season].get(server, [])
                num_coins = len(server_coins)
            except Exception as e:
                logger.debug(f"fallback coin count failed: {e}")
            # If still empty, return 0 without warning to avoid log spam or recursion.
            if num_coins == 0:
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
