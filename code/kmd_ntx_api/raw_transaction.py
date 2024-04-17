import time
from kmd_ntx_api.electrum import broadcast_raw_tx, get_coin_electrum
from kmd_ntx_api.based_58 import get_hex, lil_endian, address_to_p2pkh
from kmd_ntx_api.helper import get_or_none

class raw_tx():
    def __init__(self, version='04000080', group_id='85202f89',
                 inputs=list, sequence='feffffff', outputs=list,
                 expiry_ht='00000000', locktime=int(time.time()-5*60),
                 valueBalanceSapling="0000000000000000",
                 nSpendsSapling="0", vSpendsSapling="00",
                 nOutputsSapling="0", vOutputsSapling="00"):
        self.version = version
        self.group_id = group_id
        self.inputs = inputs
        self.sequence = sequence
        self.outputs = outputs
        # TODO: by default, 200 blocks past current tip
        self.expiry_ht = expiry_ht
        self.locktime = locktime
        self.valueBalanceSapling = valueBalanceSapling
        self.nSpendsSapling = nSpendsSapling
        self.vSpendsSapling = vSpendsSapling
        self.nOutputsSapling = nOutputsSapling
        self.vOutputsSapling = vOutputsSapling

    def construct(self):
        self.locktime = lil_endian(get_hex(self.locktime, byte_length=8))
        self.raw_tx_str = self.version+self.group_id
        self.len_inputs = get_hex(len(self.inputs), byte_length=2)
        self.raw_tx_str += self.len_inputs
        self.expiry_ht = lil_endian(
            get_hex(int(self.expiry_ht), byte_length=8))
        self.sum_inputs = 0
        for vin in self.inputs:
            self.raw_tx_str += lil_endian(vin["tx_hash"])
            self.raw_tx_str += lil_endian(
                get_hex(vin["tx_pos"], byte_length=8))
            self.sum_inputs += vin["value"]*100000000
            if "unlocking_script" in vin:
                unlocking_script = vin["unlocking_script"]
            else:
                unlocking_script = ""
            pubkey = vin["scriptPubKey"]
            self.len_script = get_hex(
                len(unlocking_script+"0121"+pubkey)/2, byte_length=2)

            if unlocking_script == "":
                self.raw_tx_str += "00"
            else:
                self.raw_tx_str += self.len_script
                self.raw_tx_str += unlocking_script
                self.raw_tx_str += "0121"
                self.raw_tx_str += lil_endian(pubkey)

            self.raw_tx_str += self.sequence
        self.sum_outputs = 0
        self.len_outputs = get_hex(len(self.outputs), byte_length=2)
        self.raw_tx_str += self.len_outputs
        i = 0
        for vout in self.outputs:
            amount = float(vout["amount"])*100000000
            self.sum_outputs += amount
            self.raw_tx_str += lil_endian(get_hex(amount, byte_length=16))
            address = vout["address"]
            pubKeyHash = address_to_p2pkh(address)
            self.raw_tx_str += get_hex(len(pubKeyHash)/2, byte_length=2)
            self.raw_tx_str += pubKeyHash
        self.raw_tx_str += self.locktime
        self.raw_tx_str += self.expiry_ht
        self.raw_tx_str += self.valueBalanceSapling
        self.raw_tx_str += self.nSpendsSapling
        self.raw_tx_str += self.vSpendsSapling
        self.raw_tx_str += self.nOutputsSapling
        self.raw_tx_str += self.vOutputsSapling
        return self.raw_tx_str

def send_raw_tx(request):
    coin = get_or_none(request, "coin")
    raw_tx = get_or_none(request, "raw_tx")

    if not coin or not raw_tx:
        return {
            "error":f"Missing params! must specify 'coin' and 'raw_tx' like ?coin=KMD&raw_tx=0400008085202f89010000000000000000000000000000000000000000000000000000000000000000ffffffff0603e3be150101ffffffff016830e2110000000023210360b4805d885ff596f94312eed3e4e17cb56aa8077c6dd78d905f8de89da9499fac3d241b5d000000000000000000000000000000"
        }

    url, port, ssl = get_coin_electrum(coin)

    if not url:
        return { "error":f"No electrums found for {coin}" }

    return broadcast_raw_tx(url, port, raw_tx, ssl)
