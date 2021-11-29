from lib_const import *
from lib_table_select import *

def lil_endian(hex_str):
    return ''.join([hex_str[i:i+2] for i in range(0, len(hex_str), 2)][::-1])

def safe_div(x,y):
    if y==0: return 0
    return float(x/y)

def handle_dual_server_chains(chain, server):
    if chain == "GLEEC" and server == "Third_Party":
        return "GLEEC-OLD"
    return chain

def handle_translate_chains(chain):
    if chain in TRANSLATE_COINS:
        return TRANSLATE_COINS[chain]
    return chain

def validate_epoch_chains(epoch_chains, season):
    if len(epoch_chains) == 0:
        return False
    for chain in epoch_chains:
        if season in DPOW_EXCLUDED_CHAINS:
            if chain in DPOW_EXCLUDED_CHAINS[season]:
                logger.warning(f"{chain} in DPOW_EXCLUDED_CHAINS[{season}]")
                return False
    return True

def validate_season_server_epoch(season, server, epoch, notary_addresses, block_time, chain, txid, notaries):
    if season in DPOW_EXCLUDED_CHAINS:
        if chain in DPOW_EXCLUDED_CHAINS[season]:
            season = "Unofficial"
            server = "Unofficial"
            epoch = "Unofficial"
    season, server = get_season_from_addresses(notary_addresses, block_time, "KMD", chain, txid, notaries)
    epoch = get_chain_epoch_at(season, server, chain, block_time)
    return season, server, epoch

def handle_translate_chains(chain):
    if chain in TRANSLATE_COINS:
        return TRANSLATE_COINS[chain]
    return chain

def get_name_from_address(address):
    if address in KNOWN_ADDRESSES:
        return KNOWN_ADDRESSES[address]
    return address


def get_season_from_block(block):
    if not isinstance(block, int):
        block = int(block)
    for season in SEASONS_INFO:
        if season.find("Testnet") == -1:
            end_block = SEASONS_INFO[season]['end_block']
            if block >= SEASONS_INFO[season]['start_block'] and block <= end_block:
                return season
    return None

def has_season_started(season):
    now = time.time()
    if season in SEASONS_INFO:
        if SEASONS_INFO[season]["start_time"] < now:
            return True
    return False


def get_chain_epoch_at(season, server, chain, timestamp):
    if season in DPOW_EXCLUDED_CHAINS: 
        if chain not in DPOW_EXCLUDED_CHAINS[season]:
            if chain in ["KMD", "BTC", "LTC"]:
                if int(timestamp) >= SEASONS_INFO[season]["start_time"] and int(timestamp) <= SEASONS_INFO[season]["end_time"]:
                    return f"{chain}"

            epochs = get_epochs(season, server)
            for epoch in epochs:
                if chain in epoch["epoch_chains"]:
                    if int(timestamp) >= epoch["epoch_start"] and int(timestamp) <= epoch["epoch_end"]:
                        return epoch["epoch"]

    return "Unofficial"


def get_chain_epoch_score_at(season, server, chain, timestamp):
    if season in DPOW_EXCLUDED_CHAINS: 
        if chain not in DPOW_EXCLUDED_CHAINS[season]:
            if chain in ["BTC", "LTC"]:
                return 0
            if chain in ["KMD"]:
                if int(timestamp) >= SEASONS_INFO[season]["start_time"] and int(timestamp) <= SEASONS_INFO[season]["end_time"]:
                    return 0.0325

            epochs = get_epochs(season, server)
            for epoch in epochs:
                if chain in epoch["epoch_chains"]:
                    if int(timestamp) >= epoch["epoch_start"] and int(timestamp) <= epoch["epoch_end"]:
                        return round(epoch["score_per_ntx"], 8)
    return 0


def get_server_active_scoring_dpow_chains_at_time(season, server, timestamp):
    url = f"{THIS_SERVER}/api/table/notarised_tenure/?server={server}&season={season}"
    # logger.info(url)
    r = requests.get(url)
    tenure = r.json()["results"]
    server_active_scoring_dpow_chains = []
    count = 0
    for item in tenure:
        if timestamp >= item["official_start_block_time"]:
            if timestamp <= item["official_end_block_time"]:
                if item["chain"] not in ["BTC", "LTC", "KMD"] and item["chain"] not in DPOW_EXCLUDED_CHAINS[season]:
                    server_active_scoring_dpow_chains.append(item["chain"])

    return server_active_scoring_dpow_chains, len(list(set(server_active_scoring_dpow_chains)))


def get_season(time_stamp=None):
    # detect & convert js timestamps
    if not time_stamp:
        time_stamp = int(time.time())
    time_stamp = int(time_stamp)
    if round((time_stamp/1000)/time.time()) == 1:
        time_stamp = time_stamp/1000
    for season in SEASONS_INFO:
        if season.find("Testnet") == -1:
            if POSTSEASON:
                if season in SEASONS_INFO:
                    if 'post_season_end_time' in SEASONS_INFO[season]:
                        end_time = SEASONS_INFO[season]['post_season_end_time']
                    else:
                        end_time = SEASONS_INFO[season]['end_time']
                else:
                    end_time = SEASONS_INFO[season]['end_time']
        if time_stamp >= SEASONS_INFO[season]['start_time'] and time_stamp <= end_time:
            return season
    return "Unofficial"


def get_gleec_ntx_server(txid):
    raw_tx = RPC["KMD"].getrawtransaction(txid,1)
    opret = raw_tx['vout'][1]['scriptPubKey']['asm']
    opret = opret.replace("OP_RETURN ","")
    decoded = requests.get(f"{THIS_SERVER}/api/tools/decode_opreturn/?OP_RETURN={opret}").json()
    if decoded["notarised_block"] < 1000000:
        return "Main"
    else:
        return "Third_Party"


def get_season_from_addresses(address_list, time_stamp, tx_chain="KMD", chain=None, txid=None, notaries=None):
    if BTC_NTX_ADDR in address_list:
        address_list.remove(BTC_NTX_ADDR)
    if chain == "BTC":
        tx_chain = "BTC"
    if chain == "KMD":
        tx_chain = "KMD"
    elif chain == "LTC":
        tx_chain = "LTC"

    seasons = list(NOTARY_ADDRESSES_DICT.keys())[::-1]
    notary_seasons = []
    last_season = None

    for season in seasons:
        if last_season != season:
            notary_seasons = []

        season_notaries = list(NOTARY_ADDRESSES_DICT[season].keys())
        for notary in season_notaries:
            addr = NOTARY_ADDRESSES_DICT[season][notary][tx_chain]
            if addr in address_list:
                notary_seasons.append(season)

        if len(notary_seasons) == 13:
            break
        last_season_num = season

    if len(notary_seasons) == 13 and len(set(notary_seasons)) == 1:
        if chain in ["KMD", "BTC", "LTC"]:
            server = chain

        elif notary_seasons[0].find("_Third_Party") > -1:
            server = "Third_Party"

        else:
            server = "Main"

        ntx_season = notary_seasons[0].replace("_Third_Party", "").replace(".5", "")
        return ntx_season, server

    else:
        return  "Unofficial", "Unofficial"


def get_chain_server(chain, season):
    if chain in ["KMD", "LTC", "BTC"]:
        return chain
    if season == SEASON:
        main_coins = ANTARA_COINS
        third_party_coins = THIRD_PARTY_COINS
    else:
        main_coins = requests.get(f'{THIS_SERVER}/api/info/dpow_server_coins/?season={season}&server=Main').json()["results"]
        third_party_coins = requests.get(f'{THIS_SERVER}/api/info/dpow_server_coins/?season={season}&server=Third_Party').json()["results"]
    if chain in main_coins:
        return "Main"
    elif chain in third_party_coins:
        return "Third_Party"
    else:
        return "Unofficial"

def get_season_notaries(season):
    if season in NOTARY_PUBKEYS:
        notaries = list(NOTARY_PUBKEYS[season].keys())
        notaries.sort()
        return notaries
    return []



''' DEPRECATED
def validate_ltc_ntx_vouts(vouts):
    for vout in vouts:

        if vout["addresses"] is not None:

            if vout["addresses"][0] == LTC_NTX_ADDR and vout["value"] == 98800:
                return True

    return False

def validate_ntx_vouts(vouts):
    for vout in vouts:

        if vout["addresses"] is not None:

            if vout["addresses"][0] == BTC_NTX_ADDR and vout["value"] == 98800:
                return True

    return False

def ts_col_to_season_col(ts_col, season_col, table):
    for season in SEASONS_INFO:
        sql = "UPDATE "+table+" \
               SET "+season_col+"='"+season+"' \
               WHERE "+ts_col+" > "+str(SEASONS_INFO[season]['start_time'])+" \
               AND "+ts_col+" < "+str(SEASONS_INFO[season]['end_time'])+";"
        CURSOR.execute(sql)
        CONN.commit()


def get_nn_btc_tx_parts(txid):
    r = requests.get(f"{OTHER_SERVER}/api/info/nn_btc_txid/?txid={txid}")
    tx_parts_list = r.json()["results"][0]
    
    tx_vins = []
    tx_vouts = []
    for part in tx_parts_list:
        if part["input_index"] != -1:
            tx_vins.append(part)
        if part["output_index"] != -1:
            tx_vouts.append(part)
    return tx_vins, tx_vouts


def get_nn_btc_tx_parts_local(txid):
    r = requests.get(f"{THIS_SERVER}/api/info/nn_btc_txid/?txid={txid}")
    tx_parts_list = r.json()["results"][0]
    
    tx_vins = []
    tx_vouts = []
    for part in tx_parts_list:
        if part["input_index"] != -1:
            tx_vins.append(part)
        if part["output_index"] != -1:
            tx_vouts.append(part)
    return tx_vins, tx_vouts 
'''


def get_notary_from_address(address):
    if address in KNOWN_ADDRESSES:
        return KNOWN_ADDRESSES[address]
    return "unknown"


def get_notary_from_ltc_address(address, season=None, notary=None):
    if address == LTC_NTX_ADDR:
        return "LTC_NTX_ADDR"

    if season in NN_LTC_ADDRESSES_DICT:
        if address in NN_LTC_ADDRESSES_DICT[season]:
            return NN_LTC_ADDRESSES_DICT[season][address]

    seasons = list(SEASONS_INFO.keys())[::-1]

    for s in seasons:
        if s in NN_LTC_ADDRESSES_DICT:
            if address in NN_LTC_ADDRESSES_DICT[s]:
                return NN_LTC_ADDRESSES_DICT[s][address]
    if notary:
        return notary
    else:
        return "non-NN"


def get_notary_from_btc_address(address, season=None, notary=None):
    if address == BTC_NTX_ADDR:
        return "BTC_NTX_ADDR"
    if season in NN_BTC_ADDRESSES_DICT:
        if address in NN_BTC_ADDRESSES_DICT[season]:
            return NN_BTC_ADDRESSES_DICT[season][address]

    seasons = list(SEASONS_INFO.keys())[::-1]

    for s in seasons:
        if s in NN_BTC_ADDRESSES_DICT:
            if address in NN_BTC_ADDRESSES_DICT[s]:
                return NN_BTC_ADDRESSES_DICT[s][address]
    if notary:
        return notary
    else:
        return "non-NN"


# Deprecate in favour of models.get_chain_epoch_score_at()?
# need to move numerators to const.py first...
def get_dpow_score_value(season, server, coin, timestamp):

    score  = 0

    if coin in ["KMD"]:
        if int(timestamp) >= SEASONS_INFO[season]["start_time"] and int(timestamp) <= SEASONS_INFO[season]["end_time"]:
            return 0.0325

        return 0

    if coin in ["BTC", "LTC"]:

        return 0
        
    active_chains, num_coins = get_server_active_scoring_dpow_chains_at_time(season, server, timestamp)
    if coin in active_chains:

        if server == "Main":
            score = 0.8698/num_coins

        elif server == "Third_Party":
            score = 0.0977/num_coins

        elif server == "Testnet":
            score = 0.0977/num_coins


    return round(score, 8)


    
def get_notaries_from_addresses(addresses):
    notaries = []
    if BTC_NTX_ADDR in addresses:
        addresses.remove(BTC_NTX_ADDR)
    if LTC_NTX_ADDR in addresses:
        addresses.remove(LTC_NTX_ADDR)
    if KMD_NTX_ADDR in addresses:
        addresses.remove(KMD_NTX_ADDR)
    for address in addresses:
        if address in KNOWN_ADDRESSES:
            notary = KNOWN_ADDRESSES[address]
            notaries.append(notary)
        else:
            notaries.append(address)
    notaries.sort()
    return notaries


def is_coin_is_dpow_scoring_active(season, server, coin, timestamp):

    r = requests.get(f"{THIS_SERVER}/api/table/notarised_tenure/?chain={coin}")
    tenure = r.json()["results"][0]

    if season in tenure:
        if server in tenure[season]:
            if coin in tenure[season][server]:
                if int(timestamp) >= int(tenure[season][server][coin]["official_start_block_time"]):
                    if int(timestamp) <= int(tenure[season][server][coin]["official_end_block_time"]):
                        return server, True

    return "Unofficial", False

def get_seasons_from_address(addr, chain="KMD"):
    addr_seasons = []
    for season in NOTARY_ADDRESSES_DICT:
        for notary in NOTARY_ADDRESSES_DICT[season]:
            season_addr = NOTARY_ADDRESSES_DICT[season][notary][chain]
            if addr == season_addr:
                addr_seasons.append(season)
    return addr_seasons