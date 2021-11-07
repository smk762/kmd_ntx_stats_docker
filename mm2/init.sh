#!/bin/bash

./mm2 > ./mm2.log &
source userpass
echo $userpass
sleep 5
./version.sh
./start_stats.sh 300
tail -f ./mm2.log
