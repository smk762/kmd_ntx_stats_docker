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

pubkey = "026943ec773d7a273d56d50546583ded7bc3521a731cc9d4dba273e67c721d2832"
print(get_p2pkh_scripthash_from_pubkey(pubkey))