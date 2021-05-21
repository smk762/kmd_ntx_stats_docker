import requests

# Grabs data from Dexstats explorer APIs
# e.g. https://kmd.explorer.dexstats.info/insight-api-komodo

def get_blocktip(chain):
    try:
        return requests.get(f"https://{chain.lower()}.explorer.dexstats.info/insight-api-komodo/sync").json()["height"]
    except:
        return 0

def get_utxos(chain, address):
    try:
        return requests.get(f"https://{chain}.explorer.dexstats.info/insight-api-komodo/addr/{address}/utxo").json()
    except:
        return []