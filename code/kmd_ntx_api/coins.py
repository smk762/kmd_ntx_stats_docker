from kmd_ntx_api.cache_data import coins_config_cache


def is_testnet(coin):
    coins_config = coins_config_cache()
    return coins_config[coin]["is_testnet"]
