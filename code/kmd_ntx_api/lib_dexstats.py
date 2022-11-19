import requests

# Grabs data from Dexstats explorer APIs
# e.g. https://kmd.explorer.dexstats.info/insight-api-komodo

DEXSTATS_COINS = ["BET", "BOTS", "CCL", "CHIPS", "CLC", "CRYPTO", "DEX",
                  "DP", "GLEEC", "HODL", "ILN", "JUMBLR", "KMD", "KOIN",
                  "LABS", "MCL", "MESH", "MGW", "MORTY", "MSHARK", "NINJA",
                  "PANGEA", "PIRATE", "REVS", "RICK", "SOULJA", "SPACE",
                  "SUPERNET", "THC", "TOKEL", "VRSC", "WSB", "ZILLA"]

def get_base_endpoint(coin):
    if coin == "MIL":
        return f"https://mil.kmdexplorer.io/api"

    if coin == "MCL":
        return f"https://explorer.marmara.io/insight-api-komodo"

    return f"https://{coin.lower()}.explorer.dexstats.info/insight-api-komodo"


def get_dexstats_utxos(coin, address):
    try:
        subdomain = get_base_endpoint(coin)
        endpoint = f"addr/{address}/utxo"
        url = f"{subdomain}/{endpoint}"
        print(url)
        return requests.get(url).json()
    except Exception as e:
        return f"{e}"


def get_sync(coin):
    try:
        subdomain = get_base_endpoint(coin)
        url = f"{subdomain}/sync"
        return requests.get(f"{url}").json()
    except Exception as e:
        return f"{e}"


def get_block_info(coin, block_height):
    try:
        subdomain = get_base_endpoint(coin)
        endpoint = f"block-index/{block_height}"
        return requests.get(f"{subdomain}/{endpoint}").json()
    except Exception as e:
        return f"{e}"


def getblock(coin, block_hash):
    try:
        subdomain = get_base_endpoint(coin)
        endpoint = f"block/{block_hash}"
        return requests.get(f"{subdomain}/{endpoint}").json()
    except Exception as e:
        return f"{e}"


def get_balance(coin, addr):
    try:
        subdomain = get_base_endpoint(coin)
        endpoint = f"addr/{addr}"
        return requests.get(f"{subdomain}/{endpoint}").json()
    except Exception as e:
        return f"{e}"