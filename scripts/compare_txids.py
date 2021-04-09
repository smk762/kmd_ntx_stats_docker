#!/usr/bin/env python3
import csv
import json
import math
import time
import requests
from lib_notary import *
from cron_populate_ntx_tables import *
from lib_const import *

chain_epochs = {
  "AYA": {
    "Third_Party": {
      "Epoch_1": {
        "start": 1593331689,
        "end": 1603623833
      },
      "Epoch_4": {
        "start": 1606390840,
        "end": 1617364799
      },
      "Epoch_3": {
        "start": 1603710234,
        "end": 1606390839
      },
      "Epoch_2": {
        "start": 1603623834,
        "end": 1603710233
      },
      "Epoch_0": {
        "start": 1592146800,
        "end": 1593331688
      }
    }
  },
  "CHIPS": {
    "Third_Party": {
      "Epoch_1": {
        "start": 1593331689,
        "end": 1603623833
      },
      "Epoch_4": {
        "start": 1606390840,
        "end": 1617364799
      },
      "Epoch_3": {
        "start": 1603710234,
        "end": 1606390839
      },
      "Epoch_2": {
        "start": 1603623834,
        "end": 1603710233
      },
      "Epoch_0": {
        "start": 1592146800,
        "end": 1593331688
      }
    }
  },
  "EMC2": {
    "Third_Party": {
      "Epoch_1": {
        "start": 1593331689,
        "end": 1603623833
      },
      "Epoch_4": {
        "start": 1606390840,
        "end": 1617364799
      },
      "Epoch_3": {
        "start": 1603710234,
        "end": 1606390839
      },
      "Epoch_2": {
        "start": 1603623834,
        "end": 1603710233
      },
      "Epoch_0": {
        "start": 1592146800,
        "end": 1593331688
      }
    }
  },
  "HUSH3": {
    "Third_Party": {
      "Epoch_1": {
        "start": 1593331689,
        "end": 1603623833
      }
    }
  },
  "MCL": {
    "Third_Party": {
      "Epoch_1": {
        "start": 1593331689,
        "end": 1603623833
      },
      "Epoch_4": {
        "start": 1606390840,
        "end": 1617364799
      },
      "Epoch_3": {
        "start": 1603710234,
        "end": 1606390839
      },
      "Epoch_2": {
        "start": 1603623834,
        "end": 1603710233
      }
    }
  },
  "VRSC": {
    "Third_Party": {
      "Epoch_1": {
        "start": 1593331689,
        "end": 1603623833
      },
      "Epoch_4": {
        "start": 1606390840,
        "end": 1617364799
      },
      "Epoch_3": {
        "start": 1603710234,
        "end": 1606390839
      },
      "Epoch_2": {
        "start": 1603623834,
        "end": 1603710233
      },
      "Epoch_0": {
        "start": 1592146800,
        "end": 1593331688
      }
    }
  },
  "AXO": {
    "Main": {
      "Epoch_3": {
        "start": 1617181776,
        "end": 1617364799
      },
      "Epoch_2": {
        "start": 1616250930,
        "end": 1617181775
      },
      "Epoch_0": {
        "start": 1592146800,
        "end": 1613769735
      },
      "Epoch_1": {
        "start": 1613769736,
        "end": 1616250929
      }
    }
  },
  "BET": {
    "Main": {
      "Epoch_3": {
        "start": 1617181776,
        "end": 1617364799
      },
      "Epoch_2": {
        "start": 1616250930,
        "end": 1617181775
      },
      "Epoch_0": {
        "start": 1592146800,
        "end": 1613769735
      },
      "Epoch_1": {
        "start": 1613769736,
        "end": 1616250929
      }
    }
  },
  "BOTS": {
    "Main": {
      "Epoch_3": {
        "start": 1617181776,
        "end": 1617364799
      },
      "Epoch_2": {
        "start": 1616250930,
        "end": 1617181775
      },
      "Epoch_0": {
        "start": 1592146800,
        "end": 1613769735
      },
      "Epoch_1": {
        "start": 1613769736,
        "end": 1616250929
      }
    }
  },
  "BTCH": {
    "Main": {
      "Epoch_3": {
        "start": 1617181776,
        "end": 1617364799
      },
      "Epoch_2": {
        "start": 1616250930,
        "end": 1617181775
      },
      "Epoch_0": {
        "start": 1592146800,
        "end": 1613769735
      },
      "Epoch_1": {
        "start": 1613769736,
        "end": 1616250929
      }
    }
  },
  "CCL": {
    "Main": {
      "Epoch_3": {
        "start": 1617181776,
        "end": 1617364799
      },
      "Epoch_2": {
        "start": 1616250930,
        "end": 1617181775
      },
      "Epoch_0": {
        "start": 1592146800,
        "end": 1613769735
      },
      "Epoch_1": {
        "start": 1613769736,
        "end": 1616250929
      }
    }
  },
  "COQUICASH": {
    "Main": {
      "Epoch_3": {
        "start": 1617181776,
        "end": 1617364799
      },
      "Epoch_2": {
        "start": 1616250930,
        "end": 1617181775
      },
      "Epoch_0": {
        "start": 1592146800,
        "end": 1613769735
      },
      "Epoch_1": {
        "start": 1613769736,
        "end": 1616250929
      }
    }
  },
  "CRYPTO": {
    "Main": {
      "Epoch_3": {
        "start": 1617181776,
        "end": 1617364799
      },
      "Epoch_2": {
        "start": 1616250930,
        "end": 1617181775
      },
      "Epoch_0": {
        "start": 1592146800,
        "end": 1613769735
      },
      "Epoch_1": {
        "start": 1613769736,
        "end": 1616250929
      }
    }
  },
  "DEX": {
    "Main": {
      "Epoch_3": {
        "start": 1617181776,
        "end": 1617364799
      },
      "Epoch_2": {
        "start": 1616250930,
        "end": 1617181775
      },
      "Epoch_0": {
        "start": 1592146800,
        "end": 1613769735
      },
      "Epoch_1": {
        "start": 1613769736,
        "end": 1616250929
      }
    }
  },
  "GLEEC": {
    "Main": {
      "Epoch_3": {
        "start": 1617181776,
        "end": 1617364799
      }
    },
    "Third_Party": {
      "Epoch_4": {
        "start": 1606390840,
        "end": 1617364799
      },
      "Epoch_3": {
        "start": 1603710234,
        "end": 1606390839
      }
    }
  },
  "HODL": {
    "Main": {
      "Epoch_3": {
        "start": 1617181776,
        "end": 1617364799
      },
      "Epoch_2": {
        "start": 1616250930,
        "end": 1617181775
      },
      "Epoch_0": {
        "start": 1592146800,
        "end": 1613769735
      },
      "Epoch_1": {
        "start": 1613769736,
        "end": 1616250929
      }
    }
  },
  "ILN": {
    "Main": {
      "Epoch_3": {
        "start": 1617181776,
        "end": 1617364799
      },
      "Epoch_2": {
        "start": 1616250930,
        "end": 1617181775
      },
      "Epoch_0": {
        "start": 1592146800,
        "end": 1613769735
      },
      "Epoch_1": {
        "start": 1613769736,
        "end": 1616250929
      }
    }
  },
  "JUMBLR": {
    "Main": {
      "Epoch_3": {
        "start": 1617181776,
        "end": 1617364799
      },
      "Epoch_2": {
        "start": 1616250930,
        "end": 1617181775
      },
      "Epoch_0": {
        "start": 1592146800,
        "end": 1613769735
      },
      "Epoch_1": {
        "start": 1613769736,
        "end": 1616250929
      }
    }
  },
  "KOIN": {
    "Main": {
      "Epoch_3": {
        "start": 1617181776,
        "end": 1617364799
      },
      "Epoch_2": {
        "start": 1616250930,
        "end": 1617181775
      },
      "Epoch_0": {
        "start": 1592146800,
        "end": 1613769735
      },
      "Epoch_1": {
        "start": 1613769736,
        "end": 1616250929
      }
    }
  },
  "MESH": {
    "Main": {
      "Epoch_3": {
        "start": 1617181776,
        "end": 1617364799
      },
      "Epoch_2": {
        "start": 1616250930,
        "end": 1617181775
      },
      "Epoch_0": {
        "start": 1592146800,
        "end": 1613769735
      },
      "Epoch_1": {
        "start": 1613769736,
        "end": 1616250929
      }
    }
  },
  "MGW": {
    "Main": {
      "Epoch_3": {
        "start": 1617181776,
        "end": 1617364799
      },
      "Epoch_2": {
        "start": 1616250930,
        "end": 1617181775
      },
      "Epoch_0": {
        "start": 1592146800,
        "end": 1613769735
      },
      "Epoch_1": {
        "start": 1613769736,
        "end": 1616250929
      }
    }
  },
  "MORTY": {
    "Main": {
      "Epoch_3": {
        "start": 1617181776,
        "end": 1617364799
      },
      "Epoch_2": {
        "start": 1616250930,
        "end": 1617181775
      },
      "Epoch_0": {
        "start": 1592146800,
        "end": 1613769735
      },
      "Epoch_1": {
        "start": 1613769736,
        "end": 1616250929
      }
    }
  },
  "MSHARK": {
    "Main": {
      "Epoch_3": {
        "start": 1617181776,
        "end": 1617364799
      },
      "Epoch_2": {
        "start": 1616250930,
        "end": 1617181775
      },
      "Epoch_0": {
        "start": 1592146800,
        "end": 1613769735
      },
      "Epoch_1": {
        "start": 1613769736,
        "end": 1616250929
      }
    }
  },
  "NINJA": {
    "Main": {
      "Epoch_3": {
        "start": 1617181776,
        "end": 1617364799
      },
      "Epoch_2": {
        "start": 1616250930,
        "end": 1617181775
      },
      "Epoch_0": {
        "start": 1592146800,
        "end": 1613769735
      },
      "Epoch_1": {
        "start": 1613769736,
        "end": 1616250929
      }
    }
  },
  "OOT": {
    "Main": {
      "Epoch_3": {
        "start": 1617181776,
        "end": 1617364799
      },
      "Epoch_2": {
        "start": 1616250930,
        "end": 1617181775
      },
      "Epoch_0": {
        "start": 1592146800,
        "end": 1613769735
      },
      "Epoch_1": {
        "start": 1613769736,
        "end": 1616250929
      }
    }
  },
  "PANGEA": {
    "Main": {
      "Epoch_3": {
        "start": 1617181776,
        "end": 1617364799
      },
      "Epoch_2": {
        "start": 1616250930,
        "end": 1617181775
      },
      "Epoch_0": {
        "start": 1592146800,
        "end": 1613769735
      },
      "Epoch_1": {
        "start": 1613769736,
        "end": 1616250929
      }
    }
  },
  "PIRATE": {
    "Main": {
      "Epoch_3": {
        "start": 1617181776,
        "end": 1617364799
      },
      "Epoch_2": {
        "start": 1616250930,
        "end": 1617181775
      },
      "Epoch_0": {
        "start": 1592146800,
        "end": 1613769735
      },
      "Epoch_1": {
        "start": 1613769736,
        "end": 1616250929
      }
    }
  },
  "REVS": {
    "Main": {
      "Epoch_3": {
        "start": 1617181776,
        "end": 1617364799
      },
      "Epoch_2": {
        "start": 1616250930,
        "end": 1617181775
      },
      "Epoch_0": {
        "start": 1592146800,
        "end": 1613769735
      },
      "Epoch_1": {
        "start": 1613769736,
        "end": 1616250929
      }
    }
  },
  "RICK": {
    "Main": {
      "Epoch_3": {
        "start": 1617181776,
        "end": 1617364799
      },
      "Epoch_2": {
        "start": 1616250930,
        "end": 1617181775
      },
      "Epoch_0": {
        "start": 1592146800,
        "end": 1613769735
      },
      "Epoch_1": {
        "start": 1613769736,
        "end": 1616250929
      }
    }
  },
  "SUPERNET": {
    "Main": {
      "Epoch_3": {
        "start": 1617181776,
        "end": 1617364799
      },
      "Epoch_2": {
        "start": 1616250930,
        "end": 1617181775
      },
      "Epoch_0": {
        "start": 1592146800,
        "end": 1613769735
      },
      "Epoch_1": {
        "start": 1613769736,
        "end": 1616250929
      }
    }
  },
  "THC": {
    "Main": {
      "Epoch_3": {
        "start": 1617181776,
        "end": 1617364799
      },
      "Epoch_2": {
        "start": 1616250930,
        "end": 1617181775
      },
      "Epoch_0": {
        "start": 1592146800,
        "end": 1613769735
      },
      "Epoch_1": {
        "start": 1613769736,
        "end": 1616250929
      }
    }
  },
  "VOTE2021": {
    "Main": {
      "Epoch_3": {
        "start": 1617181776,
        "end": 1617364799
      }
    }
  },
  "WLC21": {
    "Main": {
      "Epoch_3": {
        "start": 1617181776,
        "end": 1617364799
      },
      "Epoch_2": {
        "start": 1616250930,
        "end": 1617181775
      },
      "Epoch_0": {
        "start": 1592146800,
        "end": 1613769735
      },
      "Epoch_1": {
        "start": 1613769736,
        "end": 1616250929
      }
    }
  },
  "ZILLA": {
    "Main": {
      "Epoch_3": {
        "start": 1617181776,
        "end": 1617364799
      },
      "Epoch_2": {
        "start": 1616250930,
        "end": 1617181775
      },
      "Epoch_0": {
        "start": 1592146800,
        "end": 1613769735
      },
      "Epoch_1": {
        "start": 1613769736,
        "end": 1616250929
      }
    }
  },
  "PGT": {
    "Main": {
      "Epoch_0": {
        "start": 1592146800,
        "end": 1613769735
      },
      "Epoch_1": {
        "start": 1613769736,
        "end": 1616250929
      }
    }
  },
  "RFOX": {
    "Main": {
      "Epoch_0": {
        "start": 1592146800,
        "end": 1613769735
      }
    }
  },
  "STBL": {
    "Main": {
      "Epoch_0": {
        "start": 1592146800,
        "end": 1613769735
      },
      "Epoch_1": {
        "start": 1613769736,
        "end": 1616250929
      }
    }
  },
  "PBC": {
    "Third_Party": {
      "Epoch_4": {
        "start": 1606390840,
        "end": 1617364799
      }
    }
  }
}

decker_txid_list = []
smk_txid_list = []
decker_txid_dict = {}
smk_txid_dict = {}

CURSOR.execute("SELECT txid, chain FROM notarised WHERE season='Season_4' and score_value > 0 and chain != 'BTC' ORDER BY block_time ASC, chain ASC;")

results = CURSOR.fetchall()
print(f"{len(results)} txids in [notarised] table")


for item in results:
    txid = item[0]
    chain = item[1]
    smk_txid_list.append(txid)
    if chain not in smk_txid_dict:
        smk_txid_dict.update({chain:[]})
    smk_txid_dict[chain].append(txid)


with open('s4-stats-txes-time.csv', 'r') as csv_file:

    reader = list(csv.reader(csv_file))
    row_count = len(reader)

    print(f"{row_count} [decker] records to scan...")

    i = 0
    for row in reader:
        txid = row[0]
        #notaries = row[1]
        chain= row[2]
        #block = row[3]
        #block_time = row[4]
        decker_txid_list.append(txid)
        if chain not in decker_txid_dict:
            decker_txid_dict.update({chain:[]})
        decker_txid_dict[chain].append(txid)


smk_missing_txids = list(set(decker_txid_list).difference(set(smk_txid_list)))
decker_missing_txids = list(set(smk_txid_list).difference(set(decker_txid_list)))

print(f"{len(smk_missing_txids)} smk_missing_txids txids")
print(f"{len(decker_missing_txids)} decker_missing_txids txids")

dpow_server_coins = requests.get("http://116.203.120.91:8762/api/info/dpow_server_coins").json()
coins_list = list(set(dpow_server_coins["Third_Party"] + dpow_server_coins["Main"]))

invalid_chain= []
decker_missing_blocktimes = []
decker_missing_txids_not_within_epoch_window = []
decker_missing_txids_within_epoch_window = []
decker_missing_txids_outside_season_window = []
season = "Season_4"
i = 0
for txid in decker_missing_txids:
    i += 1
    url = f"{THIS_SERVER}/api/info/notarisation_txid?txid={txid}"
    tx_info = requests.get(url).json()
    block_time = tx_info["block_time"]
    chain = tx_info["chain"]
    server = tx_info["server"]
    block = tx_info["block_height"]
    decker_missing_blocktimes.append(block_time)
    try:
        assert int(block_time) >= SEASONS_INFO[season]['start_time'] and int(block_time) <= SEASONS_INFO[season]['end_time']
        inside_epochs = False
        valid_epoch = None
        if chain in chain_epochs:
            if server in chain_epochs[chain]:
                for epoch_id in chain_epochs[chain][server]:
                    if int(block_time) >= chain_epochs[chain][server][epoch_id]['start'] and int(block_time) <= chain_epochs[chain][server][epoch_id]['end']:
                        inside_epochs = True
                        valid_epoch = epoch_id
                        valid_server = server
        if inside_epochs == True:
            #print(f"[decker_missing_txids] block {block} block_time {block_time} is inside {chain} {valid_server} {valid_epoch} epoch")
            #print(url)
            #print(f"decker_missing_txids, {block}, {block_time}, {chain}, {valid_server}, {valid_epoch}, {url} ")
            decker_missing_txids_within_epoch_window.append(url)
        else:
            # print(f"[decker_missing_txids] block_time {block_time} is not inside {chain} epochs")
            decker_missing_txids_not_within_epoch_window.append(url)
    except Exception as e:
        print(e)
        print(f'[decker_missing_txids] [{i}/{len(decker_missing_txids)}] {block_time} {tx_info["chain"]} {url} {tx_info["score_value"]}')
        #print(f"[decker_missing_txids] block_time {block_time} is outside season window ({SEASONS_INFO[season]['start_time']} to {SEASONS_INFO[season]['end_time']})")
        decker_missing_txids_outside_season_window.append(url)
        row = notarised_row()
        row.chain = tx_info["chain"]
        row.block_height = tx_info["block_height"]
        row.block_time = tx_info["block_time"]
        row.block_datetime = tx_info["block_datetime"]
        row.block_hash = tx_info["block_hash"]
        row.notaries = tx_info["notaries"]
        row.notary_addresses = tx_info["notary_addresses"]
        row.ac_ntx_blockhash = tx_info["ac_ntx_blockhash"]
        row.ac_ntx_height = tx_info["ac_ntx_height"]
        row.txid = tx_info["txid"]
        row.opret = tx_info["opret"]
        row.season = tx_info["season"]
        row.server = tx_info["server"]
        row.epoch = tx_info["epoch"]
        
        row.score_value = 0
        row.scored = False
        row.btc_validated = "N/A"
        row.update()
    try:
        assert chain in coins_list
    except:
        invalid_chain.append(txid)
        print(f">>> Invalid chainf or s4: {url}")

decker_missing_blocktimes
print(f"{min(decker_missing_blocktimes)} min decker_missing_blocktimes")
print(f"{max(decker_missing_blocktimes)} max decker_missing_blocktimes")

print(f"{len(decker_missing_txids_within_epoch_window)} decker_missing_txids_within_epoch_window")

print(f"{len(decker_missing_txids_not_within_epoch_window)} decker_missing_txids_not_within_epoch_window")
print(f"{len(decker_missing_txids_outside_season_window)} decker_missing_txids_outside_season_window ")
print(f"{len(invalid_chain)} invalid_chain ")

if len(decker_missing_txids_within_epoch_window) > 0:
    print(f"{len(decker_missing_txids_within_epoch_window)} decker_missing_txids_within_epoch_window to verify")
    with open("decker_missing_txids_within_epoch_window.json", "w") as f:
        json.dump(list(decker_missing_txids_within_epoch_window), f)

if len(decker_missing_txids_not_within_epoch_window) > 0:
    print(f"{len(decker_missing_txids_not_within_epoch_window)} decker_missing_txids_not_within_epoch_window to verify")
    with open("decker_missing_txids_not_within_epoch_window.json", "w") as f:
        json.dump(list(decker_missing_txids_not_within_epoch_window), f)

if len(decker_missing_txids_outside_season_window) > 0:
    print(f"{len(decker_missing_txids_outside_season_window)} decker_missing_txids_outside_season_window to verify")
    with open("decker_missing_txids_outside_season_window.json", "w") as f:
        json.dump(list(decker_missing_txids_outside_season_window), f)

input()

i =0
smk_missing_txids_not_within_epoch_window = []
smk_missing_txids_within_epoch_window = []
smk_missing_txids_outside_season_window = []
missing_chains = []
for txid in smk_missing_txids:
    i += 1
    url = f"{THIS_SERVER}/api/info/notarisation_txid?txid={txid}"
    tx_info = requests.get(url).json()
    block_datetime = tx_info["block_datetime"]
    block_time = tx_info["block_time"]
    chain = tx_info["chain"]
    epoch = tx_info["epoch"]
    server = tx_info["server"]
    block = tx_info["block_height"]
    try:
        assert int(block_time) >= SEASONS_INFO[season]['start_time'] and int(block_time) <= SEASONS_INFO[season]['end_time']
        inside_epochs = False
        valid_epoch = None
        if chain in chain_epochs:
            if server in chain_epochs[chain]:
                for epoch_id in chain_epochs[chain][server]:
                    if int(block_time) >= chain_epochs[chain][server][epoch_id]['start'] and int(block_time) <= chain_epochs[chain][server][epoch_id]['end']:
                        inside_epochs = True
                        valid_epoch = epoch_id
                        valid_server = server

        if inside_epochs == True:
            #print(f"[smk_missing_txids] block_time {block_time} is inside {chain} {valid_server} {valid_epoch} epoch")  
            print(url)
            smk_missing_txids_within_epoch_window.append(txid)  
        else:
            #print(f"[smk_missing_txids]  block_time {block_time} is not inside {chain} epochs")
            
            print(f"smk_missing_txids, {block}, {block_time}, {chain}, {server}, {epoch}, {txid} ")
            smk_missing_txids_not_within_epoch_window.append(txid)
    except Exception as e:    
        print(e)
        print(f'[smk_missing_txids] [{i}/{len(smk_missing_txids)}] {block_time} {tx_info["chain"]} {url} {tx_info["score_value"]}')
        # print(f"[smk_missing_txids] block_time {block_time} is outside season window ({SEASONS_INFO[season]['start_time']} to {SEASONS_INFO[season]['end_time']})")
        smk_missing_txids_outside_season_window.append(url)

        row = notarised_row()
        row.chain = tx_info["chain"]
        row.block_height = tx_info["block_height"]
        row.block_time = tx_info["block_time"]
        row.block_datetime = tx_info["block_datetime"]
        row.block_hash = tx_info["block_hash"]
        row.notaries = tx_info["notaries"]
        row.notary_addresses = tx_info["notary_addresses"]
        row.ac_ntx_blockhash = tx_info["ac_ntx_blockhash"]
        row.ac_ntx_height = tx_info["ac_ntx_height"]
        row.txid = tx_info["txid"]
        row.opret = tx_info["opret"]
        row.season = tx_info["season"]
        row.server = tx_info["server"]
        row.epoch = tx_info["epoch"]
        row.score_value = float(tx_info["score_value"])
        row.scored = tx_info["scored"]
        row.btc_validated = tx_info["btc_validated"]

        row.update()
        missing_chains.append(row.chain)

print(f"{len(smk_missing_txids_not_within_epoch_window)} smk_missing_txids_not_within_epoch_window")
print(f"{len(smk_missing_txids_within_epoch_window)} smk_missing_txids_within_epoch_window")
print(f"{len(smk_missing_txids_outside_season_window)} smk_missing_txids_outside_season_window")

if len(smk_missing_txids_not_within_epoch_window) > 0:
    print(f"{len(smk_missing_txids_not_within_epoch_window)} smk_missing_txids_not_within_epoch_window to verify")
    with open("smk_missing_txids_not_within_epoch_window.json", "w") as f:
        json.dump(list(smk_missing_txids_not_within_epoch_window), f)

if len(smk_missing_txids_within_epoch_window) > 0:
    print(f"{len(smk_missing_txids_within_epoch_window)} smk_missing_txids_within_epoch_window to verify")
    with open("smk_missing_txids_within_epoch_window.json", "w") as f:
        json.dump(list(smk_missing_txids_within_epoch_window), f)

if len(smk_missing_txids_outside_season_window) > 0:
    print(f"{len(smk_missing_txids_outside_season_window)} smk_missing_txids_outside_season_window to verify")
    with open("smk_missing_txids_outside_season_window.json", "w") as f:
        json.dump(list(smk_missing_txids_outside_season_window), f)

def get_chain_epochs_dict(season):
    epochs = get_epochs("Season_4")
    chain_epochs = {}
    for epoch in epochs:
        for chain in epoch["epoch_chains"]:
            if chain not in chain_epochs:
                chain_epochs.update({chain:{}})
            if epoch["server"] not in chain_epochs[chain]:
                chain_epochs[chain].update({epoch["server"]:{}}) 
            if epoch["epoch"] not in chain_epochs[chain][epoch["server"]]:
                chain_epochs[chain][epoch["server"]].update({epoch["epoch"]:{}}) 
            chain_epochs[chain][epoch["server"]][epoch["epoch"]].update({
                "start":epoch["epoch_start"],
                "end":epoch["epoch_end"]
                })
    return chain_epochs


'''
print(f"START: {SEASONS_INFO[season]['start_time']}")
print(f"END: {SEASONS_INFO[season]['end_time']}")

for txid in invalid_block_time:
    url = f"{THIS_SERVER}/api/info/notarisation_txid?txid={txid}"
    tx_info = requests.get(url).json()
        row = notarised_row()
        row.chain = tx_info["chain"]
        row.block_height = tx_info["block_height"]
        row.block_time = tx_info["block_time"]
        row.block_datetime = tx_info["block_datetime"]
        row.block_hash = tx_info["block_hash"]
        row.notaries = tx_info["notaries"]
        row.notary_addresses = tx_info["notary_addresses"]
        row.ac_ntx_blockhash = tx_info["ac_ntx_blockhash"]
        row.ac_ntx_height = tx_info["ac_ntx_height"]
        row.txid = tx_info["txid"]
        row.opret = tx_info["opret"]
        row.season = tx_info["season"]
        row.server = tx_info["server"]
        row.epoch = tx_info["epoch"]
        
        row.score_value = 0
        row.scored = False
        row.btc_validated = "N/A"
        row.update()

'''

CONN.close()

'''
update_KMD_notarisations(decker_KMD_block_list)
ntx_summary, chain_totals = get_notarisation_data(season)
chain_ntx_counts, notary_season_pct = get_notary_season_count_pct(season)

for notary in ntx_summary:

    for summary_season in ntx_summary[notary]["seasons"]:
        logger.info(f"Getting season summary for {notary} {summary_season}")


        if notary in KNOWN_NOTARIES:

            season_ntx_count_row = notarised_count_season_row()
            season_ntx_count_row.notary = notary
            season_ntx_count_row.season = summary_season
            servers = ntx_summary[notary]["seasons"][summary_season]['servers']

            if "KMD" in servers:
                season_ntx_count_row.btc_count = servers['KMD']['server_ntx_count']

            elif "LTC" in servers:
                season_ntx_count_row.btc_count = servers['LTC']['server_ntx_count']

            else: 
                season_ntx_count_row.btc_count = 0

            if 'Main' in servers:
                season_ntx_count_row.antara_count = servers['Main']['server_ntx_count']

            else:
                season_ntx_count_row.antara_count = 0

            if 'Third_Party' in servers:
                season_ntx_count_row.third_party_count = servers['Third_Party']['server_ntx_count']

            else:
                season_ntx_count_row.third_party_count = 0

            season_ntx_count_row.other_count = 0
            season_ntx_count_row.total_ntx_count = ntx_summary[notary]["seasons"][summary_season]['season_ntx_count']

            season_ntx_count_row.season_score = ntx_summary[notary]["seasons"][summary_season]["season_score"]
            season_ntx_count_row.chain_ntx_counts = json.dumps(ntx_summary[notary])
            season_ntx_count_row.chain_ntx_pct = json.dumps(notary_season_pct)
            season_ntx_count_row.time_stamp = time.time()
            season_ntx_count_row.update()'''