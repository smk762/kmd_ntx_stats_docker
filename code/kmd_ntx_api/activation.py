
from kmd_ntx_api.logger import logger
from kmd_ntx_api.helper import get_or_none, sort_dict
from kmd_ntx_api.cache_data import coins_config_cache


def get_zhtlc_activation(coins_config, coin):
    return {
        "method": "task::enable_z_coin::init",
        "mmrpc": "2.0",
        "userpass":"'$userpass'",
        "params": {
            "ticker": coin,
            "activation_params": {
                "mode": {
                    "rpc": "Light",
                    "rpc_data": {
                        "electrum_servers": coins_config[coin]["electrum"],
                        "light_wallet_d_servers": coins_config[coin]["light_wallet_d_servers"]
                    }
                }
            }
        }
    }


def get_utxo_activation(coins_config, coin):
    return {
        "userpass": "'$userpass'",
        "method": "electrum",
        "coin": coin,
        "servers": coins_config[coin]["electrum"],
    }


def get_tendermint_activation(coins_config, coin):
    return {
        "method": "enable_tendermint_with_assets",
        "mmrpc": "2.0",
        "params": {
            "ticker": coin,
            "tokens_params": [],
            "rpc_urls": [i["url"] for i in coins_config[coin]["rpc_urls"]]
        },
        "userpass": "'$userpass'"
    }


def get_tendermint_token_activation(coin):
    return {
        "userpass": "'$userpass'",
        "method": "enable_tendermint_token",
        "mmrpc": "2.0",
        "params": {
            "ticker": coin,
            "activation_params": {
            "required_confirmations": 3
            }
        }
    }


def get_emv_activation(coins_config, coin):
    # TODO: Update to use newer methods
    if "nodes" in coins_config[coin]:
        return {
            "userpass": "'$userpass'",
            "method": "enable",
            "coin": coin, 
            "urls": [i["url"] for i in coins_config[coin]["nodes"] if "gui_auth" not in i]
        }
    else:
        logger.warning(f"EMV activation for {coin} not possible, no nodes found")
        logger.warning(coins_config[coin])
        return {
            "userpass": "'$userpass'",
            "method": "METHOD_NOT_FOUND",
            "coin": coin
        }

def get_bch_activation(coins_config, coin):
    return {
        "userpass": "'$userpass'",
        "method": "enable_bch_with_tokens",
        "mmrpc": "2.0",
        "params": {
            "ticker": coin,
            "allow_slp_unsafe_conf": False,
            "slp_prefix": coins_config[coin]["slp_prefix"],
            "bchd_urls": coins_config[coin]["bchd_urls"],
            "mode": {
                "rpc": "Electrum",
                "rpc_data": {
                    "servers": coins_config[coin]["electrum"]
                }
            },
            "tx_history": True,
            "slp_tokens_requests": [],
            "required_confirmations": 3,
            "requires_notarization": False,
            "address_format": coins_config[coin]["address_format"]
        }
    }
    

def get_slp_activation(coin):
    return {
        "userpass": "'$userpass'",
        "method": "enable_slp",
        "mmrpc": "2.0",
        "params": {
            "ticker": coin,
            "activation_params": {
                "required_confirmations": 3
            }
        }
    }


def get_activation_command(coins_config, coin):
    resp_json = {}
    compatible = coins_config[coin]["mm2"] == 1
    if not compatible:
        resp_json
    protocol = coins_config[coin]["protocol"]["type"]
    platform = None

    for i in ["swap_contract_address", "fallback_swap_contract"]:
        if i in coins_config[coin]:
            resp_json.update({i: coins_config[coin][i]})

    if "protocol_data" in coins_config[coin]["protocol"]:
        if "platform" in coins_config[coin]["protocol"]["protocol_data"]:
            platform = coins_config[coin]["protocol"]["protocol_data"]["platform"]

    if coin in ["BCH", "tBCH"]:
        platform = "UTXO"
        resp_json.update(get_bch_activation(coins_config, coin))
    elif protocol == "ZHTLC":
        platform = "UTXO"
        resp_json.update(get_zhtlc_activation(coins_config, coin))
    elif protocol == "UTXO":
        platform = 'UTXO'
        resp_json.update(get_utxo_activation(coins_config, coin))
    elif protocol == "QRC20" or coin in ['QTUM', 'QTUM-segwit']:
        platform = 'QRC20'
        resp_json.update(get_utxo_activation(coins_config, coin))
    elif protocol == "tQTUM" or coin in ['tQTUM', 'tQTUM-segwit']:
        platform = 'tQTUM'
        resp_json.update(get_utxo_activation(coins_config, coin))
    elif protocol == "TENDERMINT":
        platform = 'TENDERMINT'
        resp_json.update(get_tendermint_activation(coins_config, coin))
    elif protocol == "TENDERMINTTOKEN":
        platform = 'TENDERMINTTOKEN'
        resp_json.update(get_tendermint_token_activation(coin))
    elif protocol == "SLPTOKEN":
        platform = 'SLPTOKEN'
        resp_json.update(get_slp_activation(coin))
    elif coin in coins_config:
        resp_json.update(get_emv_activation(coins_config, coin))
    else:
        logger.error("No platform found for coin: {}".format(coin))
    return platform, resp_json


def get_activation_commands(request):
    logger.info("Running get_activation_commands")
    enable_commands = {"commands":{}}
    resp_json = {}

    coins_config = coins_config_cache()
    selected_coin = get_or_none(request, "coin")
    if selected_coin is None:
        for coin in coins_config:
            platform, resp_json = get_activation_command(coins_config, coin)
            if platform not in enable_commands["commands"]:
                enable_commands["commands"].update({platform: {}})
            enable_commands["commands"][platform].update({coin: sort_dict(resp_json)})
        return enable_commands
    else:
        platform, resp_json = get_activation_command(coins_config, selected_coin)
        return resp_json


def get_coin_activation_commands(request):
    coin_commands = {}
    logger.info("Running get_coin_activation_commands")
    protocol_commands = get_activation_commands(request)["commands"]
    for protocol in protocol_commands:
        for coin in protocol_commands[protocol]:
            coin_commands.update({coin: protocol_commands[protocol][coin]})
    return coin_commands
