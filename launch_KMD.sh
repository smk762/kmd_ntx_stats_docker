#!/usr/bin/env bash
set -x

trap 'komodo-cli stop'  SIGHUP SIGINT SIGTERM

# Running ILN daemon
exec komodod -pubkey=${PUBKEY} &
tail -f ~/.komodo/debug.log & wait

set +x
