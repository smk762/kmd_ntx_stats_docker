#!/usr/bin/env python3

import requests
import socket
import json
import time
import hashlib
import codecs
import logging
from base_58 import *
from lib_const import *
from lib_electrum import *


logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s', datefmt='%d-%b-%y %H:%M:%S')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

pubkey = "0227e5cad3731e381df157de189527aac8eb50d82a13ce2bd81153984ebc749515"
for chain in ANTARA_COINS:
	logger.info(f"num {chain} utxos: {get_listunspent(chain, pubkey)}")