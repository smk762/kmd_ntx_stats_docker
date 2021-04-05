#!/usr/bin/env python3
import requests
import logging
import logging.handlers
from lib_const import CONN, CURSOR, SCORING_EPOCHS, DPOW_EXCLUDED_CHAINS, SEASONS_INFO, EXCLUDED_SEASONS
from models import scoring_epoch_row, ntx_tenure_row
from lib_notary import get_server_active_dpow_chains_at_time, get_dpow_score_value, update_ntx_tenure, get_gleec_ntx_server
from lib_table_select import get_notarised_chains, get_notarised_seasons, get_notarised_servers, get_epochs
from lib_table_update import update_chain_notarised_epoch_window, update_unofficial_chain_notarised_tbl

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

all_scoring_epochs = []
for season in SCORING_EPOCHS:
    for server in SCORING_EPOCHS[season]:
        for epoch in SCORING_EPOCHS[season][server]:
            all_scoring_epochs.append(epoch)
all_scoring_epochs = list(set(all_scoring_epochs))

# Clear invalid servers
invalid_servers = ["Testnet", "Unofficial"]
for server in invalid_servers:
    row = ntx_tenure_row()
    row.delete(None, server)
    logger.info(f">>> Deleting {season} ntx_tenure_row, not in valid server")


# Update Tenure
def update_tenure(season, server=None):
    if season in EXCLUDED_SEASONS:
        row = ntx_tenure_row()
        row.delete(season)
        logger.info(f">>> Deleting {season} ntx_tenure_row, not in valid seasons")

    else:
        season_servers = get_notarised_servers(season)
        logger.info(f"{season} servers: {season_servers}")

        for server in all_notarised_servers:

            if server not in season_servers:
                row = ntx_tenure_row()
                row.delete(season, server)
                logger.info(f">>> Deleting {season} {server} ntx_tenure_row, not a valid server")

            else:
                season_server_chains = get_notarised_chains(season, server)
                logger.info(f"{season} {server} chains: {season_server_chains}")

                for chain in all_notarised_chains:

                    if chain not in season_server_chains or chain in DPOW_EXCLUDED_CHAINS[season]:
                        row = ntx_tenure_row()
                        row.delete(season, server, chain)

                    else:
                        update_ntx_tenure(chain, season, server)

# TODO: I dont think this will initialise s5 coins until they have recieved a notarisation. 
# Should probably augment with dpow readme parsing.
# Update epochs

def update_epochs(season):
    logger.info(f"Processing {season}...")

    print('\n')
    if season in EXCLUDED_SEASONS:
        logger.info(f">>> Deleting {season} epoch_row, not in valid seasons")
        row = scoring_epoch_row()
        row.delete(season)

    elif season not in SCORING_EPOCHS:
        logger.info(f">>> Deleting {season} epoch_row, season not in SCORING_EPOCHS")
        row = scoring_epoch_row()
        row.delete(season)

    else:

        scoring_season_servers = SCORING_EPOCHS[season]
        logger.info(f"{season} scoring_season_servers: {scoring_season_servers}")
        logger.info(f"all_notarised_servers: {all_notarised_servers}")

        for server in all_notarised_servers:
            print('\n')

            if server not in SCORING_EPOCHS[season]:
                logger.info(f">>> Deleting {season} epoch_row, {server} server not in SCORING_EPOCHS[season]")
                row = scoring_epoch_row()
                row.delete(season, server)

            if server not in scoring_season_servers:
                logger.info(f">>> Deleting {season} epoch_row, {server} server not in scoring_season_servers")
                row = scoring_epoch_row()
                row.delete(season, server)



            else:
                scoring_season_server_epochs = SCORING_EPOCHS[season][server]
                logger.info(f"{season} {server} scoring_season_server_epochs: {scoring_season_server_epochs}")
                logger.info(f"{season} {server} epochs: {list(scoring_season_server_epochs.keys())}")


                for epoch in all_scoring_epochs:
                    print('\n')
                    if epoch not in SCORING_EPOCHS[season][server]:
                        logger.info(f">>> Deleting {season} {server} {epoch} epoch_row, {epoch} not in SCORING_EPOCHS[season][server]")
                        row = scoring_epoch_row()
                        row.delete(season, server, epoch)

                    if epoch not in scoring_season_server_epochs:
                        logger.info(f">>> Deleting {season} {server} {epoch} epoch_row, {epoch} not in scoring_season_server_epochs")
                        row = scoring_epoch_row()
                        row.delete(season, server, epoch)

                    else:
                        logger.info(f">>> Processing {season} {server} {epoch} epoch_row")

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

                        except Exception as e:
                            logger.warning(f"Error with processing {season} {server} {epoch} {active_chains}: {e}")
                            epoch_row.score_per_ntx = 0

                        epoch_row.update()
                        logger.info(f">>> Updated {season} {server} {epoch} epoch_row\n")


# Update notarised table epochs and score value
def update_notarised_epoch_scoring():
    epochs = get_epochs()
    logger.info(f">>> Updating notarised table epochs and score value...\n")


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
        logger.info(f">>> Updating notarised table epochs and score value for {season} {server} {epoch_id} {score_per_ntx}...\n")

        for chain in epoch_chains:
            logger.info(f"{chain} {season} {server} {epoch_id} | Blocks {epoch_start} - {epoch_end} | scored True {score_per_ntx}\n")

            if chain != "GLEEC":
                update_chain_notarised_epoch_window(chain, season, server, epoch_id, epoch_start, epoch_end, score_per_ntx, True)

update_tenure("Season_4", "KMD")
update_tenure("Season_4", "BTC")
update_epochs("Season_4")

for season in all_notarised_seasons:

    update_tenure(season)
    update_epochs(season)

update_notarised_epoch_scoring()

CURSOR.close()
CONN.close()
