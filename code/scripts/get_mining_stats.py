import json
from statistics import mean
import requests
import datetime as dt
import calendar
import lib_rpc
from datetime import datetime

if __name__ == '__main__':

    mining_stats = {}
    last_supply = 0
    for year in range(2018, 2024):
        mining_stats.update({year:{}})
        for month in range(1, 13):
            print(year)
            month_str = dt.datetime(year, month, 1, 0, 0).strftime("%B")
            ldom = calendar.monthrange(year, month)[1]
            min_blocktime = int(dt.datetime(year, month, 1, 0, 0).timestamp())
            max_blocktime = int(dt.datetime(year, month, ldom, 23, 59, 59).timestamp())
            url = f"http://116.203.120.91:8762/info/mined_between_blocktimes/?min_blocktime={min_blocktime}&max_blocktime={max_blocktime}"
            print(f"url: {url}")
            data = requests.get(url).json()["results"]
            if data["blocks_mined"]:
                baseline_mined_value = data["blocks_mined"] * 3
                unclaimed_rewards_mined = float(data["sum_mined"]) - baseline_mined_value
                data["sum_mined"] = float(data["sum_mined"])
                min_blocktime = data["min_blocktime"]
                max_blocktime = data["max_blocktime"]

                days_of_mining = round((max_blocktime - min_blocktime + 60)/(24*60*60))
                data.update({
                    "days_of_mining": days_of_mining,
                    "baseline_mined_value": baseline_mined_value,
                    "unclaimed_rewards_mined": unclaimed_rewards_mined,
                    "avg_blocks_per_day": data["blocks_mined"]/days_of_mining,
                    "avg_value_per_day": float(data["sum_mined"])/days_of_mining
                })
                resp = {month_str:data}
                mining_stats[year].update(resp)

                # Get coinsupply for last block of month
                r = lib_rpc.RPC["KMD"].coinsupply(str(data["max_block"]))
                data.update({"supply_at_end_of_month": r["total"]})
                if last_supply:
                    data.update({"supply_for_month": r["total"] - last_supply})
                    surplus_to_mining = r["total"] - last_supply - data["sum_mined"]
                    data.update({"claimed_rewards_for_month": surplus_to_mining})
                last_supply = r["total"]
                print(resp)
    with open(f"mining_stats_by_month.json", "w+") as j:
        json.dump(mining_stats, j, indent=4)
