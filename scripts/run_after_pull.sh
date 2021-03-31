#!/bin/bash
./cron_populate_nn_social.py
./populate_addresses_table.py
./cron_populate_coins_table.py
./cron_populate_coin_social.py
./cron_populate_epochs.py
./cron_populate_balances_table.py
