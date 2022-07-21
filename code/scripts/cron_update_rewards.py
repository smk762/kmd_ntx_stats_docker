#!/usr/bin/env python3
import os
import sys
import json
import lib_rpc
import lib_query
import lib_wallet


script_path = os.path.abspath(os.path.dirname(sys.argv[0]))


def analyse_reward_input_addresses():
    # select where not coinbase
    vin_addresses = lib_query.get_reward_input_addresses()
    return vin_addresses



if __name__ == "__main__":

    # Rescan will check chain for data since season start
    TIP = int(lib_rpc.RPC["KMD"].getblockcount())
    START_AT = TIP - 1440

    if len(sys.argv) > 1:
        if sys.argv[1] == "rescan":
            START_AT = 1

    lib_wallet.scan_rewards(TIP)

    print(f"Unique reward claiming addresses in db: {len(analyse_reward_input_addresses())}")

