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

    if len(sys.argv) > 1:
        if sys.argv[1] == "rescan":
            lib_wallet.scan_rewards(TIP, "KMD", True)
        elif sys.argv[1] == "import":
            print("Importing rewards data...")
            lib_wallet.import_rewards()
            print("Rewards data import complete...")
        else:
            print(f"Unrecogised param {sys.argv[1]}. Use 'rescan' or 'import'")
    else:
        lib_wallet.scan_rewards(TIP)

    # print(f"Unique reward claiming addresses in db: {len(analyse_reward_input_addresses())}")

