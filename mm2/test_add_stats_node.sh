source userpass
curl --url "http://127.0.0.1:7783" --data "{
    \"mmrpc\": \"2.0\",
    \"method\":\"add_node_to_version_stat\",
    \"userpass\":\"$userpass\",
    \"params\":{\"name\": \"seed1\",
    \"address\": \"168.119.236.241\",
    \"peer_id\": \"12D3KooWEsuiKcQaBaKEzuMtT6uFjs89P1E8MK3wGRZbeuCbCw6P\"}
}"
echo ""
