

def get_balance_bot_data(txid):
    balance_deltas = {}
    inputs = {}
    outputs = {}
    raw_tx = rpc["KMD"].getrawtransaction(txid,1)
    src_addr = raw_tx["vin"][0]["address"]
    inputs.update({src_addr:raw_tx["vin"][0]["valueSat"]})
    if src_addr == BB_ADDR:
        block_hash = raw_tx['blockhash']
        block_time = raw_tx['blocktime']
        block_datetime = dt.utcfromtimestamp(raw_tx['blocktime'])
        this_block_height = raw_tx['height']
        vouts = raw_tx["vout"]

        for vout in vouts:
            addr = vout['scriptPubKey']['addresses'][0]
            outputs.update({addr:vout['valueSat']})
            
        balance_deltas = calc_balance_delta(inputs, outputs, balance_deltas)


def calc_balance_data(inputs, outputs, delta):
    for addr in inputs:
        if addr not in delta:
            val = inputs[addr]
            delta.update({addr:-1*val})
        else:
            val = delta[addr]-inputs[addr]
            delta.update({addr:val})

    for addr in outputs:
        if addr not in delta:
            val = outputs[addr]
            delta.update({addr:val})
        else:
            val = delta[addr]+outputs[addr]
            delta.update({addr:val})
    return deltas
