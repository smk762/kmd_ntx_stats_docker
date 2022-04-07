#!/usr/bin/env python3
import sys
import lib_rpc
import lib_query
import lib_wallet


def analyse_reward_input_addresses():
    # select where not coinbase
    vin_addresses = lib_query.get_reward_input_addresses()
    return vin_addresses


def scan_rewards():

    reward_blocks = lib_query.get_reward_blocks()
    scan_blocks = list(set([*range(START_AT, TIP)]) - set(reward_blocks))
    scan_blocks.sort()
    scan_blocks.reverse()
    for i in scan_blocks:
        print(i)
        lib_wallet.get_rewards_tx_data(i)


if __name__ == "__main__":

    # Rescan will check chain for data since season start
    TIP = int(lib_rpc.RPC["KMD"].getblockcount())
    START_AT = TIP - 1440

    if len(sys.argv) > 1:
        if sys.argv[1] == "rescan":
            START_AT = 1

    scan_rewards()

    print(f"Unique reward claiming addresses in db: {len(analyse_reward_input_addresses())}")

