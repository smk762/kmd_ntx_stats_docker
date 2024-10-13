
echo "New block: $1"
/usr/bin/python3.12 /home/smk762/kmd_ntx_stats_docker/code/scripts/cron_update_ntx_tables.py          > /home/smk762/kmd_ntx_stats_docker/code/scripts/cron_update_ntx_tables.log
/usr/bin/python3.12 /home/smk762/kmd_ntx_stats_docker/code/scripts/cron_update_mined_tables.py        > /home/smk762/kmd_ntx_stats_docker/code/scripts/cron_update_mined_tables.log