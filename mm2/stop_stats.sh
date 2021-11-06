#!/bin/bash
source ./userpass
curl --url "http://127.0.0.1:7783" --data "{\"mmrpc\": \"2.0\",\"method\":\"stop_version_stat_collection\",\"userpass\":\"$userpass\",\"params\":{}}"

echo ""

