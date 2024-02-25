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

# TODO: reduce calls to local api 

def get_electrums_info_url(local=True):
    api_server = get_api_server(local)
    return f'{api_server}/api/info/electrums/'


def get_explorers_info_url(local=True):
    api_server = get_api_server(local)
    return f'{api_server}/api/info/explorers/'


def get_electrums_ssl_info_url(local=True):
    api_server = get_api_server(local)
    return f'{api_server}/api/info/electrums_ssl/'

def get_electrums_wss_info_url(local=True):
    api_server = get_api_server(local)
    return f'{api_server}/api/info/electrums_wss/'


def get_ntxid_list_url(season, server, coin, local=True):
    api_server = get_api_server(local)
    url = f"{api_server}/api/info/notarisation_txid_list/?season={season}&server={server}&coin={coin}"
    print(url)
    return url


def get_rewards_txids_url(local=False):
    api_server = get_api_server(local)
    return f"{api_server}/api/wallet/rewards_txids"

    
def get_rewards_txid_url(txid, local=False):
    api_server = get_api_server(local)
    return f"{api_server}/api/wallet/rewards_txids/?txid={txid}"


def get_notarised_txid_url(txid, local=True):
    api_server = get_api_server(local)
    return f"{api_server}/api/info/notarised_txid/?txid={txid}"


def get_kmd_price_url(date):
    return f"https://api.coingecko.com/api/v3/coins/komodo/history?date={date}"


def get_coins_info_url(local=True):
    api_server = get_api_server(local)
    return f"{api_server}/api/info/coins/"

def get_seednode_stats_url(season, local=False):
    api_server = get_api_server(local)
    return f"{api_server}/api/source/seednode_version_stats/?season={season}"


def get_decode_opret_url(opret, local=True):
    api_server = get_api_server(local)
    return f'{api_server}/api/tools/decode_opreturn/?OP_RETURN={opret}'


def get_notary_btc_txid_url(txid, local=True):
    api_server = get_api_server(local)
    return f"{api_server}/api/info/notary_btc_txid/?txid={txid}"


def get_notarised_coins_url(season=None, server=None, epoch=None, local=True):
    api_server = get_api_server(local)
    url = f"{api_server}/api/info/notarised_coins/?"
    params = []
    if season:
        params.append(f"season={season}")
    if server:
        params.append(f"server={server}")
    if epoch:
        params.append(f"epoch={epoch}")
    params_string = "&".join(params)
    return url + params_string


def get_notarised_servers_url(season=None, local=True):
    api_server = get_api_server(local)
    url = f"{api_server}/api/info/notarised_servers/?"
    params = []
    if season:
        params.append(f"season={season}")
    params_string = "&".join(params)
    return url + params_string


def get_season_scoring_epochs_url(season=None, local=True):
    api_server = get_api_server(local)
    if season:
        return f"{api_server}/api/source/scoring_epochs/?season={season}"
    return f"{api_server}/api/source/scoring_epochs/"


def get_notary_ltc_txid_url(txid, local=True):
    api_server = get_api_server(local)
    return f"{api_server}/api/info/notary_ltc_txid/?txid={txid}"


def get_notary_addresses_url(season, notary=None, local=True):
    api_server = get_api_server(local)
    url = f"{api_server}/api/wallet/notary_addresses/?season={season}"
    if notary:
        url += f"&notary={notary}"
    return url

def get_source_addresses_url(season=None, server=None, coin=None, notary=None, local=True):
    api_server = get_api_server(local)
    url = f"{api_server}/api/source/addresses/?"
    params = []
    if season:
        params.append(f"season={season}")
    if server:
        params.append(f"server={server}")
    if coin:
        params.append(f"coin={coin}")
    if notary:
        params.append(f"notary={notary}")
    params_string = "&".join(params)
    return url + params_string


def get_addresses_url(season, server=None, coin=None, notary=None, local=True):
    api_server = get_api_server(local)
    url = f"{api_server}/api/table/addresses/?season={season}"
    if server:
        url += f"&server={server}"
    if coin:
        url += f"&coin={coin}"
    if notary:
        url += f"&notary={notary}"
    return url


def get_notarised_tenure_table_url(season=None, server=None, coin=None, local=True):
    api_server = get_api_server(local)
    url = f"{api_server}/api/table/notarised_tenure/?"
    if season:
        url += f"&season={season}"
    if server:
        url += f"&server={server}"
    if coin:
        url += f"&coin={coin}"
    return url



def get_notarised_source_url(
        local=True, season=None, server=None, coin=None,
        min_blocktime=None, max_blocktime=None,
        min_block=None, max_block=None
    ):
    api_server = get_api_server(local)
    url = f'{api_server}/api/source/notarised/?'
    if season:
        url += f"&season={season}"
    if server:
        url += f"&server={server}"
    if coin:
        url += f"&coin={coin}"
    if min_blocktime:
        url += f"&min_blocktime={min_blocktime}"
    if max_blocktime:
        url += f"&max_blocktime={max_blocktime}"
    if min_block:
        url += f"&min_block={min_block}"
    if max_block:
        url += f"&max_block={max_block}"
    return url


def get_utxos_url(local=True, coin=None, pubkey=None):
    api_server = get_api_server(local)
    url = f'{api_server}/api/tools/pubkey_utxos/?'
    url += f"&coin={coin}"
    url += f"&pubkey={pubkey}"
    return url


def get_proposals_url(local=True, year=None):
    api_server = get_api_server(local)
    url = f'{api_server}/api/testnet/proposals/?'
    url += f"&year={year}"
    return url


def get_dpow_active_coins_url(local=True):
    api_server = get_api_server(local)
    return f'{api_server}/api/info/coins/?dpow_active=1'


def get_dpow_server_coins_url(season, server, local=True):
    api_server = get_api_server(local)
    return f'{api_server}/api/info/dpow_server_coins/?season={season}&server={server}'


def get_coins_repo_coins_url(branch='master'):
    return f"https://raw.githubusercontent.com/KomodoPlatform/coins/{branch}/coins"


def get_coins_repo_electrums_url(branch='master'):
    return f"https://raw.githubusercontent.com/KomodoPlatform/coins/{branch}/electrums"


def get_coins_repo_explorers_url(branch='master'):
    return f"https://raw.githubusercontent.com/KomodoPlatform/coins/{branch}/explorers"


def get_coins_repo_icons_url(branch='master'):
    return f"https://raw.githubusercontent.com/KomodoPlatform/coins/{branch}/icons"


def get_dpow_readme_url(branch='master'):
    return f"https://raw.githubusercontent.com/KomodoPlatform/dPoW/{branch}/README.md"


def get_dpow_assetchains_url(branch='master'):
    return f"https://raw.githubusercontent.com/KomodoPlatform/dPoW/{branch}/iguana/assetchains.json"


def get_notary_nodes_repo_coin_social_url(season):
    return f"https://raw.githubusercontent.com/KomodoPlatform/NotaryNodes/master/{season.lower().replace('_', '')}/coin_social.json"


def get_notary_nodes_repo_elected_nn_social_url(season):
    return f"https://raw.githubusercontent.com/KomodoPlatform/NotaryNodes/master/{season.lower().replace('_', '')}/elected_nn_social.json"


def get_scoring_epochs_repo_url(branch='master'):
    return f"https://raw.githubusercontent.com/KomodoPlatform/dPoW/{branch}/doc/scoring_epochs.json"

