#!/usr/bin/env python3.12
import sys
import time
import json
import random
import requests
import lib_vote
import binascii
from lib_rpc import RPC
import lib_urls as urls
from notary_candidates import CANDIDATE_ADDRESSES
from notary_pubkeys import NOTARY_PUBKEYS

PUBKEY = "03f7e4f3dfff18aa16ef409d5973397dc968f9077a21acef0c4af3b4829c2a9fb5"
VOTE_YEAR = "VOTE2022"
change_address = "REu6rTwwgaL9UxWHWUPVHQW3FHuDraGonx"
reward_amount = 0.762

if __name__ == "__main__":

    # get last 5 mins of ntx
    since = time.time() - 1200
    url = urls.get_notarised_source_url(local=True, season="VOTE2022_Testnet", min_blocktime=since)
    r = requests.get(url)
    ntx = r.json()['results']

    r = requests.get(urls.get_proposals_url(True, "VOTE2022"))
    proposals = r.json()["results"]
    proposal_nodes = lib_vote.get_proposal_nodes()

    if len(ntx) == 0:
        print("No ntx detected!")
        sys.exit()

    print(f"{len(ntx)} ntx detected!")

    with open('/home/smk762/kmd_ntx_stats_docker/code/scripts/rewarded_ntx.json', 'r') as f:
        rewarded_ntx = json.load(f)

    with open('/home/smk762/kmd_ntx_stats_docker/code/scripts/used_utxos.json', 'r') as f:
        used_utxos = json.load(f)

    vouts = {}
    for item in ntx:
        notaries = item["notaries"]
        ac_height = item["ac_ntx_height"]
        coin = item["coin"]

        if coin not in rewarded_ntx:
            rewarded_ntx.update({coin:[]})

        if ac_height not in rewarded_ntx[coin]:
            msg = f"VOTE2022 Testnet bonus! {coin}:{ac_height}"
            msg_hex = binascii.hexlify(bytes(msg, 'utf-8'))


            # get a utxo
            url = urls.get_utxos_url(True, "VOTE2022", PUBKEY)
            r = requests.get(url)
            utxos = r.json()["results"]["utxos"]
            for utxo in utxos:
                utxo_ref = f'{utxo["tx_hash"]}_{utxo["tx_pos"]}'

                if utxo_ref in used_utxos:
                    print(f"{utxo_ref} already used!")
                else:
                    amount = utxo["value"] / 100000000
                    if amount > 5:
                        input_utxo = [{"txid": utxo["tx_hash"], "vout": utxo["tx_pos"]}]
                        input_value = float(amount)
                        used_utxos.append(utxo_ref)
                        
                        # Get notary vote addresses
                        for notary in notaries:
                        
                            notary = lib_vote.translate_testnet_name(notary, proposal_nodes.keys())
                            if notary in proposal_nodes:

                                notary_addresses = proposal_nodes[notary]
                                address = random.choice(list(notary_addresses.values()))
                                vouts.update({
                                    address: reward_amount
                                })

                            else:
                                print(f"{notary} not in proposal nodes")

                        remaining_input_value = round(input_value - (reward_amount * len(vouts)) - 0.0001, 5)
                        vouts.update({
                            change_address: remaining_input_value,
                            "data": msg_hex.decode('ascii')
                        })

                        try:
                            rawhex = RPC[VOTE_YEAR].createrawtransaction(input_utxo, vouts)
                            print(f"rawhex: {rawhex}")
                            time.sleep(0.1)
                            signedhex = RPC[VOTE_YEAR].signrawtransaction(rawhex)
                            print(f"signedhex: {signedhex}")
                            time.sleep(0.1)
                            txid = RPC[VOTE_YEAR].sendrawtransaction(signedhex["hex"])
                            print(f"Sent {reward_amount} each to {notaries} for {coin}:{ac_height}")
                            print(f"txid: {txid}")
                            time.sleep(0.1)
                        except Exception as e:
                            print(e)
                            print(utxo)
                            print(vouts)



                        rewarded_ntx[coin].append(ac_height)
                        break
                    else:
                        print("utxo too small")
        else:
            print("ntx already rewarded")

    json.dump(used_utxos, open('used_utxos.json', 'w+'))
    json.dump(rewarded_ntx, open('rewarded_ntx.json', 'w+'))
