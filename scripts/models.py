from lib_const import *
from lib_helper import *
from lib_table_select import get_epochs
from lib_table_update import *

class addresses_row():
    def __init__(self, season='', server='', notary='', notary_id='',
                 address='', pubkey='', chain=''):
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
        self.chain = handle_dual_server_chains(self.chain, self.server)
        row_data = (
            self.season, self.server, self.notary,
            self.notary_id, self.address, self.pubkey,
            self.chain
        )
        if self.validated():
            update_addresses_row(row_data)
            logger.info(f"Updated [addresses] | {self.season} | {self.server} | {self.notary} | {self.notary_id} | {self.address} | {self.pubkey} | {self.chain}")
        else:
            logger.warning(f"[addresses] Row data invalid!")
            logger.warning(f"{row_data}")

    def delete(self):
        delete_addresses_row(self.season, self.chain, self.address)
        logger.info(f"Deleted [addresses] row {self.season} | {self.chain} | {self.address}")


class balance_row():
    def __init__(self, season='', server='', notary='', address='',
                 chain='', balance='', update_time=0):
        self.notary = notary
        self.chain = chain
        self.balance = balance
        self.address = address
        self.season = season
        self.server = server
        self.update_time = update_time

    def validated(self):
        for i in [self.season, self.server, self.notary,
                  self.address, self.chain, self.balance,
                  self.update_time]:
            if i == '':
                return False
        return True

    def update(self):
        self.update_time = int(time.time())
        self.chain = handle_dual_server_chains(self.chain, self.server)
        row_data = (
            self.season, self.server, self.notary,
            self.address, self.chain, self.balance,
            self.update_time
        )
        if self.validated():
            logger.info(f"Updating [balance] {self.season} | {self.server} | {self.notary} | {self.chain} | {self.balance} | {self.address}")
            update_balances_row(row_data)
        else:
            logger.warning(f"[balance] Row data invalid!")
            logger.warning(f"{row_data}")

    def delete(self):
        delete_balances_row(self.chain, self.address, self.season)
        logger.info(f"Deleted balance row {self.season} | {self.chain} | {self.address}")

   
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
        row_data = (
            self.chain, self.coins_info, self.electrums,
            self.electrums_ssl, self.explorers, self.dpow,
            self.dpow_tenure,
            self.dpow_active, self.mm2_compatible
        )
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
        row_data = (
            self.txid, self.block_hash, self.block_height,
            self.block_time, self.block_datetime, self.address,
            self.notary, self.season, self.category, self.input_index,
            self.input_sats, self.output_index, self.output_sats,
            self.fees, self.num_inputs, self.num_outputs
        )
        if self.validated():
            if self.input_index != -1:
                logger.info(f"[btc_tx] Adding {self.season} {self.txid} {self.category} for {self.notary} VIN {self.input_index}")
            elif self.output_index != -1:
                logger.info(f"[btc_tx] Adding {self.season} {self.txid} {self.category} for {self.notary} VOUT {self.output_index}")
            else:
                logger.info(f"[btc_tx] Adding {self.season} {self.txid} {self.category} for {self.notary}")
            update_nn_btc_tx_row(row_data)
        else:
            logger.warning(f"[btc_tx] Row data invalid!")
            logger.warning(f"{OTHER_SERVER}/api/info/nn_btc_txid?txid={self.txid}")
            logger.warning(f"{row_data}")

    def delete(self):
        delete_nn_btc_tx_transaction(self.txid)


class nn_social_row():
    def __init__(self, notary='', twitter='', youtube='', discord='',
                 telegram='', github='', keybase='', website='',
                 icon='', season=''):
        self.notary = notary
        self.twitter = twitter
        self.youtube = youtube
        self.discord = discord
        self.telegram = telegram
        self.github = github
        self.keybase = keybase
        self.website = website
        self.icon = icon
        self.season = season

    def validated(self):
        return True

    def update(self):
        row_data = (
            self.notary, self.twitter, self.youtube,
            self.discord, self.telegram, self.github,
            self.keybase, self.website, self.icon, self.season
        )
        if self.validated():
            logger.info(f"Updating NN social {self.season} | {self.notary}")
            update_nn_social_row(row_data)
        else:
            logger.warning(f"[nn_social] Row data invalid!")
            logger.warning(f"{row_data}")

    def delete(self):
        pass


class coin_social_row():
    def __init__(self, coin='', twitter='', youtube='', discord='',
                 telegram='', github='', explorer='', website='',
                 icon='', season=''):
        self.coin = coin
        self.twitter = twitter
        self.youtube = youtube
        self.discord = discord
        self.telegram = telegram
        self.github = github
        self.explorer = explorer
        self.website = website
        self.icon = icon
        self.season = season

    def validated(self):
        return True

    def update(self):
        row_data = (
            self.coin, self.twitter, self.youtube,
            self.discord, self.telegram, self.github,
            self.explorer, self.website, self.icon, self.season
        )
        if self.validated():
            logger.info(f"Updating [coin_social] {self.season} | {self.coin}")
            update_coin_social_row(row_data)
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
        row_data = (
            self.chain, self.txid, self.vout, self.amount,
            self.block_hash, self.block_height, self.block_time,
            self.category, self.fee, self.address, self.notary, self.season
        )
        if self.validated():
            logger.info(f"Updating [funding] {self.chain} | {self.notary} ")
            update_funding_row(row_data)
        else:
            logger.warning(f"[funding] Row data invalid!")
            logger.warning(f"{row_data}")

    def delete(self):
        CURSOR.execute(f"DELETE FROM funding_transactions WHERE chain = '{self.chain}';")
        CONN.commit()


class notarised_chain_daily_row():
    def __init__(self, season='', server='', chain='', ntx_count='', notarised_date=''):
        self.season = season
        self.server = server
        self.chain = chain
        self.ntx_count = ntx_count
        self.notarised_date = notarised_date

    def validated(self):
        return True

    def update(self):
        self.chain = handle_dual_server_chains(self.chain, self.server)
        row_data = (self.season, self.server, self.chain, self.ntx_count, self.notarised_date)
        if self.validated():
            logger.info(f"Updating [notarised_chain_daily] {self.chain} {self.notarised_date}")
            update_daily_notarised_chain_row(row_data)
        else:
            logger.warning(f"[notarised_chain_daily_row] Row data invalid!")
            logger.warning(f"{row_data}")

    def delete(self):
        CURSOR.execute(f"DELETE FROM notarised_chain_daily WHERE chain = '{self.chain}' and notarised_date = '{self.notarised_date}';")
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
        row_data = (
            self.notary, self.btc_count, self.antara_count, 
            self.third_party_count, self.other_count, 
            self.total_ntx_count, self.chain_ntx_counts, 
            self.chain_ntx_pct, self.time_stamp, self.season,
            self.notarised_date
        )
        if self.validated():
            logger.info(f"Updating [notarised_count_daily]  {self.notary} {self.notarised_date}")
            update_daily_notarised_count_row(row_data)
        else:
            logger.warning(f"[notarised_count_daily_row] Row data invalid!")
            logger.warning(f"{row_data}")

    def delete(self):
        CURSOR.execute(f"DELETE FROM notarised_count_daily WHERE notary = '{self.notary}' and notarised_date = '{self.notarised_date}';")
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
        row_data = (
            self.notary, self.btc_count, self.antara_count, 
            self.third_party_count, self.other_count, 
            self.total_ntx_count, self.chain_ntx_counts, self.season_score, 
            self.chain_ntx_pct, self.time_stamp, self.season
        )
        if self.validated():
            logger.info(f"Updating [notarised_count_season] {self.notary} {self.season} {self.season_score}")
            update_season_notarised_count_row(row_data)
        else:
            logger.warning(f"[notarised_count_season] Row data invalid!")
            logger.warning(f"{row_data}")

    def delete(self):
        CURSOR.execute(f"DELETE FROM notarised_count_season WHERE notary = '{self.notary}' and season = '{self.season}';")
        CONN.commit()

       
class notarised_chain_season_row():
    def __init__(self, chain='', ntx_count='', block_height='', kmd_ntx_blockhash='',
          kmd_ntx_txid='', kmd_ntx_blocktime='', opret='', ac_ntx_blockhash='', 
          ac_ntx_height='', ac_block_height='', ntx_lag='', season='', server=''):
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
        row_data = (
            self.chain, self.ntx_count, self.block_height, self.kmd_ntx_blockhash,
            self.kmd_ntx_txid, self.kmd_ntx_blocktime, self.opret, self.ac_ntx_blockhash, 
            self.ac_ntx_height, self.ac_block_height, self.ntx_lag, self.season, self.server
        )
        if self.validated():
            logger.info(f"Updating [notarised_chain_season] {self.chain} {self.season} {self.server}")
            update_season_notarised_chain_row(row_data)
        else:
            logger.warning(f"[notarised_chain_season] Row data invalid!")
            logger.warning(f"{row_data}")

    def delete(self):
        CURSOR.execute(f"DELETE FROM notarised_chain_season WHERE chain = '{self.chain}' and season = '{self.season}';")
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
        self.chain = handle_dual_server_chains(self.chain, self.server)
        row_data = (
            self.notary, self.chain, self.txid, self.block_height, \
            self.block_time, self.season, self.server
        )
        if self.validated():
            logger.info(f"[last_notarised] Updating {self.notary} {self.chain} {self.season} {self.server} {self.block_height}")
            update_last_ntx_row(row_data)
        else:
            logger.warning(f"[last_notarised] Row data invalid!")
            logger.warning(f"{row_data}")

    def delete(self):
        CURSOR.execute(f"DELETE FROM last_notarised WHERE notary = '{self.notary}' and chain = '{self.chain}';")
        CONN.commit()


class mined_row():
    def __init__(self, block_height='', block_time='', block_datetime='', 
             value='', address='', name='', txid='', season=''):
        self.block_height = block_height
        self.block_time = block_time
        self.block_datetime = block_datetime
        self.value = value
        self.address = address
        self.name = name
        self.txid = txid
        self.season = season

    def validated(self):
        for item in [self.address, self.name, self.season]:
            if item == '':
                return False
        return True

    def update(self):
        self.season = get_season_from_block(self.block_height)
        self.name = get_name_from_address(self.address)
        row_data = (
            self.block_height, self.block_time, self.block_datetime, 
            self.value, self.address, self.name, self.txid, self.season
        )

        if self.validated():
            update_mined_row(row_data)
            logger.info(f"Updated [mined] {self.block_height} | {self.name} | {self.season} | {self.value} ")

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
    def __init__(self, name='', address='', season='', blocks_mined='', sum_value_mined='', 
            max_value_mined='', last_mined_blocktime='', last_mined_block='', 
            time_stamp=int(time.time())):
        self.name = name
        self.address = address
        self.season = season
        self.blocks_mined = blocks_mined
        self.sum_value_mined = sum_value_mined
        self.max_value_mined = max_value_mined
        self.last_mined_blocktime = last_mined_blocktime
        self.last_mined_block = last_mined_block
        self.time_stamp = time_stamp

    def validated(self):
        for item in [self.address, self.name, self.season]:
            if item == '':
                return False
        if self.season.find("Testnet") != -1:
            return False
        # Overcome where old season address mines within this season.
        if self.name in NOTARY_PUBKEYS[self.season]:
            if self.address != NOTARY_ADDRESSES_DICT[self.season][self.name]["KMD"]:
                return False
        return True

    def update(self):
        row_data = (
            self.name, self.season, self.address, self.blocks_mined, 
            self.sum_value_mined, self.max_value_mined,
            self.last_mined_blocktime, self.last_mined_block, self.time_stamp
        ) 
        if self.validated():
            update_season_mined_count_row(row_data)
            logger.info(f"[mined_count_season] updated: {self.name} {self.season} {self.last_mined_block} {self.sum_value_mined}")
            logger.info(f"[mined_count_season] updated: {row_data}")
        else:
            logger.warning(f"[mined_count_season] Row data invalid!")
            logger.warning(f"{row_data}")

    def delete(self):
        CURSOR.execute(f"DELETE FROM mined_count_season WHERE name = '{self.name}';")
        CONN.commit()

    def delete_season(self):
        CURSOR.execute(f"DELETE FROM mined_count_season WHERE season = '{self.season}';")
        CONN.commit()

    def delete_address(self):
        CURSOR.execute(f"DELETE FROM mined_count_season WHERE address = '{self.address}';")
        CONN.commit()
        logger.info(f"[mined_count_season] {self.address} rows deleted")

    def delete_name(self):
        CURSOR.execute(f"DELETE FROM mined_count_season WHERE name = '{self.name}';")
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
        row_data = (
            self.notary, self.blocks_mined, self.sum_value_mined, \
            self.mined_date, self.time_stamp
        )
        if self.validated():
            logger.info(f"Updating [mined_count_daily] {self.notary} {self.mined_date} ")
            update_daily_mined_count_row(row_data)
        else:
            logger.warning(f"[mined_count_daily] Row data invalid!")
            logger.warning(f"{row_data}")

    def delete(self):
        CURSOR.execute(f"DELETE FROM mined_count_daily WHERE notary = '{self.notary}';")
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
        row_data = (
            self.txid, self.block_hash, self.block_height,
            self.block_time, self.block_datetime, self.address,
            self.notary, self.season, self.category, self.input_index,
            self.input_sats, self.output_index, self.output_sats,
            self.fees, self.num_inputs, self.num_outputs
        )
        if self.validated():
            if self.input_index != -1:
                logger.info(f"[ltc_tx_row] Adding {self.season} {self.txid} {self.category} for {self.notary} VIN {self.input_index}")
            elif self.output_index != -1:
                logger.info(f"[ltc_tx_row] Adding {self.season} {self.txid} {self.category} for {self.notary} VOUT {self.output_index}")
            else:
                logger.info(f"[ltc_tx_row] Adding {self.season} {self.txid} {self.category} for {self.notary}")
            update_nn_ltc_tx_row(row_data)
        else:
            logger.warning(f"[ltc_tx_row] Row data invalid!")
            logger.warning(f"{OTHER_SERVER}/api/info/nn_ltc_txid?txid={self.txid}")
            logger.warning(f"{row_data}")


    def delete(self):
        delete_nn_ltc_tx_transaction(self.txid)


class scoring_epoch_row():
    def __init__(self, season='', server='', epoch='',epoch_start=0, epoch_end=0, \
                    start_event='', end_event='', epoch_chains=list, score_per_ntx=0):
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
        for chain in self.epoch_chains:
            if self.season in DPOW_EXCLUDED_CHAINS:
                if chain in DPOW_EXCLUDED_CHAINS[self.season]:
                    logger.warning(f"{chain} in DPOW_EXCLUDED_CHAINS[{self.season}]")
                    self.delete(season, server, epoch)
                    return False
        return True

    def update(self):

        row_data = (self.season, self.server, self.epoch, self.epoch_start, self.epoch_end, \
                    self.start_event, self.end_event, self.epoch_chains, self.score_per_ntx)
        if self.validated():
            if self.server == "Testnet":
                self.server == "Main"
            if len(self.epoch_chains) == 0:
                self.epoch_chains = [None]
            update_scoring_epoch_row(row_data)
            logger.info(f"Updated [scoring_epochs] {self.season} | {self.server} | {self.epoch} ")
        else:
            logger.warning(f"[scoring_epochs] Row data invalid!")
            logger.warning(f"{row_data}")

    def delete(self, season=None, server=None, epoch=None):
        if not season and not server and not epoch:
            logger.error("Not deleting, need to specify at least one of epoch, season or server")
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


class notarised_row():
    def __init__(self, chain='', block_height='', 
                 block_time='', block_datetime='', block_hash='', 
                 notaries=list, notary_addresses=list, ac_ntx_blockhash='',
                 ac_ntx_height='', txid='', opret='', season='', server='',
                 scored=True, score_value=0, btc_validated='', epoch=''):
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
        self.btc_validated = btc_validated

    def validated(self):
        if len(self.chain) > 12:
            return False
        if self.epoch not in ["KMD", "LTC", "BTC"]:
            if self.epoch.find("Epoch") == -1 and self.epoch != "Unofficial":
                logger.warning(f"!!!! Invalid epoch {self.epoch}")
                return False

        if self.server in ["Main", "Third_Party", "KMD", "LTC", "BTC"]:
            for notary in self.notaries[:]:
                if len(notary) > 20:
                    try:
                        self.notaries.remove(notary)
                        self.notaries.append(KNOWN_ADDRESSES[notary])
                        logger.warning(f"!!!! {self.txid} Invalid notary {notary} set to {KNOWN_ADDRESSES[notary]}")
                    except:
                        logger.warning(f"!!!! {self.txid} Invalid notary {notary}")
                        return False
        return True

    def update(self):
        self.chain = handle_dual_server_chains(self.chain, self.server)
        self.season, self.server = get_season_from_addresses(self.notary_addresses[:], self.block_time, "KMD", self.chain, self.txid, self.notaries)
        self.epoch = get_chain_epoch_at(self.season, self.server, self.chain, self.block_time)

        if self.season in DPOW_EXCLUDED_CHAINS:
            if self.chain in DPOW_EXCLUDED_CHAINS[self.season]:
                self.season = "Unofficial"
                self.server = "Unofficial"
                self.epoch = "Unofficial"

        if self.chain in ["KMD" ,"LTC", "BTC"]:
            self.server = self.chain
            self.epoch = self.chain
            if self.chain in ["KMD"]:
                if int(self.block_time) >= SEASONS_INFO[self.season]['start_time'] and int(self.block_time) <= SEASONS_INFO[self.season]['end_time']:
                    self.score_value = 0.0325
                else:
                    self.score_value = 0
            elif self.chain in ["LTC", "BTC"]:
                self.score_value = 0
        else:
            self.score_value = round(self.score_value, 8)
            score_value = get_chain_epoch_score_at(self.season, self.server, self.chain, self.block_time)
        if self.score_value > 0:
            self.scored = True
        else:
            self.scored = False

        row_data = (
            self.chain, self.block_height, 
            self.block_time, self.block_datetime, self.block_hash, 
            self.notaries, self.notary_addresses, self.ac_ntx_blockhash,
            self.ac_ntx_height, self.txid, self.opret, self.season,
            self.server, self.scored, self.score_value, self.btc_validated, self.epoch
        )
        if self.validated():
            logger.info(f"Updating [notarised] {self.txid} {self.chain} | {self.season} {self.server} {self.epoch} | {self.scored} {self.score_value} | {self.block_datetime}")
            update_ntx_row(row_data)
        else:
            logger.warning(f"[notarised] row invalid {self.chain} {self.season} {self.server} {self.epoch} {self.scored} {self.score_value} {self.block_datetime}")
            logger.warning(f"{row_data}")

    def delete(self):
        CURSOR.execute(f"DELETE FROM notarised WHERE txid = '{self.txid}';")
        CONN.commit()


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
            logger.warning(f"!!!!  [notarised_tenure] Invalid server {server}")
            return False
        if self.season not in ['Season_5', 'Season_5_Testnet', 'Season_4']:
            logger.warning(f"!!!! [notarised_tenure] Invalid season {season}")
            return False
        return True

    def update(self):
        # TODO: Validation start / end within season window

        if self.chain in ["KMD" ,"LTC", "BTC"]:
            self.server = self.chain

        if self.chain in ["LTC", "BTC"]:
            self.unscored_ntx_count = self.unscored_ntx_count + self.scored_ntx_count
            self.scored_ntx_count = 0

        row_data = (
            self.chain, self.first_ntx_block, 
            self.last_ntx_block, self.first_ntx_block_time,
            self.last_ntx_block_time, self.official_start_block_time, 
            self.official_end_block_time, self.unscored_ntx_count, 
            self.scored_ntx_count, self.season, self.server
        )

        if self.validated():
            logger.info(f">>> Updating [notarised_tenure] {self.chain} {self.season} {self.server} || {self.scored_ntx_count} scored, {self.unscored_ntx_count} unscored")
            update_notarised_tenure_row(row_data)

        else:
            logger.warning(f"!!! Invalid row [notarised_tenure] {self.chain} {self.season} {self.server} || {self.scored_ntx_count} scored, {self.unscored_ntx_count} unscored")
            logger.warning(f"{row_data}")

    def delete(self, season=None, server=None, chain=None):
        if not season and not server and not chain:
            logger.error("Not deleting, need to specify at least one of chain, season or server")
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
            logger.warning(f"Deleting [notarised_tenure] row: {season} {server} {chain}")

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
        row_data = (
            self.txid, self.block_hash, self.block_time, \
            self.lock_time, self.block_height, self.votes, \
            self.candidate, self.candidate_address, self.mined_by,
            self.difficulty, self.notes
        )
        if self.validated():
            logger.info(f"Updating [vote2021_row] {self.txid} | {self.block_height} | {self.candidate} | {self.votes}")
            update_vote2021_row(row_data)
        else:
            logger.warning(f"[vote2021_row] Row data invalid!")
            logger.warning(f"{row_data}")

    def delete_txid(self):
        CURSOR.execute(f"DELETE FROM [vote2021_row] WHERE txid = '{self.txid}';")
        CONN.commit()
