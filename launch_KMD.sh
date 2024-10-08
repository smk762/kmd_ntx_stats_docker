#!/usr/bin/env bash
set -x

trap 'komodo-cli stop'  SIGHUP SIGINT SIGTERM

if ! [ -f /home/komodian/.komodo/debug.log ]; then
    echo "" > /home/komodian/.komodo/debug.log
fi

exec komodod -pubkey=${PUBKEY} &
sleep 3
tail -f /home/komodian/.komodo/debug.log & wait
set +x
