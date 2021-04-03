#!/usr/bin/env python3
import sys
import json
from lib_const import *
from cron_populate_ntx_tables import get_notarisation_data
from lib_notary import get_dpow_score_value
import logging
import logging.handlers

logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s', datefmt='%d-%b-%y %H:%M:%S')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

season = "Season_4"
server = "Main"
epoch = "Epoch_3"
notary = "mihailo_EU"
chain = "GLEEC"

CURSOR.execute("SELECT season, server, epoch, notaries, score_value, scored  \
                 FROM notarised \
                 WHERE notaries = '{}';")
resp = CURSOR.fetchall()
for item in resp:
	print(item)

epoch_midpoint = SCORING_EPOCHS[season][server][epoch]["start"]/2 + SCORING_EPOCHS[season][server][epoch]["end"]/2

score = get_dpow_score_value(season, server, coin, epoch_midpoint)
ntx_summary, chain_totals = get_notarisation_data(season, None, None, notary, chain, server, epoch)


print(json.dumps(ntx_summary, indent=4))
print(f"score: {score}")