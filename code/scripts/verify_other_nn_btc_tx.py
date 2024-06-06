#!/usr/bin/env python3
import os
import json
import time
import telebot
import datetime
import threading
import concurrent.futures
from telebot import util
from telegram import ParseMode
import requests
from datetime import datetime, timezone

from dotenv import load_dotenv
from logging import Handler, Formatter
from lib_const import *

load_dotenv()

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
THIS_SERVER = os.getenv("THIS_SERVER") # IP / domain of the local server

class RequestsHandler(Handler):
    def emit(self, record):
        log_entry = self.format(record)
        payload = {
            'chat_id': TELEGRAM_CHAT_ID,
            'text': log_entry,
            'parse_mode': 'HTML'
        }
        return requests.post("https://api.telegram.org/bot{token}/sendMessage".format(token=TELEGRAM_TOKEN),
                             data=payload).content

class LogstashFormatter(Formatter):
    def __init__(self):
        super(LogstashFormatter, self).__init__()

    def format(self, record):
        t = datetime.now(timezone.utc).timestamp().strftime('%Y-%m-%d %H:%M:%S')

        return "<i>{datetime}</i><pre>\n{message}</pre>".format(message=record.msg, datetime=t)

logger = logging.getLogger()
logger.setLevel(logging.WARNING)
handler = RequestsHandler()
formatter = LogstashFormatter()
handler.setFormatter(formatter)
logger.addHandler(handler)

season = SEASON

r = requests.get(f"{THIS_SERVER}/api/info/notary_nodes/?season={season}")
notaries = r.json()["results"]

notaries_with_others = {}
for notary in notaries:
    print(f"Checking {notary}")
    params = f"?season={season}&notary={notary}&category=Other"
    r = requests.get(f"{THIS_SERVER}/api/info/notary_btc_transactions/{params}")
    results = r.json()["results"]
    if "Other" in results:
        txids = results["Other"]["txids"].keys()
        notaries_with_others.update({
            notary: {
                "count":len(txids),
                "txids":[]
                }
            })
        print(f"{notary} has {len(txids)} unrecognised transactions")
        for txid in txids:
            notaries_with_others[notary]['txids'].append(f"https://www.blockchain.com/btc/tx/{txid}")

msg = f"### Uncategorised BTC Transactions ###\n"
for notary in notaries_with_others:
    print(f"{notary}")
    msg += f"### {notary} ###\n"

    for txid in notaries_with_others[notary]['txids']:
        print(txid)
        msg += f"{txid}\n"

        if len(msg) > 2000:
            print(msg)
            logger.warning(msg)
            msg = ''

if msg == f"### Uncategorised BTC Transactions ###\n":
    pass
elif msg != '':
    print(msg)
    logger.warning(msg)

