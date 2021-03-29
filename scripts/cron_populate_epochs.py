#!/usr/bin/env python3
import os
import json
import time
import requests
import logging
import logging.handlers
from lib_const import CONN, CURSOR, SCORING_EPOCHS
from models import scoring_epoch_row
from lib_notary import get_server_active_dpow_chains_at_time, get_dpow_score_value

logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s', datefmt='%d-%b-%y %H:%M:%S')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

for season in SCORING_EPOCHS:
    for server in SCORING_EPOCHS[season]:
        for epoch in SCORING_EPOCHS[season][server]:

            epoch_start = SCORING_EPOCHS["Season_4"][server][epoch]["start"]
            epoch_end = SCORING_EPOCHS["Season_4"][server][epoch]["end"]
            epoch_midpoint = int((epoch_start + epoch_end)/2)
            active_chains, num_chains = get_server_active_dpow_chains_at_time("Season_4", server, epoch_midpoint)

            epoch_row = scoring_epoch_row()
            epoch_row.season = season
            epoch_row.server = server
            epoch_row.epoch = epoch
            epoch_row.epoch_start = epoch_start
            epoch_row.epoch_end = epoch_end
            if isinstance(SCORING_EPOCHS[season][server][epoch]["start_event"], list):
                epoch_row.start_event = ", ".join(SCORING_EPOCHS[season][server][epoch]["start_event"])    
            else:
                epoch_row.start_event = SCORING_EPOCHS[season][server][epoch]["start_event"]
            if isinstance(SCORING_EPOCHS[season][server][epoch]["end_event"], list):
                epoch_row.end_event = ", ".join(SCORING_EPOCHS[season][server][epoch]["end_event"])
            else:
                epoch_row.end_event = SCORING_EPOCHS[season][server][epoch]["end_event"]
            epoch_row.epoch_chains = active_chains
            epoch_row.score_per_ntx = get_dpow_score_value(season, server, active_chains[0], epoch_midpoint)
            epoch_row.update()
    
CURSOR.close()
CONN.close()
