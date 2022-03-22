#!/usr/bin/env python3
from lib_table_select import *
from lib_table_update import *
import lib_validate
from models import ntx_tenure_row, scoring_epoch_row

def delete_invalid_servers():
    invalid_servers = ["Testnet", "Unofficial"]

    for server in invalid_servers:
        logger.info(f"Deleting invalid server {server} from [ntx_tenure] table...")
        row = ntx_tenure_row()
        row.delete(None, server)


@print_runtime
def get_server_epochs(season):
    server_epochs = {}
    servers = get_notarised_servers(season)
    for server in servers:
        server_epochs.update({
            server: get_notarised_epochs(season, server)
        })
    return server_epochs


@print_runtime
def get_server_epoch_chains(season, server_epochs):
    server_epoch_chains = {}
    for server in server_epochs:
        server_epoch_chains.update({
            server:{}
        })
        for epoch in server_epochs[server]:
            server_epoch_chains[server].update({
                epoch: get_notarised_chains(season, server, epoch)
            })
    return server_epoch_chains


def delete_invalid_seasons():

    for season in EXCLUDED_SEASONS:
        logger.info(f"Deleting invalid season {season} from [ntx_tenure] table (excluded season)...")
        row = ntx_tenure_row()
        row.delete(season)

        logger.info(f"Deleting invalid season {season} from [scoring_epochs] table (excluded season)...")
        row = scoring_epoch_row()
        row.delete(season) 

    for season in get_notarised_seasons():
        if season not in SCORING_EPOCHS and season not in EXCLUDED_SEASONS:
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


def delete_invalid_season_server_chains(season, server):
    all_notarised_chains = get_notarised_chains()
    season_server_chains = get_notarised_chains(season, server)

    for chain in all_notarised_chains:
        if chain not in season_server_chains or chain in DPOW_EXCLUDED_CHAINS[season]:
            row = ntx_tenure_row()
            row.delete(season, server, chain)


def delete_invalid_epochs(season, server):
    scoring_season_server_epochs = SCORING_EPOCHS[season][server]

    for epoch in ALL_SCORING_EPOCHS:
        if epoch not in SCORING_EPOCHS[season][server] or epoch not in scoring_season_server_epochs:
            row = scoring_epoch_row()
            row.delete(season, server, epoch)


def update_ntx_tenure(chain, season, server):
    ntx_results = get_ntx_min_max(season, chain, server) # from notarised
    max_blk = ntx_results[0]
    max_blk_time = ntx_results[1]
    min_blk = ntx_results[2]
    min_blk_time = ntx_results[3]
    total_ntx_count = ntx_results[4]

    if max_blk is not None:
        scoring_window = get_dpow_scoring_window(season, chain, server)
        official_start = scoring_window[0]
        official_end = scoring_window[1]

        if season in DPOW_EXCLUDED_CHAINS:

            if chain in DPOW_EXCLUDED_CHAINS[season]:
                season = "Unofficial"
                scored_ntx_count = 0
                unscored_ntx_count = len(scoring_window[2])+len(scoring_window[3])

            else:
                scored_ntx_count = len(scoring_window[2])
                unscored_ntx_count = len(scoring_window[3])

        elif chain in ["LTC", "BTC"]:
            scored_ntx_count = 0
            unscored_ntx_count = len(scoring_window[2])+len(scoring_window[3])

        else:
            scored_ntx_count = len(scoring_window[2])
            unscored_ntx_count = len(scoring_window[3])

        row = ntx_tenure_row()
        row.chain = chain
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
        row.update()

    else:
        now = int(time.time())
        s_start = SEASONS_INFO[season]["start_time"]

        if now < SEASONS_INFO[season]["start_time"] and s_start - now < 604800:
            print("Pre-season epoch pop!")
            row = ntx_tenure_row()
            row.chain = chain
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
            row.update()


def update_tenure(season):
    now = int(time.time())
    season_servers = SCORING_EPOCHS[season]

    for server in season_servers:
        s_start = SEASONS_INFO[season]["start_time"]

        if now < SEASONS_INFO[season]["start_time"] and s_start - now < 604800:

            print("Pre-season epoch pop!")
            if server in NEXT_SEASON_CHAINS:
                season_server_chains = NEXT_SEASON_CHAINS[server]
            else:
                season_server_chains = []

        else:
            season_server_chains = get_notarised_chains(season, server)

        for chain in season_server_chains:
            update_ntx_tenure(chain, season, server)


def update_epochs(season):
    now = int(time.time())
    logger.info(f"Processing {season}...")
    scoring_season_servers = SCORING_EPOCHS[season]
    logger.info(f"{season} scoring_season_servers: {scoring_season_servers}")

    for server in scoring_season_servers:
        scoring_season_server_epochs = SCORING_EPOCHS[season][server]

        for epoch in scoring_season_server_epochs:
            logger.info(f">>> Processing {season} {server} {epoch} epoch_row")

            epoch_start = scoring_season_server_epochs[epoch]["start"]
            epoch_end = scoring_season_server_epochs[epoch]["end"]
            epoch_midpoint = int((epoch_start + epoch_end)/2)
            s_start = SEASONS_INFO[season]["start_time"]

            if now < SEASONS_INFO[season]["start_time"] and s_start - now < 604800:

                print("Pre-season epoch pop!")
                if server in NEXT_SEASON_CHAINS:
                    active_chains = NEXT_SEASON_CHAINS[server]
                    num_chains = len(active_chains)
                else:
                    active_chains = []
                    num_chains = len(active_chains)

            else:
                active_chains, num_chains = lib_validate.get_server_active_scoring_dpow_chains_at_time(
                                                season,
                                                server,
                                                epoch_midpoint
                                            ) 

            active_chains.sort()

            if num_chains > 0:
                epoch_row = scoring_epoch_row()
                epoch_row.season = season
                epoch_row.server = server
                epoch_row.epoch = epoch
                epoch_row.epoch_start = epoch_start
                epoch_row.epoch_end = epoch_end
                epoch_row.epoch_chains = active_chains[:]

                if epoch_row.server in ["KMD", "BTC", "LTC"]:
                    epoch_row.epoch_chains = [epoch_row.server]
                    epoch_row.start_event = "Season start"

                elif isinstance(scoring_season_server_epochs[epoch]["start_event"], list):
                    epoch_row.start_event = ", ".join(scoring_season_server_epochs[epoch]["start_event"]) 

                else:
                    epoch_row.start_event = scoring_season_server_epochs[epoch]["start_event"]


                if epoch_row.server in ["KMD", "BTC", "LTC"]:
                    epoch_row.end_event = "Season end"

                elif isinstance(scoring_season_server_epochs[epoch]["end_event"], list):
                    epoch_row.end_event = ", ".join(scoring_season_server_epochs[epoch]["end_event"])

                else:
                    epoch_row.end_event = scoring_season_server_epochs[epoch]["end_event"]

                try:
                    if len(epoch_row.epoch_chains) != 0:
                        epoch_row.score_per_ntx = lib_validate.get_chain_epoch_score_at(
                                                    season,
                                                    server,
                                                    epoch_row.epoch_chains[0],
                                                    epoch_midpoint
                                                )
                    else:
                        epoch_row.score_per_ntx = 0
                    epoch_row.update()

                except Exception as e:
                    logger.warning(f"Error with processing {season} {server} {epoch} {active_chains}: {e}")


# Update notarised table epochs and score value
def update_notarised_epoch_scoring():
    epochs = get_epochs()

    for epoch in epochs:

        season = epoch['season']
        server = epoch['server']
        epoch_id = epoch['epoch']
        epoch_start = epoch['epoch_start']
        epoch_end = epoch['epoch_end']
        start_event = epoch['start_event']
        end_event = epoch['end_event']
        epoch_chains = epoch['epoch_chains']
        score_per_ntx = epoch['score_per_ntx']
        logger.info(f">>> Updating notarised table epochs and score value for {season} {server} {epoch_id} {score_per_ntx}...")

        for chain in epoch_chains:
            update_notarised_epoch_scores(
                                        chain,
                                        season,
                                        server,
                                        epoch_id,
                                        epoch_start,
                                        epoch_end,
                                        score_per_ntx,
                                        True
                                    )


def get_dpow_scoring_window(season, chain, server):

    official_start = None
    official_end = None

    if season in SEASONS_INFO:
        official_start = SEASONS_INFO[season]["start_time"]
        official_end = SEASONS_INFO[season]["end_time"]

    if season in PARTIAL_SEASON_DPOW_CHAINS:
        for partial_season_server in PARTIAL_SEASON_DPOW_CHAINS[season]["Servers"]:
            if chain in PARTIAL_SEASON_DPOW_CHAINS[season]["Servers"][partial_season_server]:
                if partial_season_server == server:
                    if "start_time" in PARTIAL_SEASON_DPOW_CHAINS[season]["Servers"][partial_season_server][chain]:
                        official_start = PARTIAL_SEASON_DPOW_CHAINS[season]["Servers"][partial_season_server][chain]["start_time"]
                    if "end_time" in PARTIAL_SEASON_DPOW_CHAINS[season]["Servers"][partial_season_server][chain]:
                        official_end = PARTIAL_SEASON_DPOW_CHAINS[season]["Servers"][partial_season_server][chain]["end_time"]
                    break

    scored_list, unscored_list = get_ntx_scored(season, chain, official_start, official_end, server)
    return official_start, official_end, scored_list, unscored_list


