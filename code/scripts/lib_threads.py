#!/usr/bin/env python3.12
import threading

from models import BalanceRow


class update_notary_balances_thread(threading.Thread):
    def __init__(self, season, server, notary, coin, pubkey, address):
        threading.Thread.__init__(self)
        self.season = season
        self.server = server
        self.notary = notary
        self.coin = coin
        self.pubkey = pubkey
        self.address = address

    def run(self):
        update_notary_balances(
            self.season, self.server,
            self.notary, self.coin,
            self.pubkey, self.address
        )


def update_notary_balances(season, server, notary, coin, pubkey, address):
    balance = BalanceRow()
    balance.season = season
    balance.server = server
    balance.notary = notary
    balance.coin = coin
    balance.pubkey = pubkey
    balance.address = address
    balance.update()

