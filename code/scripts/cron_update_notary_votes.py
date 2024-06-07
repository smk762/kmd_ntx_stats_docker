#!/usr/bin/env python3.12
import sys
import lib_vote
from lib_rpc import RPC
from notary_candidates import CANDIDATE_ADDRESSES

if __name__ == "__main__":

    RESCAN_SEASON = False
    if len(sys.argv) > 1:
        if sys.argv[1] == "rescan":
            RESCAN_SEASON = True

    for year in CANDIDATE_ADDRESSES:
        if year in ["VOTE2022"]:
            vote = lib_vote.notary_vote(year, RESCAN_SEASON)
            vote.update_table()

            proposals = lib_vote.notary_candidates(year)
            proposals.update_table()
