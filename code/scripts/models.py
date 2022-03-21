from lib_const import *
from lib_helper import *
from lib_validate import *
from lib_table_select import get_epochs
from lib_table_update import *

class addresses_row():
    def __init__(self, season='', server='', notary='',
                 notary_id='', address='', pubkey='', chain=''):
        self.season = season
        self.server = server
        self.notary = notary
        self.notary_id = notary_id
        self.address = address
        self.pubkey = pubkey
        self.chain = chain

    def validated(self):
        for i in [self.season, self.server, self.notary,
                  self.notary_id, self.address, self.pubkey,
                  self.chain]:
            if i == '':
                return False
        return True

    def update(self):
        self.server, self.chain = handle_dual_server_chains(self.server, self.chain)
        row_data = (self.season, self.server, self.notary,
                    self.notary_id, self.address, self.pubkey,
                    self.chain)
        if self.validated():
            update_addresses_row(row_data)
            logger.info(f"Updated [addresses] | {self.season} | \
                {self.server} | {self.notary} | {self.address} | \
                {self.chain}")
        else:
            logger.warning(f"[addresses] Row data invalid!")
            logger.warning(f"{row_data}")

    def delete(self):
        delete_addresses_row(self.season, self.chain, self.address)
        logger.info(f"Deleted [addresses] row {self.season} | \
                      {self.chain} | {self.address}")


class balance_row():
    def __init__(self, season='', server='', notary='', address='',
                 chain='', balance=0, update_time=0):
        self.notary = notary
        self.chain = chain
        self.balance = balance
        self.address = address
        self.season = season
        self.server = server
        self.update_time = update_time

    def validated(self):
        for i in [self.season, self.server, self.notary,
                  self.address, self.chain, self.update_time]:
            if i == '':
                return False
        return True

    def update(self):
        self.update_time = int(time.time())
        self.server, self.chain = handle_dual_server_chains(
                                    self.server, self.chain, self.address
                                )
        self.balance = get_balance(self.chain, self.pubkey, self.address, self.server)
        row_data = (self.season, self.server, self.notary,
            self.address, self.chain, self.balance,
            self.update_time)

        if self.validated():
            logger.info(f"Updating [balance] {self.season} | {self.server} | {self.notary} | {self.chain} | {self.balance} | {self.address} | {self.update_time}")
            update_balances_row(row_data)
        else:
            logger.warning(f"[balance] Row data invalid!")
            logger.warning(f"{row_data}")

    def delete(self):
        delete_balances_row(self.chain, self.address, self.season)
        logger.info(f"Deleted balance row {self.season} | {self.chain} | \
                      {self.address}")

   
class coins_row():
    def __init__(self, chain='', coins_info='',
     electrums='', electrums_ssl='', explorers='',
     dpow='', dpow_tenure=dict, dpow_active='', mm2_compatible=''):
        self.chain = chain
        self.coins_info = coins_info
        self.electrums = electrums
        self.electrums_ssl = electrums_ssl
        self.explorers = explorers
        self.dpow = dpow
        self.dpow_tenure = dpow_tenure
        self.dpow_active = dpow_active
        self.mm2_compatible = mm2_compatible

    def validated(self):
        return True

    def update(self):
        self.chain = handle_translate_chains(self.chain)
        row_data = (self.chain, self.coins_info, self.electrums,
            self.electrums_ssl, self.explorers, self.dpow,
            self.dpow_tenure, self.dpow_active, self.mm2_compatible)
        if self.validated():
            logger.info(f"Updating [coins] {self.chain} ")
            update_coins_row(row_data)
        else:
            logger.warning(f"[coins] Row data invalid!")
            logger.warning(f"{row_data}")

    def delete(self):
        CURSOR.execute(f"DELETE FROM coins WHERE chain = '{self.chain}';")
        CONN.commit()
        logger.info(f"Deleted {self.chain} from [coins] ")
  

# TODO: DEPRECATE in S5, no more BTC
class tx_row():
    def __init__(self, txid='', block_hash='', block_height='',
                 block_time='', block_datetime='', address='',
                 notary='non-NN', season='', category='Other',
                 input_index=-1, input_sats=-1, output_index=-1,
                 output_sats=-1, fees=-1, num_inputs=0,
                 num_outputs=0):
        self.txid = txid
        self.block_hash = block_hash
        self.block_height = block_height
        self.block_time = block_time
        self.block_datetime = block_datetime
        self.address = address
        self.notary = notary
        self.season = season
        self.category = category
        self.input_index = input_index
        self.input_sats = input_sats
        self.output_index = output_index
        self.output_sats = output_sats
        self.fees = fees
        self.num_inputs = num_inputs
        self.num_outputs = num_outputs

    def validated(self):
        for i in [self.txid, self.block_hash, self.block_height,
                  self.block_time, self.block_datetime, self.address,
                  self.season, self.block_hash, self.txid, self.block_hash,
                  self.input_index, self.input_sats, self.output_index, 
                  self.output_sats]:
            if i == '':
                return False
        return True

    def update(self):
        if self.category == "SPAM":
            self.input_index = 0
            self.input_sats = 0
            self.output_index = 0
            self.output_sats = 0

        if self.category == "Split":
            self.input_index = -99
            self.input_sats = -99
            self.output_index = -99
            self.output_sats = -99

        if self.address == BTC_NTX_ADDR:
            self.notary = "BTC_NTX_ADDR"
            
        if self.notary.find("linked") != -1:
            self.notary = get_name_from_address(self.address)

        self.season = get_season(self.block_time)

        row_data = (self.txid, self.block_hash, self.block_height,
                    self.block_time, self.block_datetime, self.address,
                    self.notary, self.season, self.category, self.input_index,
                    self.input_sats, self.output_index, self.output_sats,
                    self.fees, self.num_inputs, self.num_outputs)
        if self.validated():
            msg = f"[btc_tx] Adding {self.season} {self.txid} \
                    {self.category} {self.notary}"
            if self.input_index != -1:
                logger.info(f"{msg} VIN {self.input_index}")
            elif self.output_index != -1:
                logger.info(f"{msg} VOUT {self.output_index}")
            else:
                logger.info(msg)
            update_nn_btc_tx_row(row_data)
        else:
            url = f"{OTHER_SERVER}/api/info/nn_btc_txid/?txid={self.txid}"
            logger.warning("[btc_tx] Row data invalid!")
            logger.warning(url)
            logger.warning(row_data)

    def delete(self):
        delete_nn_btc_tx_transaction(self.txid)


class nn_social_row():
    def __init__(self, notary='', twitter='', youtube='', email='',
                 discord='', telegram='', github='', keybase='', website='',
                 icon='', season=''):
        self.notary = notary
        self.discord = discord
        self.email = email
        self.github = github
        self.icon = icon
        self.keybase = keybase
        self.telegram = telegram
        self.twitter = twitter
        self.youtube = youtube
        self.website = website
        self.season = season

    def validated(self):
        return True

    def update(self):
        row_data = (self.notary, self.twitter, self.youtube,
                    self.email, self.discord, self.telegram, self.github,
                    self.keybase, self.website, self.icon, self.season)
        if self.validated():
            logger.info(f"Updating NN social {self.season} | {self.notary}")
            update_nn_social_row(row_data)
        else:
            logger.warning(f"[nn_social] Row data invalid!")
            logger.warning(f"{row_data}")

    def delete(self):
        pass


class coin_social_row():
    def __init__(self='', chain='', discord='', email='', explorers=list,
                 github='', icon='', linkedin='', mining_pools=list,
                 reddit='', telegram='', twitter='', youtube='',
                 website='', season=''):
        self.chain = chain
        self.discord = discord
        self.email = email
        self.explorers = explorers
        self.github = github
        self.icon = icon
        self.linkedin = linkedin
        self.mining_pools = mining_pools
        self.reddit = reddit
        self.telegram = telegram
        self.twitter = twitter
        self.youtube = youtube
        self.website = website
        self.season = season

    def validated(self):
        return True

    def update(self):
        self.chain = handle_translate_chains(self.chain)

        row_data = (self.chain, self.discord, self.email, self.explorers,
                    self.github, self.icon, self.linkedin, self.mining_pools,
                    self.reddit, self.telegram, self.twitter, self.youtube,
                    self.website, self.season)
        if self.validated():
            update_coin_social_row(row_data)
            logger.info(f"Updated [coin_social] {self.season} | {self.chain}")
        else:
            logger.warning(f"[coin_social] Row data invalid!")
            logger.warning(f"{row_data}")

    def delete(self):
        pass

        
class funding_row():
    def __init__(self, chain='', txid='', vout='', amount='',
            block_hash='', block_height='', block_time='',
            category='', fee='', address='', notary='', season=''):
        self.chain = chain
        self.txid = txid
        self.vout = vout
        self.amount = amount
        self.block_hash = block_hash
        self.block_height = block_height
        self.block_time = block_time
        self.category = category
        self.fee = fee
        self.address = address
        self.notary = notary
        self.season = season

    def validated(self):
        return True

    def update(self):
        self.chain = handle_translate_chains(self.chain)
        row_data = (self.chain, self.txid, self.vout, self.amount,
                    self.block_hash, self.block_height, self.block_time,
                    self.category, self.fee, self.address, self.notary,
                    self.season)
        if self.validated():
            logger.info(f"Updating [funding] {self.chain} | {self.notary} ")
            update_funding_row(row_data)
        else:
            logger.warning(f"[funding] Row data invalid!")
            logger.warning(f"{row_data}")

    def delete(self):
        sql = f"DELETE FROM funding_transactions WHERE chain = '{self.chain}';"
        CURSOR.execute(sql)
        CONN.commit()


class notarised_row():
    def __init__(self, chain='', block_height='', 
                 block_time='', block_datetime='', block_hash='', 
                 notaries=list, notary_addresses=list, ac_ntx_blockhash='',
                 ac_ntx_height='', txid='', opret='', season='', server='',
                 scored=True, score_value=0, epoch=''):
        self.chain = chain
        self.block_height = block_height
        self.block_time = block_time
        self.block_datetime = block_datetime
        self.block_hash = block_hash
        self.notaries = notaries
        self.notary_addresses = notary_addresses
        self.ac_ntx_blockhash = ac_ntx_blockhash
        self.ac_ntx_height = ac_ntx_height
        self.txid = txid
        self.opret = opret
        self.season = season
        self.server = server
        self.epoch = epoch
        self.score_value = score_value
        self.scored = scored

    def validated(self):

        if len(self.chain) > 12:
            return False

        for notary in self.notaries:
            if len(notary) > 20:
                return False

        return True

    def update(self):
        self.server, self.chain = handle_dual_server_chains(
                                    self.server, self.chain,
                                    self.notary_addresses[0]
                                )

        self.season, self.server, self.epoch = validate_season_server_epoch(
            self.season, self.server, self.epoch,
            self.notary_addresses, self.block_time, 
            self.chain, self.txid, self.notaries)

        self.score_value = get_chain_epoch_score_at(
            self.season, self.server, self.chain, int(self.block_time))
        self.scored = get_scored(self.score_value)

        # Sort lists for slightly simpler aggregation
        self.notaries.sort()
        self.notary_addresses.sort()

        row_data = (self.chain, self.block_height, 
                    self.block_time, self.block_datetime, self.block_hash, 
                    self.notaries, self.notary_addresses,
                    self.ac_ntx_blockhash, self.ac_ntx_height, self.txid,
                    self.opret, self.season, self.server, self.scored,
                    self.score_value, self.epoch)

        if self.validated():
            logger.info(f"Updating [notarised] {self.block_datetime} {self.txid} {self.season} {self.server} {self.epoch} | {self.scored} {self.score_value} {self.chain} ")
            update_ntx_row(row_data)
        else:
            logger.warning(f"[notarised] row invalid {self.block_datetime} {self.txid} {self.season} {self.server} {self.epoch} | {self.scored} {self.score_value} {self.chain}")
            logger.warning(f"{row_data}")

    def delete(self):
        CURSOR.execute(f"DELETE FROM notarised WHERE txid = '{self.txid}';")
        CONN.commit()



class notarised_chain_daily_row():
    def __init__(self, season='', server='', chain='',
                 ntx_count='', notarised_date=''):
        self.season = season
        self.server = server
        self.chain = chain
        self.ntx_count = ntx_count
        self.notarised_date = notarised_date

    def validated(self):
        return True

    def update(self):
        self.server, self.chain = handle_dual_server_chains(self.server, self.chain)
        row_data = (self.season, self.server, self.chain,
                    self.ntx_count, self.notarised_date)
        if self.validated():
            logger.info(f"Updating [notarised_chain_daily] {self.chain} {self.notarised_date}")
            update_daily_notarised_chain_row(row_data)
        else:
            logger.warning(f"[notarised_chain_daily_row] Row data invalid!")
            logger.warning(f"{row_data}")

    def delete(self):
        sql = f"DELETE FROM notarised_chain_daily \
                WHERE chain = '{self.chain}' \
                AND notarised_date = '{self.notarised_date}';"
        CURSOR.execute(sql)
        CONN.commit()


class notarised_count_daily_row():
    def __init__(self, notary='', btc_count='', antara_count='', 
        third_party_count='', other_count='', 
        total_ntx_count='', chain_ntx_counts='', 
        chain_ntx_pct='', time_stamp=int(time.time()),
        season='', notarised_date=''):
        self.notary = notary
        self.btc_count = btc_count
        self.antara_count = antara_count
        self.third_party_count = third_party_count
        self.other_count = other_count
        self.total_ntx_count = total_ntx_count
        self.chain_ntx_counts = chain_ntx_counts
        self.chain_ntx_pct = chain_ntx_pct
        self.time_stamp = time_stamp
        self.season = season
        self.notarised_date = notarised_date

    def validated(self):
        return True

    def update(self):
        row_data = (self.notary, self.btc_count, self.antara_count,
                    self.third_party_count, self.other_count, 
                    self.total_ntx_count, self.chain_ntx_counts, 
                    self.chain_ntx_pct, self.time_stamp, self.season,
                    self.notarised_date)
        if self.validated():
            logger.info(f"Updating [notarised_count_daily] {self.notarised_date} {self.notary}")
            update_daily_notarised_count_row(row_data)
        else:
            logger.warning(f"[notarised_count_daily_row] Row data invalid!")
            logger.warning(f"{row_data}")

    def delete(self):
        sql = f"DELETE FROM notarised_count_daily \
                WHERE notary = '{self.notary}' \
                AND notarised_date = '{self.notarised_date}';"
        CURSOR.execute(sql)
        CONN.commit()

       
class notarised_count_season_row():
    def __init__(self, notary='', btc_count='', antara_count='', 
        third_party_count='', other_count='', 
        total_ntx_count='', chain_ntx_counts='', season_score='', 
        chain_ntx_pct='', time_stamp=int(time.time()),
        season=''):
        self.notary = notary
        self.btc_count = btc_count
        self.antara_count = antara_count
        self.third_party_count = third_party_count
        self.other_count = other_count
        self.total_ntx_count = total_ntx_count
        self.chain_ntx_counts = chain_ntx_counts
        self.season_score = season_score
        self.chain_ntx_pct = chain_ntx_pct
        self.time_stamp = time_stamp
        self.season = season

    def validated(self):
        return True

    def update(self):
        row_data = (self.notary, self.btc_count, self.antara_count, 
                    self.third_party_count, self.other_count, 
                    self.total_ntx_count, self.chain_ntx_counts,
                    self.season_score, self.chain_ntx_pct, self.time_stamp,
                    self.season)
        if self.validated():
            logger.info(f"Updating [notarised_count_season] {self.notary} {self.season} {self.season_score}")
            update_season_notarised_count_row(row_data)
        else:
            logger.warning(f"[notarised_count_season] Row data invalid!")
            logger.warning(f"{row_data}")

    def delete(self):
        sql = f"DELETE FROM notarised_count_season \
                WHERE notary = '{self.notary}' \
                AND season = '{self.season}';"
        CURSOR.execute(sql)
        CONN.commit()

       
class notarised_chain_season_row():
    def __init__(self, chain='', ntx_count='', block_height='',
                 kmd_ntx_blockhash='', kmd_ntx_txid='', kmd_ntx_blocktime='',
                 opret='', ac_ntx_blockhash='', ac_ntx_height='',
                 ac_block_height='', ntx_lag='', season='', server=''):
        self.chain = chain
        self.ntx_count = ntx_count
        self.block_height = block_height
        self.kmd_ntx_blockhash = kmd_ntx_blockhash
        self.kmd_ntx_txid = kmd_ntx_txid
        self.kmd_ntx_blocktime = kmd_ntx_blocktime
        self.opret = opret
        self.ac_ntx_blockhash = ac_ntx_blockhash
        self.ac_ntx_height = ac_ntx_height
        self.ac_block_height = ac_block_height
        self.ntx_lag = ntx_lag
        self.season = season
        self.server = server

    def validated(self):
        return True

    def update(self):
        self.server, self.chain = handle_dual_server_chains(self.server, self.chain)
        row_data = (self.chain, self.ntx_count, self.block_height,
            self.kmd_ntx_blockhash, self.kmd_ntx_txid, self.kmd_ntx_blocktime,
            self.opret, self.ac_ntx_blockhash, self.ac_ntx_height,
            self.ac_block_height, self.ntx_lag, self.season, self.server)
        if self.validated():
            msg = f"{self.chain} {self.season} {self.server}"
            logger.info(f"Updating [notarised_chain_season] {msg}")
            update_season_notarised_chain_row(row_data)
        else:
            logger.warning(f"[notarised_chain_season] Row data invalid!")
            logger.warning(f"{row_data}")

    def delete(self):
        sql = f"DELETE FROM notarised_chain_season \
                WHERE chain = '{self.chain}' \
                AND season = '{self.season}';"
        CURSOR.execute(sql)
        CONN.commit()

      
class last_notarised_row():
    def __init__(self, notary='', chain='', txid='', block_height='', \
            block_time='', season='', server=''):
        self.notary = notary
        self.chain = chain
        self.txid = txid
        self.block_height = block_height
        self.block_time = block_time
        self.season = season
        self.server = server

    def validated(self):
        for i in [self.notary, self.chain, self.txid, self.block_height, \
            self.block_time, self.season, self.server]:
            if i == "":
                return False
        return True

    def update(self):
        self.server, self.chain = handle_dual_server_chains(self.server, self.chain)
        row_data = (self.notary, self.chain, self.txid, self.block_height,
            self.block_time, self.season, self.server)
        if self.validated():
            logger.info(f"[last_notarised] Updating {self.season} {self.server} {self.chain} {self.block_height} {self.notary}")
            update_last_ntx_row(row_data)
        else:
            logger.warning(f"[last_notarised] Row data invalid!")
            logger.warning(f"{row_data}")

    def delete(self):
        logger.warning(f"[last_notarised_row] DELETING {self.season} \
            {self.server} {self.notary} {self.chain}")
        sql = f"DELETE FROM last_notarised \
                WHERE notary = '{self.notary}' \
                AND season = '{self.season}' \
                AND server = '{self.server}' \
                AND chain = '{self.chain}';"
        CURSOR.execute(sql)
        CONN.commit()


class mined_row():
    def __init__(self, block_height='', block_time='', block_datetime='', 
             value='', address='', name='', txid='', diff=0, season=''):
        self.block_height = block_height
        self.block_time = block_time
        self.block_datetime = block_datetime
        self.value = value
        self.address = address
        self.name = name
        self.txid = txid
        self.diff = diff
        self.season = season

    def validated(self):
        for item in [self.address, self.name, self.season]:
            if item == '':
                logger.warning(f"No value for {item}!")
                return False

        if self.name in KNOWN_NOTARIES:
            if self.name not in NOTARY_ADDRESSES_DICT[self.season][self.name]["KMD"]:
                for season in SEASONS_INFO:
                    if self.name in NOTARY_ADDRESSES_DICT[season]:
                        if self.address in NOTARY_ADDRESSES_DICT[season][self.name]["KMD"]:
                            self.season = season
                            return True

        return True

    def update(self):
        self.season = get_season_from_block(self.block_height)
        self.name = get_name_from_address(self.address)
        row_data = (self.block_height, self.block_time, self.block_datetime, 
            self.value, self.address, self.name, self.txid, self.diff, self.season)

        if self.validated():
            update_mined_row(row_data)
            logger.info(f"Updated [mined] {row_data}")

        else:
            logger.warning(f"[mined] Row data invalid!")
            logger.warning(f"{row_data}")


    def delete(self):
        CURSOR.execute(f"DELETE FROM mined WHERE name = '{self.name}';")
        CONN.commit()
        
    def delete_address(self):
        CURSOR.execute(f"DELETE FROM mined WHERE address = '{self.address}';")
        CONN.commit()
        
    def delete_name(self):
        CURSOR.execute(f"DELETE FROM mined WHERE name = '{self.name}';")
        CONN.commit()


class season_mined_count_row():
    def __init__(self, name='', season='', address='', blocks_mined='',
                 sum_value_mined='', max_value_mined='', max_value_txid='',
                 last_mined_blocktime='', last_mined_block='', 
                 time_stamp=int(time.time())):
        self.name = name
        self.season = season
        self.address = address
        self.blocks_mined = blocks_mined
        self.sum_value_mined = sum_value_mined
        self.max_value_mined = max_value_mined
        self.max_value_txid = max_value_txid
        self.last_mined_blocktime = last_mined_blocktime
        self.last_mined_block = last_mined_block
        self.time_stamp = time_stamp

    def validated(self):
        for item in [self.address, self.name, self.season]:
            if item == '':
                logger.warning(f"No value for {item}!")
                return False
        if self.season.find("Testnet") != -1:
            logger.warning(f"Ignoring testnet")
            return False
        if self.name in NOTARY_PUBKEYS[self.season]:
            if self.address != NOTARY_ADDRESSES_DICT[self.season][self.name]["KMD"]:
                logger.warning(f"{self.address} not in NOTARY_ADDRESSES_DICT")
                return False
        return True

    def update(self):
        self.name = get_name_from_address(self.address)
        row_data = (self.name, self.season, self.address, self.blocks_mined, 
            self.sum_value_mined, self.max_value_mined, self.max_value_txid,
            self.last_mined_blocktime, self.last_mined_block, self.time_stamp) 
        if self.validated():
            update_season_mined_count_row(row_data)
            logger.info(f"[mined_count_season] updated: {row_data}")
        else:
            logger.warning(f"[mined_count_season] Row data invalid!")
            logger.warning(f"{row_data}")

    def delete(self):
        sql = f"DELETE FROM mined_count_season WHERE name = '{self.name}';"
        CURSOR.execute(sql)
        CONN.commit()

    def delete_season(self):
        sql = f"DELETE FROM mined_count_season WHERE season = '{self.season}';"
        CURSOR.execute(sql)
        CONN.commit()

    def delete_address(self):
        sql = f"DELETE FROM mined_count_season \
                WHERE address = '{self.address}';"
        CURSOR.execute()
        CONN.commit()
        logger.info(f"[mined_count_season] {self.address} rows deleted")

    def delete_name(self):
        sql = f"DELETE FROM mined_count_season WHERE name = '{self.name}';"
        CURSOR.execute(sql)
        CONN.commit()


class daily_mined_count_row():
    def __init__(self, notary='', blocks_mined='', sum_value_mined='', \
            mined_date='', time_stamp=int(time.time())):
        self.notary = notary
        self.blocks_mined = blocks_mined
        self.sum_value_mined = sum_value_mined
        self.mined_date = mined_date
        self.time_stamp = time_stamp

    def validated(self):
        return True

    def update(self):
        row_data = (self.notary, self.blocks_mined, self.sum_value_mined, \
                    self.mined_date, self.time_stamp)
        if self.validated():
            logger.info(f"Updating [mined_count_daily] {row_data}")
            update_daily_mined_count_row(row_data)
        else:
            logger.warning(f"[mined_count_daily] Row data invalid!")
            logger.warning(f"{row_data}")

    def delete(self):
        sql = f"DELETE FROM mined_count_daily WHERE notary = '{self.notary}';"
        CURSOR.execute(sql)
        CONN.commit()


class ltc_tx_row():
    def __init__(self, txid='', block_hash='', block_height='',
                 block_time='', block_datetime='', address='',
                 notary='non-NN', season='', category='Other',
                 input_index=-1, input_sats=-1, output_index=-1,
                 output_sats=-1, fees=-1, num_inputs=0,
                 num_outputs=0):
        self.txid = txid
        self.block_hash = block_hash
        self.block_height = block_height
        self.block_time = block_time
        self.block_datetime = block_datetime
        self.address = address
        self.notary = notary
        self.season = season
        self.category = category
        self.input_index = input_index
        self.input_sats = input_sats
        self.output_index = output_index
        self.output_sats = output_sats
        self.fees = fees
        self.num_inputs = num_inputs
        self.num_outputs = num_outputs


    def validated(self):

        for i in [
            self.txid, self.block_hash, self.block_height,
            self.block_time, self.block_datetime, self.address,
            self.season, self.block_hash, self.txid, self.block_hash
            ]:

            if i == '':
                return False

        return True

    def update(self):
        if self.category == "SPAM":
            self.input_index = 0
            self.input_sats = 0
            self.output_index = 0
            self.output_sats = 0

        if self.category == "Split":
            self.input_index = -99
            self.input_sats = -99
            self.output_index = -99
            self.output_sats = -99

        if self.address == LTC_NTX_ADDR:
            self.notary = "LTC_NTX_ADDR"

        if self.notary.find("linked") != -1:
            self.notary = get_name_from_address(self.address)

        self.season = get_season(self.block_time)

        row_data = (
            self.txid, self.block_hash, self.block_height,
            self.block_time, self.block_datetime, self.address,
            self.notary, self.season, self.category, self.input_index,
            self.input_sats, self.output_index, self.output_sats,
            self.fees, self.num_inputs, self.num_outputs
        )
        if self.validated():
            msg = f"[ltc_tx_row] Adding {self.season} {self.txid} \
                    {self.category} for {self.notary}"
            if self.input_index != -1:
                msg += f"VIN {self.input_index}"
            elif self.output_index != -1:
                msg += f"VOUT {self.output_index}"
            update_nn_ltc_tx_row(row_data)
            logger.info(msg)
        else:
            url = f"{OTHER_SERVER}/api/info/nn_ltc_txid/?txid={self.txid}"
            logger.warning(f"[ltc_tx_row] Row data invalid!")
            logger.warning(url)
            logger.warning(f"{row_data}")


    def delete(self):
        delete_nn_ltc_tx_transaction(self.txid)


class scoring_epoch_row():
    def __init__(self, season='', server='', epoch='',epoch_start=0,
                 epoch_end=0, start_event='', end_event='',
                 epoch_chains=list, score_per_ntx=0):
        self.season = season
        self.server = server
        self.epoch = epoch
        self.epoch_start = epoch_start
        self.epoch_end = epoch_end
        self.start_event = start_event
        self.end_event = end_event
        self.epoch_chains = epoch_chains
        self.score_per_ntx = score_per_ntx

    def validated(self):
        if self.season in EXCLUDED_SEASONS:
            logger.warning(f"{self.season} in EXCLUDED_SEASONS")
            return False
        if self.server in EXCLUDED_SERVERS:
            logger.warning(f"{self.server} in EXCLUDED_SERVERS")
            return False
        epoch_chains_validated = validate_epoch_chains(
                                        self.epoch_chains, self.season)
        return epoch_chains_validated

    def update(self):
        if self.season.find("Testnet") > -1:
            self.server == "Main"
        if len(self.epoch_chains) == 0:
            self.epoch_chains = [None]
        row_data = (self.season, self.server, self.epoch, self.epoch_start, \
                    self.epoch_end, self.start_event, self.end_event, \
                    self.epoch_chains, self.score_per_ntx)
        if self.validated():
            update_scoring_epoch_row(row_data)
            logger.info(f"Updated [scoring_epochs] {self.season} | \
                          {self.server} | {self.epoch} ")
        else:
            logger.warning(f"[scoring_epochs] Row data invalid!")
            logger.warning(f"{row_data}")

    def delete(self, season=None, server=None, epoch=None):
        if not season and not server and not epoch:
            logger.error("Not deleting, need to specify \
                          at least one of epoch, season or server")
        else:
            sql = f"DELETE FROM scoring_epochs"
            conditions = []
            if season:
                conditions.append(f"season = '{season}'")
            if server:
                conditions.append(f"server = '{server}'")
            if epoch:
                conditions.append(f"epoch = '{epoch}'")

            if len(conditions) > 0:
                sql += " WHERE "
                sql += " AND ".join(conditions)    
            sql += ";"

            CURSOR.execute(sql)
            CONN.commit()
            logger.warning(f"Deleted [scoring_epochs] row: {season} {server} {epoch}")


class ntx_tenure_row():
    def __init__(self, chain='', first_ntx_block='', 
            last_ntx_block='', first_ntx_block_time='',
            last_ntx_block_time='',official_start_block_time='',
            official_end_block_time='', unscored_ntx_count='',
            scored_ntx_count='', season='', server=''):
        self.chain = chain
        self.first_ntx_block = first_ntx_block
        self.last_ntx_block = last_ntx_block
        self.first_ntx_block_time = first_ntx_block_time
        self.last_ntx_block_time = last_ntx_block_time
        self.official_start_block_time = official_start_block_time
        self.official_end_block_time = official_end_block_time
        self.unscored_ntx_count = unscored_ntx_count
        self.scored_ntx_count = scored_ntx_count
        self.server = server
        self.season = season

    def validated(self):
        if self.server not in VALID_SERVERS:
            logger.warning(f" [notarised_tenure] Invalid server {server}")
            return False
        if self.season not in ['Season_5', 'Season_5_Testnet', 'Season_4']:
            logger.warning(f"[notarised_tenure] Invalid season {season}")
            return False
        return True

    def update(self):
        # TODO: Validation start / end within season window
        self.server, self.chain = handle_dual_server_chains(self.server, self.chain)

        if self.chain in ["KMD" ,"LTC", "BTC"]:
            self.server = self.chain

        if self.chain in ["LTC", "BTC"]:
            self.unscored_ntx_count = self.unscored_ntx_count \
                                    + self.scored_ntx_count
            self.scored_ntx_count = 0

        row_data = (self.chain, self.first_ntx_block, 
                    self.last_ntx_block, self.first_ntx_block_time,
                    self.last_ntx_block_time, self.official_start_block_time, 
                    self.official_end_block_time, self.unscored_ntx_count, 
                    self.scored_ntx_count, self.season, self.server)

        if self.validated():
            logger.info(f">>> Updating [notarised_tenure] {self.season} {self.server} {self.chain} | {self.scored_ntx_count} scored | {self.unscored_ntx_count} unscored")
            update_notarised_tenure_row(row_data)

        else:
            logger.warning(f"Invalid row [notarised_tenure] {self.chain} \
                             {self.season} | {self.server} | \
                             {self.scored_ntx_count} scored | \
                             {self.unscored_ntx_count} unscored")
            logger.warning(f"{row_data}")

    def delete(self, season=None, server=None, chain=None):
        if not season and not server and not chain:
            logger.error("Not deleting, need to specify at \
                          least one of chain, season or server")
        else:
            sql = f"DELETE FROM notarised_tenure"
            conditions = []
            if season:
                conditions.append(f"season = '{season}'")
            if server:
                conditions.append(f"server = '{server}'")
            if chain:
                conditions.append(f"chain = '{chain}'")

            if len(conditions) > 0:
                sql += " WHERE "
                sql += " AND ".join(conditions)    
            sql += ";"
            logger.warning(f"Deleting [notarised_tenure] row: \
                             {season} {server} {chain}")

            CURSOR.execute(sql)
            CONN.commit()


class vote2021_row():
    def __init__(self, txid='', block_hash='', block_time=0, \
            lock_time=0, block_height=0, votes=0, candidate='', 
            candidate_address='', mined_by='', difficulty='', notes=''):
        self.txid = txid
        self.block_hash = block_hash
        self.block_time = block_time
        self.lock_time = lock_time
        self.block_height = block_height
        self.votes = votes
        self.candidate = candidate
        self.candidate_address = candidate_address
        self.mined_by = mined_by
        self.difficulty = difficulty
        self.notes = notes

    def validated(self):
        for i in [self.block_time, self.lock_time, self.block_time,
                  self.votes]:
            if i in [0, None]:
                return False

        for i in [self.txid, self.block_hash, self.candidate,
                  self.candidate_address]:
            if i in ['', None]:
                return False

        if self.candidate_address not in VOTE2021_ADDRESSES_DICT:
            return False

        return True

    def update(self):
        logger.info(f"Updating votes for {self.candidate}")
        if self.lock_time == 0:
            self.lock_time = self.block_time
        row_data = (self.txid, self.block_hash, self.block_time, \
                    self.lock_time, self.block_height, self.votes, \
                    self.candidate, self.candidate_address, self.mined_by,
                    self.difficulty, self.notes)
        if self.validated():
            logger.info(f"Updating [vote2021_row] {self.txid} | \
                          {self.block_height} | {self.candidate} | \
                          {self.votes}")
            update_vote2021_row(row_data)
        else:
            logger.warning(f"[vote2021_row] Row data invalid!")
            logger.warning(f"{row_data}")

    def delete_txid(self):
        sql = f"DELETE FROM [vote2021_row] WHERE txid = '{self.txid}';"
        CURSOR.execute(sql)
        CONN.commit()


class swaps_row():
    def __init__(self, uuid='', started_at='', taker_coin='', 
                 taker_amount=0, taker_gui='', taker_version='',
                 taker_pubkey='', maker_coin='', maker_amount=0,
                 maker_gui='', maker_version='', maker_pubkey='', time_stamp=''):
        self.uuid = uuid
        self.started_at = started_at
        self.taker_coin = taker_coin
        self.taker_amount = taker_amount
        self.taker_gui = taker_gui
        self.taker_version = taker_version
        self.taker_pubkey = taker_pubkey
        self.maker_coin = maker_coin
        self.maker_amount = maker_amount
        self.maker_gui = maker_gui
        self.maker_version = maker_version
        self.maker_pubkey = maker_pubkey
        self.time_stamp = time_stamp

    def validated(self):
        return True

    def update(self):
        row_data = (self.uuid, self.started_at, self.taker_coin,
                    self.taker_amount, self.taker_gui, self.taker_version,
                    self.taker_pubkey, self.maker_coin, self.maker_amount,
                    self.maker_gui, self.maker_version, self.maker_pubkey, self.time_stamp)
        if self.validated():
            logger.info(f"Updating [swaps_row] {row_data}")
            update_swaps_row(row_data)
        else:
            logger.warning(f"[swaps_row] Row data invalid!")
            logger.warning(f"{row_data}")

    def delete(self, conditions):
        sql = f"DELETE FROM swaps WHERE {conditions};"
        CURSOR.execute(sql)
        CONN.commit()


class swaps_failed_row():
    def __init__(self, uuid='', started_at='', taker_coin='', 
                 taker_amount=0, taker_error_type='', taker_error_msg='',
                 taker_gui='', taker_version='', taker_pubkey='',
                 maker_coin='', maker_amount=0, maker_error_type='',
                 maker_error_msg='', maker_gui='', maker_version='',
                 maker_pubkey='', time_stamp=''):
        self.uuid = uuid
        self.started_at = started_at
        self.taker_coin = taker_coin
        self.taker_amount = taker_amount
        self.taker_error_type = taker_error_type
        self.taker_error_msg = taker_error_msg
        self.taker_gui = taker_gui
        self.taker_version = taker_version
        self.taker_pubkey = taker_pubkey
        self.maker_coin = maker_coin
        self.maker_amount = maker_amount
        self.maker_error_type = maker_error_type
        self.maker_error_msg = maker_error_msg
        self.maker_gui = maker_gui
        self.maker_version = maker_version
        self.maker_pubkey = maker_pubkey
        self.time_stamp = time_stamp

    def validated(self):
        return True

    def update(self):
        row_data = (self.uuid, self.started_at, self.taker_coin,
                    self.taker_amount, self.taker_error_type, self.taker_error_msg,
                    self.taker_gui, self.taker_version, self.taker_pubkey,
                    self.maker_coin, self.maker_amount,
                    self.maker_error_type, self.maker_error_msg,
                    self.maker_gui, self.maker_version, self.maker_pubkey, self.time_stamp)
        if self.validated():
            logger.info(f"Updating [swaps_failed_row] {row_data}")
            update_swaps_failed_row(row_data)
        else:
            logger.warning(f"[swaps_failed_row] Row data invalid!")
            logger.warning(f"{row_data}")

    def delete(self, conditions):
        sql = f"DELETE FROM swaps_failed WHERE {conditions};"
        CURSOR.execute(sql)
        CONN.commit()