#!/usr/bin/env python3
import requests
import logging
import logging.handlers
from lib_const import CONN, CURSOR, SCORING_EPOCHS
from models import scoring_epoch_row, ntx_tenure_row
from lib_notary import get_server_active_dpow_chains_at_time, get_dpow_score_value, update_ntx_tenure, get_gleec_ntx_server
from lib_table_select import get_notarised_chains, get_notarised_seasons, get_notarised_servers, get_epochs
from lib_table_update import update_chain_notarised_epoch_window

logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s', datefmt='%d-%b-%y %H:%M:%S')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# First tenure then epochs

all_notarised_seasons = get_notarised_seasons()
all_notarised_servers = get_notarised_servers()
all_notarised_chains = get_notarised_chains()

for season in all_notarised_seasons:

    if season in ["Season_1", "Season_2", "Season_3", "Unofficial"]:
        row = ntx_tenure_row()
        row.delete(season)

    else:

        season_servers = get_notarised_servers(season)
        logger.info(f"{season} servers: {season_servers}")

        for server in all_notarised_servers:

            if server not in season_servers:
                row = ntx_tenure_row()
                row.delete(season, server)

            else:
                season_server_chains = get_notarised_chains(season, server)
                logger.info(f"{season} {server} chains: {season_server_chains}")

                for chain in all_notarised_chains:

                    if chain not in season_server_chains:
                        row = ntx_tenure_row()
                        row.delete(season, server, chain)

                    else:
                        if season == "Testnet":
                            server = "Main"
                        update_ntx_tenure(chain, season, server)


all_scoring_epochs = []
for season in SCORING_EPOCHS:
    for server in SCORING_EPOCHS[season]:
        for epoch in SCORING_EPOCHS[season][server]:
            all_scoring_epochs.append(epoch)
all_scoring_epochs = list(set(all_scoring_epochs))

for season in all_notarised_seasons:

    if season in ["Season_1", "Season_2", "Season_3", "Unofficial"] or season not in SCORING_EPOCHS:
        row = scoring_epoch_row()
        row.delete(season)

    else:
        scoring_season_servers = SCORING_EPOCHS[season]

        for server in all_notarised_servers:

                if server not in scoring_season_servers:

                    row = scoring_epoch_row()
                    row.delete(season, server)

                else:
                    scoring_season_server_epochs = SCORING_EPOCHS[season][server]
                    logger.info(f"{season} {server} epochs: {list(scoring_season_server_epochs.keys())}")

                    for epoch in all_scoring_epochs:

                        if epoch not in scoring_season_server_epochs:
                            row = scoring_epoch_row()
                            row.delete(season, server, epoch)

                        else:

                            epoch_start = scoring_season_server_epochs[epoch]["start"]
                            epoch_end = scoring_season_server_epochs[epoch]["end"]
                            epoch_midpoint = int((epoch_start + epoch_end)/2)
                            active_chains, num_chains = get_server_active_dpow_chains_at_time(season, server, epoch_midpoint) 

                            epoch_row = scoring_epoch_row()
                            epoch_row.season = season
                            epoch_row.server = server
                            epoch_row.epoch = epoch
                            epoch_row.epoch_start = epoch_start
                            epoch_row.epoch_end = epoch_end
                            epoch_row.epoch_chains = active_chains

                            if isinstance(scoring_season_server_epochs[epoch]["start_event"], list):
                                epoch_row.start_event = ", ".join(scoring_season_server_epochs[epoch]["start_event"]) 

                            else:
                                epoch_row.start_event = scoring_season_server_epochs[epoch]["start_event"]


                            if isinstance(scoring_season_server_epochs[epoch]["end_event"], list):
                                epoch_row.end_event = ", ".join(scoring_season_server_epochs[epoch]["end_event"])

                            else:
                                epoch_row.end_event = scoring_season_server_epochs[epoch]["end_event"]


                            try:
                                # checks tenure
                                epoch_row.score_per_ntx = get_dpow_score_value(season, server, active_chains[0], epoch_midpoint)

                            except:
                                logger.warning(f"{season} {server} {epoch} {active_chains}")
                                epoch_row.score_per_ntx = 0

                            epoch_row.update()

# Update notarised table epochs and score value
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

    for chain in epoch_chains:
        if chain == "GLEEC":
            server = get_gleec_ntx_server(txid)
        update_chain_notarised_epoch_window(chain, season, server, epoch_id, epoch_start, epoch_end, score_per_ntx, True)

        


CURSOR.close()
CONN.close()
