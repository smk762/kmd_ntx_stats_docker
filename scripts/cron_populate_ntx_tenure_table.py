#!/usr/bin/env python3
import logging
import logging.handlers
import requests
from lib_notary import *
from lib_table_select import *

# TODO: deliniate 3P server as separate season.

logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s', datefmt='%d-%b-%y %H:%M:%S')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

notarised_chains = get_notarised_chains()
notarised_seasons = get_notarised_seasons()

update_ntx_tenure(notarised_chains, notarised_seasons)