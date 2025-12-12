#!/usr/bin/env python3.12
from typing import List, Dict, Any, Optional
import requests
from functools import cached_property
from pathlib import Path
import json

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

    def node_status(self) -> Dict[str, Any]:
        """Get the current status of the node."""
        return self._request("status")

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


def load_insight_explorers() -> Dict[str, list]:
    """Load explorer list from JSON so it can be edited without touching code."""
    path = Path(__file__).resolve().parent / "insight_explorers.json"
    try:
        return json.loads(path.read_text())
    except Exception as e:
        logger.error(f"Failed to load insight_explorers.json: {e}")
        return {}


INSIGHT_EXPLORERS = load_insight_explorers()
