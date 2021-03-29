#!/usr/bin/env python3
import os
import json
import time
import logging
import telebot
import datetime
import threading
import concurrent.futures
from telebot import util
from telegram import ParseMode
import requests
from datetime import datetime as dt

from lib_const import *
from dotenv import load_dotenv
from logging import Handler, Formatter

load_dotenv()

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

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
        t = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')

        return "<i>{datetime}</i><pre>\n{message}</pre>".format(message=record.msg, datetime=t)

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARNING)

handler = RequestsHandler()
formatter = LogstashFormatter()
handler.setFormatter(formatter)
logger.addHandler(handler)

r = requests.get(f"{THIS_SERVER}/api/info/notary_nodes/")
notaries = r.json()["results"][0]

notaries_with_others = {}
for notary in notaries:
    r = requests.get(f"{THIS_SERVER}/api/info/notary_btc_txids?notary={notary}")
    results = r.json()["results"]["Season_4"]
    print(f"Checking {notary}")
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

msg = f"### Uncategorised Transactions ###\n"
for notary in notaries_with_others:
    print(f"{notary}")
    msg += f"### {notary} ###\n"

    for txid in notaries_with_others[notary]['txids']:
        print(txid)
        msg += f"{txid}\n"

        if len(msg) > 3200:
            print(msg)
            logger.warning(msg)
            msg = ''

if msg == f"### Uncategorised Transactions ###\n":
    pass
elif msg != '':
    print(msg)
    logger.warning(msg)

