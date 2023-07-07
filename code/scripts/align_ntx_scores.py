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
TODO: Use SEASONS
'''

scoring_epochs = get_scoring_epochs_repo_data()

coin_ranges = {}
epochs = populate_epochs()
for season in ["Season_7"]:
    for server in epochs[season]:
        if server not in coin_ranges:
            coin_ranges.update({
                server: {}
            })
        for epoch in epochs[season][server]:
            start = epochs[season][server][epoch]['start_time']
            end = epochs[season][server][epoch]['end_time']
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
                start = epochs[season][server][epoch]['start_time']
                end = epochs[season][server][epoch]['end_time']
                if end > 1680911999: end = 1680911999
                lib_update_ntx.update_notarised_epoch_scores(coin, season, server, epoch, start, end, score, True)
    



for server in coin_ranges:
    for coin in coin_ranges[server]:
        start = coin_ranges[server][coin]["start"]
        end = coin_ranges[server][coin]["end"]
        # zero out the scores where before season coin tenure
        lib_update_ntx.update_notarised_epoch_scores(coin=coin, epoch_start=0, epoch_end=start, score_per_ntx=0, scored=False)
        # zero out the scores where after season coin tenure
        lib_update_ntx.update_notarised_epoch_scores(coin=coin, epoch_start=end, epoch_end=9988169599, score_per_ntx=0, scored=False)


if __name__ == '__main__':
    print(coin_ranges)


