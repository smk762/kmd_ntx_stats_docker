import os
import sys
import time
import json
import requests
from os.path import expanduser, dirname, realpath

def refresh_external_data(file, url):
    if not os.path.exists(file):
        data = requests.get(url).json()
        with open(file, "w+") as f:
            json.dump(data, f, indent=4)
    now = int(time.time())
    mtime = os.path.getmtime(file)
    if now - mtime > 86400: # 24 hrs
        data = requests.get(url).json()
        with open(file, "w+") as f:
            json.dump(data, f, indent=4)
    with open(file, "r") as f:
        return json.load(f)

HOME = expanduser('~')
SCRIPT_PATH = dirname(realpath(sys.argv[0]))
os.makedirs(f"{SCRIPT_PATH}/cache", exist_ok=True)

# Unified coins config
COINS_CONFIG_URL = "https://raw.githubusercontent.com/KomodoPlatform/coins/master/utils/coins_config.json"
COINS_CONFIG_PATH = f"{SCRIPT_PATH}/cache/coins_config.json"

# Seed node version epochs
VERSION_TIMESPANS_URL = "https://raw.githubusercontent.com/KomodoPlatform/dPoW/seednode-update/doc/seed_version_epochs.json"
VERSION_TIMESPANS_PATH = f"{SCRIPT_PATH}/cache/seed_version_epochs.json"

# Links to ecosystem sites
ECOSYSTEM_LINKS_URL = "https://raw.githubusercontent.com/gcharang/data/master/info/ecosystem.json"
ECOSYSTEM_LINKS_PATH = f"{SCRIPT_PATH}/cache/ecosystem.json"

def coins_config():
    return refresh_external_data(COINS_CONFIG_PATH, COINS_CONFIG_URL)

def version_timespans():
    return refresh_external_data(VERSION_TIMESPANS_PATH, VERSION_TIMESPANS_URL)

def ecosystem_links():
    return refresh_external_data(ECOSYSTEM_LINKS_PATH, ECOSYSTEM_LINKS_URL)

