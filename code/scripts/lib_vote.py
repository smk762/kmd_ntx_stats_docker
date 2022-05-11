#!/usr/bin/env python3

from models import *
from lib_const import *
from decorators import *
from lib_rpc import RPC
import lib_query_ntx as query
from notary_candidates import CANDIDATE_ADDRESSES

# Notarised table
class notary_vote():
    def __init__(self, year, rescan):
        self.year = year
        self.rescan = rescan
        self.notes = ''
        self.chain_tip = int(RPC[self.year].getblockcount())
        self.CANDIDATE_ADDRESSES = CANDIDATE_ADDRESSES[self.year]
        if rescan:
            self.start_block = 1
        else:
            self.start_block = self.chain_tip - 100


    @print_runtime
    def update_table(self):
        for block in range(self.start_block, self.chain_tip):
            logger.info(f"Processing votes for {self.year} block {block}")
            self.scan_block(block)


    def get_vote_row(self, block_height, raw_tx, txid, vin_addresses, vout):
        try:
            address = None
            if "address" in vout:
                address = vout["address"]
                if address not in vin_addresses:
                    if address in self.CANDIDATE_ADDRESSES:
                        row = notary_vote_row(self.year)
                        row.notes = "option 1"
                        row.txid = txid
                        row.block_hash = self.block_hash
                        row.block_time = raw_tx["blocktime"]
                        row.lock_time = raw_tx["locktime"]
                        row.block_height = block_height
                        row.votes = vout["value"]
                        row.candidate = self.CANDIDATE_ADDRESSES[address]
                        row.candidate_address = address
                        row.mined_by = self.mined_by
                        row.difficulty = self.difficulty
                        row.year = self.year
                        return row
                    else:
                        print(f"{txid} not a vote tx")
                else:
                    print(f"{txid} looks like a self-send")

            elif "addresses" in vout["scriptPubKey"]:
                if len(vout["scriptPubKey"]["addresses"]) == 1:
                    address = vout["scriptPubKey"]["addresses"][0]

                    if address not in vin_addresses:
                        if address in self.CANDIDATE_ADDRESSES:
                            row = notary_vote_row(self.year)
                            row.notes = "option 2"
                            row.txid = txid
                            row.block_hash = self.block_hash
                            row.block_time = raw_tx["blocktime"]
                            row.lock_time = raw_tx["locktime"]
                            row.block_height = block_height
                            row.votes = vout["value"]
                            row.candidate = self.CANDIDATE_ADDRESSES[address]
                            row.candidate_address = address
                            row.mined_by = self.mined_by
                            row.difficulty = self.difficulty
                            row.year = self.year
                            return row
                        else:
                            print(f"{txid} not a vote tx")
                    else:
                        print(f"{txid} looks like a self-send")

                else:
                    for address in len(vout["scriptPubKey"]["addresses"]):
                        if address not in vin_addresses:

                            if address in self.CANDIDATE_ADDRESSES:
                                row = notary_vote_row(self.year)
                                row.notes = "option 3"
                                row.txid = txid
                                row.block_hash = self.block_hash
                                row.block_time = raw_tx["blocktime"]
                                row.lock_time = raw_tx["locktime"]
                                row.block_height = block_height
                                row.votes = vout["value"]
                                row.candidate = self.CANDIDATE_ADDRESSES[address]
                                row.candidate_address = address
                                row.mined_by = self.mined_by
                                row.difficulty = self.difficulty
                                row.year = self.year
                                return row
                            else:
                                print(f"{txid} not a vote tx")
                        else:
                            print(f"{txid} looks like a self-send")

        except Exception as e:
            logger.error(f"[scan_vote_blocks] {e}")
            logger.warning(f"[scan_vote_blocks] txid: {txid}")
            logger.warning(f"[scan_vote_blocks] vout: {vout}")
            input()

        return None


    def scan_block(self, block_height):
        logger.info(f"Scanning block {block_height}")
        block_info = RPC[self.year].getblock(str(block_height))
        txids = block_info["tx"]
        self.block_hash = block_info["hash"]
        self.difficulty = block_info['difficulty']

        for txid in txids:
            raw_tx = RPC[self.year].getrawtransaction(txid,1)
            if "coinbase" in raw_tx["vin"][0]:
                vouts = raw_tx["vout"]
                self.mined_by = vouts[0]["scriptPubKey"]["addresses"][0]

        for txid in txids:
            raw_tx = RPC[self.year].getrawtransaction(txid,1)
            vins = raw_tx["vin"]
            vouts = raw_tx["vout"]
            coinbase = False
            vin_addresses = []

            for vin in vins:
                if "address" in vin:
                    vin_addresses.append(vin["address"])
                if 'coinbase' in vin:
                    coinbase = True

            if not coinbase:
                for vout in vouts:
                    row = self.get_vote_row(block_height, raw_tx, txid, vin_addresses, vout)
                    if row:
                        row.valid = self.is_vote_valid(row)
                        if not row.valid:
                            logger.warning("Invalid vote!")
                        row.update()


    def is_vote_valid(self, row):
        end_time = 1653523199
        last_notarised_blocks = query.select_from_notarised_tbl_where(
            season="Season_5", coin="VOTE2022", lowest_blocktime=end_time,
            highest_blocktime=row.block_time
        )
        
        if row.block_time < end_time:
            row.notes = "before timestamp"
            return True

        tip = int(RPC[self.year].getblockcount())

        if len(last_notarised_blocks) == 0:
            row.notes = "block after timestamp but before notarisation"
            return True

        if len(last_notarised_blocks) == 1:
            last_notarised_block = last_notarised_blocks[0][7]

            if row.block_height > last_notarised_block:
                row.notes = "block above last notarised after timestamp"
                return False
            row.notes = "block after timestamp but before or in last notarised after timestamp"
            return True

        if len(last_notarised_blocks) > 1:
            row.notes = "more than one ntx since timestamp"
            return False


        return False