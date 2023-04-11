#!/bin/bash

./collect_seednode_stats.py rectify_scores
./cron_update_ntx_tables.py rescan
./align_ntx_scores.py