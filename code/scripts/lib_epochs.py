#!/usr/bin/env python3
import json
from lib_update import *
from lib_query import *
import lib_validate
from models import ntx_tenure_row, scoring_epoch_row
from decorators import print_runtime
from lib_helper import get_season_coins


@print_runtime
def preseason_populate_ntx_tenure(season):
    now = int(time.time())
    s_start = SEASONS_INFO[season]["start_time"]
    if now < SEASONS_INFO[season]["start_time"] and s_start - now < 604800:
        row = ntx_tenure_row()
        row.coin = coin
        row.first_ntx_block = 0
        row.last_ntx_block = 0
        row.first_ntx_block_time = SEASONS_INFO[season]["start_block"]
        row.last_ntx_block_time = SEASONS_INFO[season]["end_block"]
        row.official_start_block_time = SEASONS_INFO[season]["start_time"]
        row.official_end_block_time = SEASONS_INFO[season]["end_time"]
        row.scored_ntx_count = 0
        row.unscored_ntx_count = 0
        row.season = season
        row.server = server
        return row
    else:
        return None


@print_runtime
def get_ntx_tenure(season, server, coin):
    ntx_results = get_ntx_min_max(season, server, None, coin) # from notarised
    min_blk = ntx_results[0]
    min_blk_time = ntx_results[1]
    max_blk = ntx_results[2]
    max_blk_time = ntx_results[3]
    total_ntx_count = ntx_results[4]

    if max_blk is not None:
        scoring_window = get_dpow_scoring_window(season, server, coin)
        if scoring_window is not None:
            official_start = scoring_window[0]
            official_end = scoring_window[1]

            if season in DPOW_EXCLUDED_COINS:

                if coin in DPOW_EXCLUDED_COINS[season]:
                    season = "Unofficial"
                    scored_ntx_count = 0
                    unscored_ntx_count = len(scoring_window[2])+len(scoring_window[3])

                else:
                    scored_ntx_count = len(scoring_window[2])
                    unscored_ntx_count = len(scoring_window[3])

            elif coin in ["LTC", "BTC"]:
                scored_ntx_count = 0
                unscored_ntx_count = len(scoring_window[2])+len(scoring_window[3])

            else:
                scored_ntx_count = len(scoring_window[2])
                unscored_ntx_count = len(scoring_window[3])

            row = ntx_tenure_row()
            row.coin = coin
            row.first_ntx_block = min_blk
            row.last_ntx_block = max_blk
            row.first_ntx_block_time = min_blk_time
            row.last_ntx_block_time = max_blk_time
            row.official_start_block_time = official_start
            row.official_end_block_time = official_end
            row.scored_ntx_count = scored_ntx_count
            row.unscored_ntx_count = unscored_ntx_count
            row.season = season
            row.server = server
            return row
    return None


@print_runtime
def update_tenure(season):
    now = int(time.time())
    if season in SEASONS_INFO:
        for server in SEASONS_INFO[season]["servers"]:
            s_start = SEASONS_INFO[season]["start_time"]

            if now < SEASONS_INFO[season]["start_time"] and s_start - now < 604800:

                print("Pre-season epoch pop!")
                if server in NEXT_SEASON_COINS:
                    season_server_coins = NEXT_SEASON_COINS[server]
                else:
                    season_server_coins = []

            else:
                season_server_coins = SEASONS_INFO[season]["servers"][server]["coins"]

            for coin in season_server_coins:
                update_ntx_tenure(season, server, coin)


@print_runtime
def update_epochs(season):
    now = int(time.time())
    logger.info(f"Processing {season}...")

    for server in SEASONS_INFO[season]["servers"]:
        scoring_season_server_epochs = SEASONS_INFO[season]["servers"][server]["epochs"]
        for epoch in SEASONS_INFO[season]["servers"][server]["epochs"]:
            logger.info(f">>> Processing {season} {server} {epoch} epoch_row")
            epoch_start = SEASONS_INFO[season]["servers"][server]["epochs"][epoch]["start_time"]
            epoch_end = SEASONS_INFO[season]["servers"][server]["epochs"][epoch]["end_time"]
            epoch_midpoint = int((epoch_start + epoch_end)/2)
            s_start = SEASONS_INFO[season]["start_time"]

            if now < SEASONS_INFO[season]["start_time"] and s_start - now < 604800:

                print("Pre-season epoch pop!")
                if server in NEXT_SEASON_COINS:
                    active_coins = NEXT_SEASON_COINS[server]
                    num_coins = len(active_coins)
                else:
                    active_coins = []
                    num_coins = len(active_coins)

            else:
                active_coins = SEASONS_INFO[season]["servers"][server]["epochs"][epoch]["coins"]
                num_coins = len(active_coins)

            active_coins.sort()

            if num_coins > 0:
                epoch_row = scoring_epoch_row()
                epoch_row.season = season
                epoch_row.server = server
                epoch_row.epoch = epoch
                epoch_row.epoch_start = epoch_start
                epoch_row.epoch_end = epoch_end
                epoch_row.epoch_coins = active_coins

                if epoch_row.server in ["KMD", "BTC", "LTC"]:
                    epoch_row.epoch_coins = [epoch_row.server]
                    epoch_row.start_event = "Season start"

                elif isinstance(SEASONS_INFO[season]["servers"][server]["epochs"][epoch]["start_event"], list):
                    epoch_row.start_event = ", ".join(scoring_season_server_epochs[epoch]["start_event"]) 

                else:
                    epoch_row.start_event = SEASONS_INFO[season]["servers"][server]["epochs"][epoch]["start_event"]


                if epoch_row.server in ["KMD", "BTC", "LTC"]:
                    epoch_row.end_event = "Season end"

                elif isinstance(SEASONS_INFO[season]["servers"][server]["epochs"][epoch]["end_event"], list):
                    epoch_row.end_event = ", ".join(SEASONS_INFO[season]["servers"][server]["epochs"][epoch]["end_event"])

                else:
                    epoch_row.end_event = SEASONS_INFO[season]["servers"][server]["epochs"][epoch]["end_event"]

                if len(epoch_row.epoch_coins) != 0:
                    epoch_row.score_per_ntx = lib_validate.calc_epoch_score(server, num_coins)
                else:
                    epoch_row.score_per_ntx = 0
                epoch_row.update()



@print_runtime
def get_dpow_scoring_window(season, server, coin):
    official_start = None
    official_end = None

    if season in SEASONS_INFO:
        official_start = SEASONS_INFO[season]["start_time"]
        official_end = SEASONS_INFO[season]["end_time"] - 1

    if season in SCORING_EPOCHS_REPO_DATA:
        if server in SCORING_EPOCHS_REPO_DATA[season]["Servers"]:
            if coin in SCORING_EPOCHS_REPO_DATA[season]["Servers"][server]:

                if "start_time" in SCORING_EPOCHS_REPO_DATA[season]["Servers"][server][coin]:
                    official_start = SCORING_EPOCHS_REPO_DATA[season]["Servers"][server][coin]["start_time"]
                if "end_time" in SCORING_EPOCHS_REPO_DATA[season]["Servers"][server][coin]:
                    official_end = SCORING_EPOCHS_REPO_DATA[season]["Servers"][server][coin]["end_time"] - 1

    scored_list, unscored_list = get_ntx_scored(season, server, coin, official_start, official_end)
    return official_start, official_end, scored_list, unscored_list


# Update notarised table epochs and score value
@print_runtime
def update_notarised_epoch_scoring(season):
    for server in SEASONS_INFO[season]["servers"]:
        for epoch in SEASONS_INFO[season]["servers"][server]["epochs"]:

            epoch_start = SEASONS_INFO[season]["servers"][server]["epochs"][epoch]['start_time']
            epoch_end = SEASONS_INFO[season]["servers"][server]["epochs"][epoch]['end_time']
            epoch_coins = SEASONS_INFO[season]["servers"][server]["epochs"][epoch]['coins']
            if season.find("Testnet") != -1:
                score_per_ntx = 1
            else:
                score_per_ntx = lib_validate.calc_epoch_score(server, len(epoch_coins))
            logger.info(f">>> Updating notarised table epochs and score value for {season} {server} {epoch} {score_per_ntx}...")

            for coin in epoch_coins:
                update_notarised_epoch_scores(
                    coin, season, server, epoch, epoch_start,
                    epoch_end, score_per_ntx, True
                )

@print_runtime
def update_ntx_tenure(season, server, coin):
    row = get_ntx_tenure(season, server, coin)
    if row is not None:
        row.update()
    else:
        row = preseason_populate_ntx_tenure(season)
        if row is not None:
            row.update()


def delete_invalid_servers():
    invalid_servers = ["Testnet", "Unofficial"]

    for server in invalid_servers:
        logger.info(f"Deleting invalid server {server} from [ntx_tenure] table...")
        row = ntx_tenure_row()
        row.delete(None, server)


def delete_invalid_seasons():

    for season in EXCLUDED_SEASONS:
        logger.info(f"Deleting invalid season {season} from [ntx_tenure] table (excluded season)...")
        row = ntx_tenure_row()
        row.delete(season)

        logger.info(f"Deleting invalid season {season} from [scoring_epochs] table (excluded season)...")
        row = scoring_epoch_row()
        row.delete(season) 

    for season in SEASONS_INFO:
        if season not in SCORING_EPOCHS_REPO_DATA and season not in EXCLUDED_SEASONS:
            logger.info(f"Deleting invalid season {season} from [scoring_epochs] table (not in scoring epochs)...")
            row = scoring_epoch_row()
            row.delete(season)


def delete_invalid_season_servers(season):
    all_notarised_servers = get_notarised_servers()
    season_servers = get_notarised_servers(season)

    for server in all_notarised_servers:
        if server not in season_servers:
            row = ntx_tenure_row()
            row.delete(season, server)


def delete_invalid_season_server_coins(season, server):
    all_notarised_coins = get_notarised_coins()
    season_server_coins = get_season_coins(season, server)

    for coin in all_notarised_coins:
        if coin not in season_server_coins or coin in DPOW_EXCLUDED_COINS[season]:
            row = ntx_tenure_row()
            row.delete(season, server, coin)
