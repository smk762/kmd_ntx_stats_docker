import requests

# Grabs data from Dexstats explorer APIs
# e.g. https://kmd.explorer.dexstats.info/insight-api-komodo


def get_blocktip(chain):
    try:
        subdomain = f"https://{chain.lower()}.explorer.dexstats.info"
        endpoint = f"insight-api-komodo/sync"
        return requests.get(f"{subdomain}/{endpoint}").json()["height"]
    except:
        return 0


def get_utxos(chain, address):
    try:
        subdomain = f"https://{chain.lower()}.explorer.dexstats.info"
        endpoint = f"insight-api-komodo/addr/{address}/utxo"
        return requests.get(f"{subdomain}/{endpoint}").json()
    except:
        return []
