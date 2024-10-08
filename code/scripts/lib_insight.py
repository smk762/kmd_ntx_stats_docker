#!/usr/bin/env python3.12
from typing import List, Dict, Any, Optional
import requests
from functools import cached_property

from logger import logger

# See https://github.com/DeckerSU/insight-api-komodo for more info


class InsightAPI:
    def __init__(self, baseurl: str, api_path: str = "insight-api-komodo", api_key: Optional[str] = None):
        self.api_key = api_key
        self.session = requests.Session()  # Reuse session for efficiency
        self.session.headers.update({
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}" if api_key else ""
        })
        
        if baseurl.endswith("/"):
            baseurl = baseurl[:-1]
        self.api_url = f"{baseurl}/{api_path}"

    def _request(self, endpoint: str, params: Dict[str, Any] = None) -> Any:
        """Helper method to make API requests and handle errors."""
        url = f"{self.api_url}/{endpoint}"
        try:
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()  # Raise an exception for bad responses (4xx, 5xx)
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Error requesting {url}: {e}")
            raise

    def address_info(self, address: str) -> Dict[str, Any]:
        """Get information about an address."""
        return self._request(f"addr/{address}")

    def address_balance(self, address: str) -> int:
        """Get the balance of an address in satoshis."""
        return self._request(f"addr/{address}/balance")

    def address_transactions(self, address: str) -> Dict[str, Any]:
        """Get the transactions for an address."""
        return self._request(f"txs/?address={address}")

    def address_utxos(self, address: str) -> List[Dict[str, Any]]:
        """Get the unspent outputs for an address."""
        return self._request(f"addr/{address}/utxo")

    def addresses_transactions(self, addresses: List[str], from_: Optional[int] = None, to_: Optional[int] = None, 
                               no_asm: Optional[bool] = None, no_script_sig: Optional[bool] = None, 
                               no_spent: Optional[bool] = None) -> Dict[str, Any]:
        """Get transactions for multiple addresses with optional filters."""
        params = {
            "from": from_,
            "to": to_,
            "noAsm": no_asm,
            "noScriptSig": no_script_sig,
            "noSpent": no_spent
        }
        return self._request(f"addrs/{','.join(addresses)}/txs", params=params)

    def block_info(self, block_hash: str) -> Dict[str, Any]:
        """Get information about a block by its hash."""
        return self._request(f"block/{block_hash}")

    def block_transactions(self, block_hash: str) -> Dict[str, Any]:
        """Get the transactions for a block by its hash."""
        return self._request(f"txs/?block={block_hash}")

    def block_index_info(self, block_height: int) -> Dict[str, Any]:
        """Get information about a block by its height."""
        return self._request(f"block-index/{block_height}")

    def blocks_on_date(self, date: str, limit: Optional[int] = None) -> Dict[str, Any]:
        """Get block summaries by date."""
        params = {"blockDate": date, "limit": limit}
        return self._request("blocks", params=params)

    def raw_block(self, block_height: Optional[int] = None, block_hash: Optional[str] = None) -> Dict[str, Any]:
        """Get raw block data by block height or hash."""
        if block_hash:
            return self._request(f"rawblock/{block_hash}")
        else:
            block_hash = self.block_index_info(block_height)["blockHash"]
            return self._request(f"rawblock/{block_hash}")

    def raw_transaction(self, txid: str) -> Dict[str, Any]:
        """Get raw transaction data for a given transaction ID."""
        return self._request(f"rawtx/{txid}")

    def sync_status(self) -> Dict[str, Any]:
        """Get the current sync status of the blockchain."""
        return self._request("sync")

    def transaction_info(self, txid: str) -> Dict[str, Any]:
        """Get information about a transaction by its ID."""
        return self._request(f"tx/{txid}")

    def transaction_utxos(self, txid: str) -> List[Dict[str, Any]]:
        """Get unspent outputs for a transaction by its ID."""
        return self._request(f"tx/{txid}/utxo")

    def transactions_info(self, txids: List[str]) -> Dict[str, Any]:
        """Get information for multiple transactions by their IDs."""
        return self._request(f"txs/?txid={','.join(txids)}")

    def transactions_for_block(self, block_hash: str) -> Dict[str, Any]:
        """Get the transactions for a block by its hash."""
        return self._request(f"txs/?block={block_hash}")

    def transactions_for_block_height(self, block_height: int) -> Dict[str, Any]:
        """Get transactions for a block by its height."""
        block_hash = self.block_index_info(block_height)["blockHash"]
        return self.transactions_for_block(block_hash)


INSIGHT_EXPLORERS = {
    "CHIPS": [
        "https://chips.komodo.earth/",
        "https://chips.explorer.dragonhound.info/",
        "https://chips.explorer.dexstats.info/",
        "https://explorer.chips.cash/",
    ],
    "CCL": [
        "https://ccl.komodo.earth/",
        "https://ccl.explorer.dragonhound.info/",
        "https://ccl.kmdexplorer.io/",
        "https://ccl.explorer.dexstats.info/"
    ],
    "CLC": [
        "https://clc.komodo.earth/",
        "https://clc.explorer.dragonhound.info/",
        "https://clc.explorer.dexstats.info/",
    ],
    "DOC": [
        "https://doc.explorer.dexstats.info/",
        "https://doc.komodo.earth/",
        "https://doc.explorer.dragonhound.info/",
    ],
    "DP": ["https://dp.explorer.dexstats.info/"],
    "GLEEC": [
        "https://explorer.gleec.com/",
        "https://gleec.explorer.dexstats.info/"
    ],
    "GLEEC-OLD": [
        "https://gleec.komodo.earth/",
        "https://gleec.explorer.dragonhound.info/",
        "https://old.gleec.xyz/",
    ],
    "ILN": [
        "https://iln.komodo.earth/",
        "https://iln.explorer.dragonhound.info/",
        "https://explorer.ilien.io/",
        "https://iln.explorer.dexstats.info/",
    ],
    "KMD": [
        "https://explorer.komodoplatform.com/",
        "https://explorer.kmd.dev/",
        "https://explorer.kmd.io/",
        "https://kmd.explorer.dexstats.info/",
        "https://kmdexplorer.io/",
        "https://www.kmdexplorer.ru/",
    ],
    "LABS": ["https://labs.explorer.dexstats.info/"],
    "KOIN": [
        "https://koin.komodo.earth/",
        "https://koin.explorer.dragonhound.info/",
        "https://block.koinon.cloud/",
        "https://koin.explorer.dexstats.info/",
    ],
    "MARTY": [
        "https://marty.komodo.earth/",
        "https://marty.explorer.dragonhound.info/",
        "https://marty.explorer.dexstats.info/",
    ],
    "MCL": [
        "https://mcl.komodo.earth/",
        "https://explorer.marmara.io/",
        "https://mcl.explorer.dexstats.info/",
        "https://mcl.explorer.dragonhound.info/",
    ],
    "NINJA": [
        "https://ninja.komodo.earth/",
        "https://ninja.explorer.dragonhound.info/",
        "https://ninja.explorer.dexstats.info/",
        "https://ninja.kmdexplorer.io/",
    ],
    "PIRATE": [
        "https://pirate.komodo.earth/",
        "https://pirate.explorer.dragonhound.info/",
        "https://explorer.pirate.black/",
        "https://pirate.explorer.dexstats.info/",
        "https://pirate.kmdexplorer.io/",
    ],
    "SPACE": [
        "https://explorer.spaceworks.co/",
        "https://space.explorer.dexstats.info/",
    ],
    "SUPERNET": [
        "https://supernet.komodo.earth/",
        "https://supernet.explorer.dragonhound.info/",
        "https://supernet.explorer.dexstats.info/",
        "https://supernet.kmdexplorer.io/",
    ],
    "THC": [
        "https://thc.komodo.earth/",
        "https://thc.explorer.dragonhound.info/",
        "https://thc.explorer.dexstats.info/",
    ],
    "TOKEL": [
        "https://tokel.komodo.earth/",
        "https://tokel.explorer.dragonhound.info/",
        "https://explorer.tokel.io/",
        "https://tokel.explorer.dexstats.info/",
    ],
    "VRSC": [
        "https://vrsc.komodo.earth/",
        "https://vrsc.explorer.dragonhound.info/",
        "https://explorer.verus.io/",
        "https://vrsc.explorer.dexstats.info/",
    ],
}
