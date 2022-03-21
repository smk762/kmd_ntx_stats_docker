#!/usr/bin/env python3
import os
from dotenv import load_dotenv

# ENV VARS
load_dotenv()

OTHER_SERVER = os.getenv("OTHER_SERVER")
THIS_SERVER = os.getenv("THIS_SERVER")


def get_api_server(local=True):
    if local:
        return THIS_SERVER
    return OTHER_SERVER


def get_ntxid_list_url(season, server, chain, local=True):
    api_server = get_api_server(local)
    return f"{api_server}/api/info/notarisation_txid_list/?season={season}&server={server}&chain={chain}"


def get_notarised_txid_url(txid, local=True):
    api_server = get_api_server(local)
    return f"{api_server}/api/info/notarised_txid/?txid={txid}"


def get_coins_info_url(local=True):
    api_server = get_api_server(local)
    return f"{api_server}/api/info/coins/"

def get_decode_opret_url(opret, local=True):
    api_server = get_api_server(local)
    return f'{api_server}/api/tools/decode_opreturn/?OP_RETURN={opret}'

def get_notary_btc_txid_url(txid, local=True):
    api_server = get_api_server(local)
    return f"{api_server}/api/info/notary_btc_txid/?txid={txid}"


def get_notary_ltc_txid_url(txid, local=True):
    api_server = get_api_server(local)
    return f"{api_server}/api/info/notary_ltc_txid/?txid={txid}"


def get_notary_addresses_url(season, notary=None, local=True):
    api_server = get_api_server(local)
    url = f"{api_server}/api/wallet/notary_addresses/?season={season}"
    if notary:
        url += f"&notary={notary}"
    return url

def get_source_addresses_url(season=None, server=None, chain=None, local=True):
    api_server = get_api_server(local)
    url = f"{api_server}/api/source/addresses/?"
    params = []
    if season:
        params.append(f"season={season}")
    if server:
        params.append(f"server={server}")
    if chain:
        params.append(f"chain={chain}")
    params_string = "&".join(params)
    return url + params_string


def get_notarised_tenure_table_url(season=None, server=None, chain=None, local=True):
    api_server = get_api_server(local)
    url = f"{api_server}/api/table/notarised_tenure/?"
    if season:
        url += f"&season={season}"
    if server:
        url += f"&server={server}"
    if chain:
        url += f"&chain={chain}"
    return url


def get_dpow_server_coins_url(season, server, local=True):
    api_server = get_api_server(local)
    return f'{api_server}/api/info/dpow_server_coins/?season={season}&server={server}'


def get_coins_repo_coins_url(branch='master'):
    return f"https://raw.githubusercontent.com/KomodoPlatform/coins/{branch}/coins"


def get_dpow_readme_url(branch='master'):
    return f"https://raw.githubusercontent.com/KomodoPlatform/dPoW/{branch}/README.md"


def get_dpow_assetchains_url(branch='master'):
    return f"https://raw.githubusercontent.com/KomodoPlatform/dPoW/{branch}/iguana/assetchains.json"


def get_notary_nodes_repo_coin_social_url(season):
    return f"https://raw.githubusercontent.com/KomodoPlatform/NotaryNodes/master/{season.lower().replace('_', '')}/coin_social.json"


def get_notary_nodes_repo_elected_nn_social_url(season):
    return f"https://raw.githubusercontent.com/KomodoPlatform/NotaryNodes/master/{season.lower().replace('_', '')}/elected_nn_social.json"


def get_scoring_epochs_url(branch='master'):
    return f"https://raw.githubusercontent.com/KomodoPlatform/dPoW/{branch}/doc/scoring_epochs.json"

def get_coins_info_url(local=True):
    api_server = get_api_server(local)
    return f'{api_server}/api/info/coins/'

def get_electrums_info_url(local=True):
    api_server = get_api_server(local)
    return f'{api_server}/api/info/electrums/'

# f"{OTHER_SERVER}/api/info/nn_btc_txid/?txid={self.txid}"
# f"{OTHER_SERVER}/api/info/nn_ltc_txid/?txid={self.txid}"
# f"{OTHER_SERVER}/api/info/notary_btc_txid/?txid={txid}"
# f"{OTHER_SERVER}/api/info/notary_ltc_txid/?txid={txid}"
# f"{OTHER_SERVER}/api/info/ltc_txid_list/?notary={NN_LTC_ADDRESSES_DICT[season][notary_address]}&season={season}"
# f"{OTHER_SERVER}/api/info/btc_txid_list/?notary={NN_BTC_ADDRESSES_DICT[season][notary_address]}&season={season}"
