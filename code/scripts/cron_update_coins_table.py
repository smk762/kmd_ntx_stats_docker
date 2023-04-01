#!/usr/bin/env python3
from decorators import *
from lib_coins import *


@print_runtime
def update_coins_tables():
    # Gets data from coins repo, komodo repo and dpow repo...
    coins_data = parse_coins_repo()
    coins_data = parse_electrum_explorer(coins_data)
    coins_data, dpow_coins = parse_dpow_coins(coins_data)
    coins_data = parse_assetchains(coins_data)
    coins_data = get_dpow_tenure(coins_data)

    # TODO: update timestamp column, use that to delete stale coins
    # remove_old_coins(coins_data)

    update_coins(coins_data)
    remove_delisted_coins(dpow_coins)

if __name__ == "__main__":

    update_coins_tables()
    CURSOR.close()
    CONN.close()
