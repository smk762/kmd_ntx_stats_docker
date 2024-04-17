from kmd_ntx_api.cache_data import coins_config_cache
from kmd_ntx_api.info import get_dpow_server_coins_info
from kmd_ntx_api.notary_seasons import get_season
from kmd_ntx_api.query import get_scoring_epochs_data
from kmd_ntx_api.logger import logger, timed

def is_testnet(coin):
    coins_config = coins_config_cache()
    return coins_config[coin]["is_testnet"]


def get_dpow_coins(season=get_season(), list=False):
    logger.info("get_dpow_coins(season=get_season(), list=False):")
    dpow_main_coins = get_dpow_server_coins_info(season=season, server="Main")
    dpow_3p_coins = get_dpow_server_coins_info(season=season, server="Third_Party")
    if list:
        return dpow_main_coins + dpow_3p_coins
    coins_dict = {
        "Main": dpow_main_coins,
        "Third_Party": dpow_3p_coins
    }
    return coins_dict


def get_coin_server(season, coin):
    if season.find("Testnet") != -1:
        return "Main"
    if coin in ["KMD", "BTC", "LTC"]:
        return coin
    coins_dict = get_dpow_coins(season)
    for server in coins_dict:
        if coin in coins_dict[server]:
            return server
    return "Unofficial"


def get_dpow_coins_list(season=None, server=None, epoch=None):
    dpow_coins = get_scoring_epochs_data(season, server, None, epoch).values('epoch_coins')
    coins_list = []
    for item in dpow_coins:
        coins_list += item['epoch_coins']
    coins_list = list(set(coins_list))
    coins_list.sort()
    return coins_list
