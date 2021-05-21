#!/usr/bin/env python3
from models import *
from lib_const import *
from lib_table_select import *

tables = ["addresses", "balances", "chain_sync", "coins", "coin_social",
		  "funding_transactions", "last_notarised", "mined", "mined_count_daily",
		  "mined_count_season", "nn_btc_tx", "nn_ltc_tx", "nn_social", 
		  "notarised", "notarised_chain_daily", "notarised_chain_season",
		  "notarised_count_daily", "notarised_count_season", "notarised_tenure",
		  "scoring_epochs", "vote2021"]

def validate_addresses_table():
	# Should be valid seasons, servers, notaries
	table = "addresses"
	check_distinct_columns = ["season", "server", "notary"]
	season_values = get_distinct_col_vals_from_table(table, "season")
	print(f"DISTINCT [season] values: {season_values}")
	# Extra seasons? Seasons Missing?

	for season in season_values:
		conditions = f"WHERE season = '{season}'"
		server_values = get_distinct_col_vals_from_table(table, "server", conditions)
		print(f"\nDISTINCT [{season}] [server] values: {server_values}")
		# Extra servers? Servers Missing?

		for server in server_values:
			conditions = f"WHERE season = '{season}' AND server = '{server}'"
			notary_values = get_distinct_col_vals_from_table(table, "notary", conditions)
			print(f"DISTINCT [{season}] [{server}] [notary] values: {notary_values}")
			# Extra notaries? Notaries Missing?

		for notary in notary_values:
			conditions = f"WHERE season = '{season}' AND server = '{server}' and notary = '{notary}'"
			chain_values = get_distinct_col_vals_from_table(table, "chain", conditions)
			print(f"DISTINCT [{season}] [{server}] [{notary}] [chain] values: {chain_values}")
			# Extra chains? Chains Missing?

	# Are address values valid for chain? Do they match pubkey?
	# Is notary_id correct?

validate_addresses_table()
