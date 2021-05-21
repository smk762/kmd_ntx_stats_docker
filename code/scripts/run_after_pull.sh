#!/bin/bash
./cron_populate_nn_social.py
./populate_addresses_table.py
./cron_populate_coins_table.py
./cron_populate_coin_social.py
./cron_populate_epochs.py
#./validate_nn_btc_tx_DB_integrity.py
#./validate_notarised_table_integrity.py
