import time
import datetime
import requests
from contacts import NN_DISCORD_IDS

class NotaryMonitor():
    def __init__(self):
        pass

    def get_last_mined(self):
        try:
            r = requests.get("https://stats.kmd.io/api/mining/notary_last_mined_table/")
            return r.json()["results"]
        except Exception as e:
            print(f"Error: {e}")
            print(f"Response: {r.content}")
            return {}

    def alert_slow_miners(self):
        msg = ""
        data = self.get_last_mined()
        now = int(time.time())
        threshold = now - 4 * 60 * 60 # 4 hours
        slow_miners = {}
        [
            slow_miners.update({
                i["name"]: datetime.timedelta(seconds=now - i["blocktime"])
            })
            for i in data
            if i["blocktime"] < threshold
        ]

        if len(slow_miners) > 1:
            msg = "**The following Notaries have not mined a block recently...**\n"
            for notary in slow_miners:
                if NN_DISCORD_IDS[notary] == "":
                    msg += f"{notary} (last mined {slow_miners[notary]} ago)\n"
                else:
                    msg += f"{NN_DISCORD_IDS[notary]} ({notary} last mined {slow_miners[notary]} ago)\n"
        return msg
