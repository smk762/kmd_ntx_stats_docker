#!/usr/bin/env python3
from models import *
from lib_const import *
from lib_helper import *
from lib_validate import *
from lib_query import *

tables = ["addresses", "balances", "coin_sync", "coins", "coin_social",
          "funding_transactions", "notary_last_ntx", "mined", "mined_count_daily",
          "mined_count_season", "nn_btc_tx", "nn_ltc_tx", "nn_social", 
          "notarised", "notarised_coin_daily", "notarised_coin_season",
          "notarised_count_daily", "notarised_count_season", "notarised_tenure",
          "scoring_epochs", "vote2021"]

for season in ["Season_7"]:
    if season not in EXCLUDED_SEASONS:
        for server in SEASONS_INFO[season]["servers"]:
            for epoch in SEASONS_INFO[season]["servers"][server]["epochs"]:
                epoch_data = SEASONS_INFO[season]["servers"][server]["epochs"][epoch]
                print(epoch_data)
                score_per_ntx = epoch_data["score_per_ntx"]
                epoch_start = epoch_data["start_time"]
                epoch_end = epoch_data["end_time"]
                epoch_coins = epoch_data["coins"]
                epoch_coins.sort()

                notarised_coins = get_notarised_coins(season, server, epoch)
                print(f"{len(notarised_coins)} coins for {season} {server} {epoch}")
                notarised_coins.sort()
                for coin in notarised_coins:
                    if coin not in epoch_coins:
                        logger.warning(f"Invalid coin {coin} in notarised for {season} {server} {epoch}")

                epoch_scores = get_notarised_server_epoch_scores(season, server, epoch)[server][epoch]
                print(epoch_scores)
                print(f"{len(epoch_scores)} ntx score for {season} {server} {epoch}")
                if len(epoch_scores) > 1:
                    logger.warning(f"Invalid epoch scores {epoch_scores} in notarised for {season} {server} {epoch}")
                elif epoch_scores[0] != score_per_ntx:
                    logger.warning(f"Mismatched epoch score {epoch_scores[0]} vs {score_per_ntx} in notarised for {season} {server} {epoch}")


        unofficial_scores = get_notarised_coin_epoch_scores(season, None, "Unofficial")
        if len(unofficial_scores) > 0:
            logger.warning(f"Mismatched epoch score {unofficial_scores[0]} vs 0 in notarised for {season} unofficial epoch")


