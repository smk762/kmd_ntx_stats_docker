from kmd_ntx_api.cache_data import cached
from kmd_ntx_api.info import get_dpow_server_coins_info
from kmd_ntx_api.notary_seasons import get_season
from kmd_ntx_api.query import get_scoring_epochs_data
from kmd_ntx_api.logger import logger

def is_testnet(coin):
    coins_config = cached.get_data("coins_config_cache")
    return coins_config[coin]["is_testnet"]


def get_dpow_coins_dict(season=None, as_list=False):
    if season is None:
        season = get_season()
    # Intended for season use only. For more filtering, use 'get_dpow_coins_list'
    logger.info(f"get_dpow_coins_dict(season={season}, list={as_list}):")
    dpow_main_coins = get_dpow_server_coins_info(season=season, server="Main")
    dpow_3p_coins = get_dpow_server_coins_info(season=season, server="Third_Party")
    if as_list:
        return dpow_main_coins + dpow_3p_coins
    dpow_coins_dict = {
        "Main": dpow_main_coins,
        "Third_Party": dpow_3p_coins
    }
    return dpow_coins_dict


def get_dpow_coins_list(season=None, server=None, epoch=None, include_kmd=False):
    logger.info(f"get_dpow_coins_list {season}")
    dpow_coins = get_scoring_epochs_data(season, server, None, epoch).values('epoch_coins')
    coins_list = []
    for item in dpow_coins:
        coins_list += item['epoch_coins']

    # Fallback/merge: include currently-active dPoW coins from cached snapshot to capture late additions.
    try:
        cache_key = cached.namespaced_key("epochs", "dpow_active_coins")
        active_details = cached.get_data(cache_key, expire=300) or {}
        if server:
            extra = [c for c, meta in active_details.items() if meta.get("dpow", {}).get("server") == server]
        else:
            extra = list(active_details.keys())
        coins_list += extra
    except Exception:
        pass

    if include_kmd:
        if server in ["Main", None]:
            coins_list.append("KMD")
            coins_list.append("LTC")
    coins_list = list(set(coins_list))
    coins_list.sort()
    return coins_list


def get_dpow_coin_server(season, coin):
    if season.find("Testnet") != -1:
        return "Main"
    if coin in ["KMD", "BTC", "LTC"]:
        return coin
    dpow_coins_dict = get_dpow_coins_dict(season)
    for server in dpow_coins_dict:
        if coin in dpow_coins_dict[server]:
            return server
    return "Unofficial"
