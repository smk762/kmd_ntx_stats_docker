#!/usr/bin/env python3

from models import *

TIP = int(RPC["VOTE2021"].getblockcount())

def scan_vote_blocks():
    for block_height in range(1, TIP):
        logger.info(f"Scanning block {block_height}")
        block_info = RPC["VOTE2021"].getblock(str(block_height))
        txids = block_info["tx"]
        block_hash = block_info["hash"]
        difficulty = block_info['difficulty']

        for txid in txids:
            raw_tx = RPC["VOTE2021"].getrawtransaction(txid,1)
            vouts = raw_tx["vout"]
            if "coinbase" in raw_tx["vin"][0]:
                mined_by = vouts[0]["scriptPubKey"]["addresses"][0]

        for txid in txids:
            raw_tx = RPC["VOTE2021"].getrawtransaction(txid,1)
            vouts = raw_tx["vout"]

            for vout in vouts:
                

                try:
                    address = None

                    if "address" in vout:
                        address = vout["address"]

                    elif "addresses" in vout["scriptPubKey"]:

                        if len(vout["scriptPubKey"]["addresses"]) == 1:
                            address = vout["scriptPubKey"]["addresses"][0]
                        else:
                            logger.warning(f"{txid} skipped, more than one address in vout")
                            logger.warning(f"{txid} vout: {vout}")

                
                    if address in VOTE2021_ADDRESSES_DICT:
                        notes = ""
                        if raw_tx["locktime"] == 0:
                            notes += "zero locktime value"
                        logger.info(f"[scan_vote_blocks] candidate: {VOTE2021_ADDRESSES_DICT[address]}")
                        row = vote2021_row()
                        row.txid = txid
                        row.block_hash = block_hash
                        row.block_time = raw_tx["blocktime"]
                        row.lock_time = raw_tx["locktime"]
                        row.block_height = block_height
                        row.votes = vout["value"]
                        row.candidate = VOTE2021_ADDRESSES_DICT[address]
                        row.candidate_address = address
                        row.mined_by = mined_by
                        row.difficulty = difficulty
                        row.notes = notes
                        row.update()

                except Exception as e:
                    logger.error(f"[scan_vote_blocks] {e}")
                    logger.warning(f"[scan_vote_blocks] txid: {txid}")
                    logger.warning(f"[scan_vote_blocks] vout: {vout}")

if __name__ == "__main__":

    scan_vote_blocks()