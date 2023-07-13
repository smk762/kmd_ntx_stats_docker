import os
import sys
import time
import json
import requests
from os.path import expanduser, dirname, realpath

def refresh_external_data(file, url):
    if not os.path.exists(file):
        data = requests.get(url).json()
        with open(file, "w") as f:
            json.dump(data, f, indent=4)
    now = int(time.time())
    mtime = os.path.getmtime(file)
    if now - mtime > 86400 * 7: # 7 days
        data = requests.get(url).json()
        with open(file, "w") as f:
            json.dump(data, f, indent=4)
    with open(file, "r") as f:
        return json.load(f)

HOME = expanduser('~')
SCRIPT_PATH = dirname(realpath(sys.argv[0]))

COINS_CONFIG_URL = "https://raw.githubusercontent.com/KomodoPlatform/coins/master/utils/coins_config.json"
COINS_CONFIG_PATH = f"{SCRIPT_PATH}/coins_config.json"
VERSION_TIMESPANS = refresh_external_data(COINS_CONFIG_PATH, COINS_CONFIG_URL)

VERSION_TIMESPANS_URL = "https://raw.githubusercontent.com/KomodoPlatform/dPoW/seednode-update/doc/seed_version_epochs.json"
VERSION_TIMESPANS_PATH = f"{SCRIPT_PATH}/seed_version_epochs.json"
VERSION_TIMESPANS = refresh_external_data(VERSION_TIMESPANS_PATH, VERSION_TIMESPANS_URL)
