#!/usr/bin/env python3
import sys
from lib_const import *
import lib_helper as helper
from decorators import print_runtime
import lib_ntx
import lib_update_ntx

'''
At the end of a season (or after an epoch change), the ntx scores may need to be realigned to the new epoch scores.
This script will do that.
'''

scoring_epochs = get_scoring_epoch_data()
print("==============[scoring_epochs]==================")
print(scoring_epochs)
print("================================================")

coin_ranges = {}
epochs = populate_epochs()
print("==============[populate_epochs]=================")
print(epochs)
print("================================================")
for season in ["Season_6"]:
    print(season)
    for server in epochs[season]:
        print(server)
        if server not in coin_ranges:
            coin_ranges.update({
                server: {}
            })
        for epoch in epochs[season][server]:
            start = epochs[season][server][epoch]['epoch_start']
            end = epochs[season][server][epoch]['epoch_end']
            if end > 1680911999: end = 1680911999
            score = epochs[season][server][epoch]['score_per_ntx']
            coins = epochs[season][server][epoch]['coins']
            for coin in coins:
                if coin not in coin_ranges[server]:
                    coin_ranges[server].update({
                        coin: {
                            "start": start
                        }
                    })
            for coin in coin_ranges[server]:
                if coin not in coins:
                    coin_ranges[server][coin].update({
                        "end": end
                    })
            print(f"{season} {server} {epoch} {score}")

        for coin in coin_ranges[server]:
            if "end" not in coin_ranges[server][coin]:
                coin_ranges[server][coin].update({
                    "end": 1680911999
                })

        for epoch in epochs[season][server]:
            for coin in epochs[season][server][epoch]['coins']:
                score = epochs[season][server][epoch]['score_per_ntx']
                start = epochs[season][server][epoch]['epoch_start']
                end = epochs[season][server][epoch]['epoch_end']
                if end > 1680911999: end = 1680911999
                lib_update_ntx.update_notarised_epoch_scores(coin, season, server, epoch, start, end, score, True)
    


print("================[coin_ranges]===================")
print(coin_ranges)
print("================================================")

for server in coin_ranges:
    for coin in coin_ranges[server]:
        print(f"{coin}: {coin_ranges[server][coin]}")
        start = coin_ranges[server][coin]["start"]
        end = coin_ranges[server][coin]["end"]
        # zero out the scores where before season coin tenure
        lib_update_ntx.update_notarised_epoch_scores(coin=coin, epoch_start=0, epoch_end=start, score_per_ntx=0, scored=False)
        # zero out the scores where after season coin tenure
        lib_update_ntx.update_notarised_epoch_scores(coin=coin, epoch_start=end, epoch_end=9988169599, score_per_ntx=0, scored=False)


if __name__ == '__main__':
    #print(scoring_epochs['Season_6'])
    #print(epochs['Season_6'])
    print(coin_ranges)


