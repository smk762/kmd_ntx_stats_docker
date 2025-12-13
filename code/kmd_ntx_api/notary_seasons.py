#!/usr/bin/env python3.12
import time
from copy import deepcopy
from pathlib import Path
import json
import requests

try:
    # Full season metadata (coins/servers/epochs) maintained in scripts.
    from scripts.const_seasons import SEASONS as CONST_SEASONS
except Exception:  # pragma: no cover - optional dependency in API context
    CONST_SEASONS = None

from kmd_ntx_api.const import SINCE_INTERVALS
from kmd_ntx_api.pubkeys import NOTARY_PUBKEYS
from kmd_ntx_api.seasons import SEASONS_DATA
from kmd_ntx_api.struct import default_regions_info
from kmd_ntx_api.logger import logger
from kmd_ntx_api.cache_data import cached
from scripts import lib_urls
from scripts.lib_github import gh, GH_TOKEN

# Distinct cache keys to avoid collisions between season metadata and per-notary season lists.
SEASONS_INFO_CACHE_KEY = "notary_seasons_info"
NOTARY_SEASONS_MAP_CACHE_KEY = "notary_seasons_map"


def _current_season_has_metadata(seasons: dict) -> bool:
    """Return True when the current season has coins and populated server info."""
    if not seasons:
        return False
    try:
        current = get_season(notary_seasons=seasons)
    except Exception:
        return False
    if current not in seasons:
        return False

    season_data = seasons.get(current, {})
    if not season_data.get("coins"):
        return False

    servers = season_data.get("servers")
    if not isinstance(servers, dict) or len(servers) == 0:
        return False

    for _, meta in servers.items():
        if not isinstance(meta, dict):
            return False
        # Ensure nested info is present; empty structures also count as missing
        if not meta.get("coins"):
            return False
        if "addresses" not in meta or "epochs" not in meta:
            return False

    return True


def _write_seasons_cache(seasons: dict):
    """Persist refreshed seasons to both cache keys (legacy + current)."""
    cached.bump_epoch("seasons")
    info_key = cached.namespaced_key("seasons", SEASONS_INFO_CACHE_KEY)
    cached.refresh(data=seasons, force=True, key=info_key, expire=86400)

    # Legacy file name support (notary_seasons.json) for external consumers
    legacy_key = cached.namespaced_key("seasons", "notary_seasons")
    cached.refresh(data=seasons, force=True, key=legacy_key, expire=86400)
def load_scoring_epochs():
    """Fetch scoring_epochs (with auth if available), cache to file, and return normalized data."""
    url = lib_urls.get_scoring_epochs_repo_url()
    cache_path = Path(__file__).resolve().parent.parent / "cache" / "scoring_epochs.json"
    cache_path.parent.mkdir(exist_ok=True)

    data = None
    sess = gh if GH_TOKEN else requests.Session()
    if not GH_TOKEN:
        logger.warning("GITHUB_TOKEN not set; fetching scoring_epochs without auth")
    try:
        logger.info(f"Fetching scoring_epochs from {url}")
        resp = sess.get(url, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        cache_path.write_text(json.dumps(data, indent=4))
        logger.info(f"scoring_epochs fetched ({len(data)} seasons) and cached to {cache_path}")
    except Exception as e:
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

    # New data fetched; bump epochs namespace so dependent caches invalidate.
    try:
        cached.bump_epoch("epochs")
    except Exception:
        pass

    # Normalize server keys for downstream (dPoW-Mainnet -> Main, dPoW-3P -> Third_Party)
    for _season in data:
        servers = list(data[_season].get("Servers", {}).keys())
        for srv in servers:
            if srv == "dPoW-Mainnet":
                data[_season]["Servers"]["Main"] = data[_season]["Servers"].pop(srv)
            if srv == "dPoW-3P":
                data[_season]["Servers"]["Third_Party"] = data[_season]["Servers"].pop(srv)
    return data


# TODO: reduce calls without `notary_seasons` param
def get_season(timestamp: int | None = None, notary_seasons=None) -> str:
    # Evaluate the current time at call-time, not import-time, to avoid stale seasons.
    if timestamp is None:
        timestamp = int(time.time())
    if notary_seasons is None:
        cache_key = cached.namespaced_key("seasons", SEASONS_INFO_CACHE_KEY)
        notary_seasons = cached.get_data(cache_key, expire=86400)
    # Fallback when cache is missing or empty to avoid NoneType iteration
    if not notary_seasons:
        logger.warning("notary_seasons cache missing; falling back to SEASONS_DATA")
        notary_seasons = SEASONS_DATA
        cache_key = cached.namespaced_key("seasons", SEASONS_INFO_CACHE_KEY)
        cached.refresh(
            key=cache_key,
            data=notary_seasons,
            expire=86400,
            force=True
        )
    for season in notary_seasons:
        if 'post_season_end_time' in notary_seasons[season]:
            end_time = notary_seasons[season]['post_season_end_time']
        else:
            end_time = notary_seasons[season]['end_time']
        if timestamp >= notary_seasons[season]['start_time'] and timestamp <= end_time:
            return season
    return "Unofficial"


# TODO: reduce calls without `seasons_info` param
def get_page_season(request, seasons_info=None, default="Season_8"):
    if "season" in request.GET:
        season = request.GET["season"]
        if season.isnumeric():
            return f"Season_{request.GET['season']}"
        if seasons_info is None:
            seasons_info = get_seasons_info()
        if season.title() in seasons_info:
            return season.title()
    if default is None:
        return get_season()
    return default


# Cached
def get_notary_seasons():
    '''Only used in `notary_profile_view` (Notary Profile page)'''
    cache_key = cached.namespaced_key("seasons", NOTARY_SEASONS_MAP_CACHE_KEY)
    # Guard against cache misses returning None
    ntx_seasons = cached.get_data(cache_key, expire=86400) or {}
    if not isinstance(ntx_seasons, dict):
        logger.warning("Unexpected notary seasons cache value; resetting to empty dict")
        ntx_seasons = {}
    if not ntx_seasons:
        ntx_seasons = {}
        for season in NOTARY_PUBKEYS:
            for server in NOTARY_PUBKEYS[season]:
                for notary in NOTARY_PUBKEYS[season][server]:
                    if notary not in ntx_seasons:
                        ntx_seasons.update({notary:[]})
                    season = season.replace(".5", "")
                    ntx_seasons[notary].append(season)
        for notary in ntx_seasons:
            ntx_seasons[notary] = list(set(ntx_seasons[notary]))
            ntx_seasons[notary].sort()
        cached.bump_epoch("seasons")
        cache_key = cached.namespaced_key("seasons", NOTARY_SEASONS_MAP_CACHE_KEY)
        cached.refresh(
            data=ntx_seasons,
            key=cache_key,
            expire=86400
        )
    else:
        # Ensure on-disk cache exists even if memcache had data but file was removed
        cache_path = cached.data_path(cache_key)
        if not cache_path.exists():
            cached.refresh(
                data=ntx_seasons,
                key=cache_key,
                expire=86400,
                force=True
            )
    return ntx_seasons


def _build_seasons_from_sources() -> dict:
    """Build seasons metadata from local constants, pubkeys, and scoring epochs."""
    # Ensure const_seasons refreshes epochs/coins from cached or live scoring_epochs
    if CONST_SEASONS:
        for attr in ("epochs_repo_data", "epochs", "coins"):
            CONST_SEASONS.__dict__.pop(attr, None)
        try:
            CONST_SEASONS.populate_info()
        except Exception as e:
            logger.warning(f"const_seasons populate_info failed: {e}")

    seasons = deepcopy(SEASONS_DATA)
    const_info = getattr(CONST_SEASONS, "INFO", {}) if CONST_SEASONS else {}
    # Always attempt to load scoring_epochs (fetch + cache fallback) for epochs/coins enrichment
    scoring_epochs = load_scoring_epochs()

    for season in SEASONS_DATA:
        if season in NOTARY_PUBKEYS:
            notaries = get_season_notaries(season)
            seasons[season].update({
                "servers": {},
                "notaries": notaries,
                "regions": default_regions_info()
            })
            for notary in notaries:
                region = notary.split("_")[-1]
                if region not in seasons[season]["regions"].keys():
                    region = "DEV"
                if notary not in seasons[season]["regions"][region]['nodes']:
                    seasons[season]["regions"][region]['nodes'].append(notary)
            # Initial server keys from pubkeys
            for server in NOTARY_PUBKEYS[season]:
                seasons[season]["servers"].update({server: {}})

            # Hydrate coins / servers / epochs from const_seasons when available
            if season in const_info:
                seasons[season]["coins"] = const_info[season].get("coins", seasons[season].get("coins", []))
                # Merge server details from const_info (includes epochs/coins when fetch succeeded)
                for server, data in const_info[season].get("servers", {}).items():
                    seasons[season]["servers"][server] = data

            if CONST_SEASONS:
                start_coins = getattr(CONST_SEASONS, "START_COINS", {}).get(season, {})
                epoch_map = getattr(CONST_SEASONS, "epochs", {}).get(season, {})
                if not epoch_map and season in scoring_epochs:
                    epoch_map = scoring_epochs[season].get("Servers", {})

                # Ensure all known servers (pubkeys/start/epoch) are present
                server_keys = set(seasons[season]["servers"].keys()) | set(start_coins.keys()) | set(epoch_map.keys())
                for server in server_keys:
                    srv = seasons[season]["servers"].get(server, {})
                    srv.setdefault("addresses", {})
                    srv.setdefault("coins", [])
                    srv.setdefault("epochs", {})

                    # Overlay epochs/coins from epoch_map
                    if server in epoch_map:
                        srv["epochs"] = epoch_map[server]
                        epoch_coins = []
                        for _epoch, meta in epoch_map[server].items():
                            if isinstance(meta, dict) and "coins" in meta:
                                epoch_coins += meta["coins"]
                        srv["coins"] = list(set(srv.get("coins", []) + epoch_coins))

                    # Seed coins from start_coins if still empty
                    if not srv.get("coins") and server in start_coins:
                        srv["coins"] = start_coins[server]

                    # Sort coins for stability
                    srv["coins"] = sorted(list(set(srv.get("coins", []))))
                    seasons[season]["servers"][server] = srv

                logger.info(f"season {season}: servers={len(seasons[season]['servers'])} epoch_servers={len(epoch_map)} coins={len(seasons[season].get('coins', []))}")
                if not epoch_map:
                    logger.warning(f"season {season}: epoch_map empty; scoring_epochs may not have loaded")

                # If season-level coins missing, union all server coins
                if not seasons[season].get("coins"):
                    all_coins = []
                    for server in seasons[season]["servers"]:
                        all_coins += seasons[season]["servers"][server].get("coins", [])
                    seasons[season]["coins"] = sorted(list(set(all_coins)))
        elif season.lower().find("testnet") == -1:
            logger.warning(f"{season} not in NOTARY_PUBKEYS!")

    _write_seasons_cache(seasons)
    return seasons


def get_seasons_info() -> dict:
    """Return enriched season info; refresh cache if current season lacks metadata."""
    cache_key = cached.namespaced_key("seasons", SEASONS_INFO_CACHE_KEY)
    seasons = cached.get_data(cache_key, expire=86400)

    if not seasons:
        # Legacy file fallback (notary_seasons.json) in case current cache key is empty
        legacy_key = cached.namespaced_key("seasons", "notary_seasons")
        seasons = cached.get_data(legacy_key, expire=86400)

    if seasons:
        if not _current_season_has_metadata(seasons):
            logger.warning("notary_seasons cache missing coins/servers for current season; rebuilding from sources")
            return _build_seasons_from_sources()
        return seasons

    return _build_seasons_from_sources()


def get_season_notaries(season):
    notaries = list(NOTARY_PUBKEYS[season]["Main"].keys())
    notaries.sort()
    return notaries

# Possibly unused

def get_timespan_season(start, end):
    season = get_season()
    if not start:
        start = time.time() - SINCE_INTERVALS['day']
    if not end:
        end = time.time()
    else:
        season = get_season((end+start)/2)
    return int(float(start)), int(float(end)), season
