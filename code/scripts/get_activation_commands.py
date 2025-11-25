#!/usr/bin/env python3
import json
from collections import defaultdict
from typing import Dict, Tuple, Any
from logger import logger


def sort_dict(item: dict):
    return {k: sort_dict(v) if isinstance(v, dict) else v for k, v in sorted(item.items())}

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


def get_utxo_activation(coins_config, coin, wss: bool=False):
    electrums = []
    for i in coins_config[coin]["electrum"]:
        if "protocol" in i:
            if wss is True and i["protocol"] == "WSS":
                electrums.append(i)
            else:
                electrums.append(i)
    return {
        "userpass": "'$userpass'",
        "method": "electrum",
        "coin": coin,
        "servers": electrums
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


def get_evm_activation(coins_config, coin):
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
    '''Deprecated'''
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


def get_activation_command(coins_config: Dict[str, Dict[str, Any]], coin: str, wss: bool=False) -> Tuple[str, Dict[str, Any]]:
    try:
        if coin not in coins_config:
            return None, {}
        if coins_config[coin]["mm2"] != 1:
            logger.error(f"Coin {coin} is not compatible with mm2.")
            return None, {}
        resp_json = defaultdict(dict)
        protocol = coins_config[coin]["protocol"]["type"]
        platform = None

        for contract_key in ["swap_contract_address", "fallback_swap_contract"]:
            if contract_key in coins_config[coin]:
                resp_json.update({contract_key: coins_config[coin][contract_key]})

        protocol_data = coins_config[coin]["protocol"].get("protocol_data", {})
        platform = protocol_data.get("platform")
        try:
            if protocol == "ZHTLC":
                platform = "UTXO"
                resp_json.update(get_zhtlc_activation(coins_config, coin))
            elif protocol == "UTXO":
                platform = 'UTXO'
                resp_json.update(get_utxo_activation(coins_config, coin, wss))
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
                if platform is None:
                    platform = protocol
                resp_json.update(get_evm_activation(coins_config, coin))
            else:
                logger.error("No platform found for coin: {}".format(coin))
            return platform, resp_json
        except Exception as e:
            logger.error(f"Error getting activation command for {coin}: {e}")
            return None, {}


def get_activation_commands(coins_config: Dict[str, Dict[str, Any]], wss: bool=False) -> Dict[str, Any]:
        enable_commands = {}
        logger.info("================ Getting coin activation examples ================")
        for coin in coins_config:
            platform, resp_json = get_activation_command(coins_config, coin, wss)
            if platform not in enable_commands:
                enable_commands.update({platform: {}})
            enable_commands[platform].update({coin: sort_dict(resp_json)})
        return enable_commands

if __name__ == '__main__':

    with open('coins_config.json', 'r') as f:
        coins_config = json.load(f)

    wss_commands = get_activation_commands(coins_config, True)
    with open('wss_commands.json', 'w+') as f:
        json.dump(wss_commands, f, indent=4)

    tcp_commands = get_activation_commands(coins_config, False)
    with open('tcp_commands.json', 'w+') as f:
        json.dump(tcp_commands, f, indent=4)
