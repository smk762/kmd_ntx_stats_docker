import time
import logging
import logging.handlers
from lib_table_update import *
from lib_const import CONN, CURSOR

logger = logging.getLogger(__name__)

class balance_row():
    def __init__(self, notary='', chain='', balance='', address='',
                 season='', node='', time=int(time.time())):
        self.notary = notary
        self.chain = chain
        self.balance = balance
        self.address = address
        self.season = season
        self.node = node
        self.time = time

    def validated(self):

        for i in [
            self.notary, self.chain, self.balance,
            self.address, self.season, self.node,
            self.time
            ]:

            if i == '':
                return False

        return True

    def update(self):
        row_data = (
            self.notary, self.chain, self.balance,
            self.address, self.season, self.node,
            self.time
        )
        if self.validated():
            logger.info(f"Updating balance {self.season} | {self.node} | {self.notary} | {self.chain} | {self.balance} | {self.address}")
            update_balances_row(row_data)
        else:
            logger.warning(f"Row data invalid!")
            logger.warning(f"{row_data}")


    def delete(self):
        delete_balances_row(self.chain, self.address, self.season)
        logger.info(f"Deleted balance row {self.season} | {self.chain} | {self.address}")

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
                logger.info(f"Adding {self.season} {self.txid} {self.category} for {self.notary} VIN {self.input_index}")
            elif self.output_index != -1:
                logger.info(f"Adding {self.season} {self.txid} {self.category} for {self.notary} VOUT {self.output_index}")
            else:
                logger.info(f"Adding {self.season} {self.txid} {self.category} for {self.notary}")
            update_nn_btc_tx_row(row_data)
        else:
            logger.warning(f"Row data invalid!")
            logger.warning(f"{OTHER_SERVER}/api/info/nn_btc_txid?txid={self.txid}")
            logger.warning(f"{row_data}")

    def insert(self):
        row_data = (
            self.txid, self.block_hash, self.block_height,
            self.block_time, self.block_datetime, self.address,
            self.notary, self.season, self.category, self.input_index,
            self.input_sats, self.output_index, self.output_sats,
            self.fees, self.num_inputs, self.num_outputs
        )
        if self.validated():
            if self.input_index != -1:
                logger.info(f"Inserting {self.season} {self.txid} {self.category} for {self.notary} VIN {self.input_index}")
            elif self.output_index != -1:
                logger.info(f"Inserting {self.season} {self.txid} {self.category} for {self.notary} VOUT {self.output_index}")
            else:
                logger.info(f"Inserting {self.season} {self.txid} {self.category} for {self.notary}")
            insert_nn_btc_tx_row(row_data)
        else:
            logger.warning(f"Row data invalid!")
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
            logger.warning(f"Row data invalid!")
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
            logger.info(f"Updating NN social {self.season} | {self.coin}")
            update_coin_social_row(row_data)
        else:
            logger.warning(f"Row data invalid!")
            logger.warning(f"{row_data}")

    def delete(self):
        pass
        
class rewards_row():
    def __init__(self, addr='', notary='', utxo_count='', eligible_utxo_count='',
                   oldest_utxo_block='', balance='', total_rewards='',
                   update_time=int(time.time())):
        self.addr = addr
        self.notary = notary
        self.utxo_count = utxo_count
        self.eligible_utxo_count = eligible_utxo_count
        self.oldest_utxo_block = oldest_utxo_block
        self.balance = balance
        self.total_rewards = total_rewards
        self.update_time = update_time

    def validated(self):
        return True

    def update(self):
        row_data = (
            self.addr, self.notary, self.utxo_count,
            self.eligible_utxo_count, self.oldest_utxo_block, self.balance,
            self.total_rewards, self.update_time
        )
        if self.validated():
            logger.info(f"Updating KMD REWARDS {self.notary} | REWARDS {self.total_rewards}")
            logger.info(f"Oldest unclaimed block: {self.oldest_utxo_block}")
            update_rewards_row(row_data)
        else:
            logger.warning(f"Row data invalid!")
            logger.warning(f"{row_data}")

    def delete(self):
        pass
        

class coins_row():
    def __init__(self, chain='', coins_info='',
     electrums='', electrums_ssl='', explorers='',
     dpow='', dpow_active='', mm2_compatible=''):
        self.chain = chain
        self.coins_info = coins_info
        self.electrums = electrums
        self.electrums_ssl = electrums_ssl
        self.explorers = explorers
        self.dpow = dpow
        self.dpow_active = dpow_active
        self.mm2_compatible = mm2_compatible

    def validated(self):
        return True

    def update(self):
        row_data = (
            self.chain, self.coins_info, self.electrums,
            self.electrums_ssl, self.explorers, self.dpow,
            self.dpow_active, self.mm2_compatible
        )
        if self.validated():
            logger.info(f"Updating COIN TABLE {self.chain} ")
            update_coins_row(row_data)
        else:
            logger.warning(f"Row data invalid!")
            logger.warning(f"{row_data}")

    def delete(self):
        CURSOR.execute(f"DELETE FROM coins WHERE chain = '{self.chain}';")
        CONN.commit()
        

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
            logger.info(f"Updating FUNDING TABLE {self.chain} | {self.notary} ")
            update_funding_row(row_data)
        else:
            logger.warning(f"Row data invalid!")
            logger.warning(f"{row_data}")

    def delete(self):
        CURSOR.execute(f"DELETE FROM funding_transactions WHERE chain = '{self.chain}';")
        CONN.commit()
        

class notarised_chain_daily_row():
    def __init__(self, chain='', ntx_count='', notarised_date=''):
        self.chain = chain
        self.ntx_count = ntx_count
        self.notarised_date = notarised_date

    def validated(self):
        return True

    def update(self):
        row_data = (
            self.chain, self.ntx_count, self.notarised_date
        )
        if self.validated():
            logger.info(f"Updating notarised_chain_daily TABLE {self.chain} {self.notarised_date}")
            update_daily_notarised_chain_row(row_data)
        else:
            logger.warning(f"Row data invalid!")
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
            logger.info(f"Updating notarised_count_daily TABLE {self.notary} {self.notarised_date}")
            update_daily_notarised_count_row(row_data)
        else:
            logger.warning(f"Row data invalid!")
            logger.warning(f"{row_data}")

    def delete(self):
        CURSOR.execute(f"DELETE FROM notarised_count_daily WHERE notary = '{self.notary}' and notarised_date = '{self.notarised_date}';")
        CONN.commit()
        
class notarised_count_season_row():
    def __init__(self, notary='', btc_count='', antara_count='', 
        third_party_count='', other_count='', 
        total_ntx_count='', chain_ntx_counts='', 
        chain_ntx_pct='', time_stamp=int(time.time()),
        season=''):
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

    def validated(self):
        return True

    def update(self):
        row_data = (
            self.notary, self.btc_count, self.antara_count, 
            self.third_party_count, self.other_count, 
            self.total_ntx_count, self.chain_ntx_counts, 
            self.chain_ntx_pct, self.time_stamp, self.season
        )
        if self.validated():
            logger.info(f"Updating notarised_count_season TABLE {self.notary} {self.season}")
            update_season_notarised_count_row(row_data)
        else:
            logger.warning(f"Row data invalid!")
            logger.warning(f"{row_data}")

    def delete(self):
        CURSOR.execute(f"DELETE FROM notarised_count_season WHERE notary = '{self.notary}' and season = '{self.season}';")
        CONN.commit()
        
class notarised_chain_season_row():
    def __init__(self, chain='', ntx_count='', block_height='', kmd_ntx_blockhash='',
          kmd_ntx_txid='', kmd_ntx_blocktime='', opret='', ac_ntx_blockhash='', 
          ac_ntx_height='', ac_block_height='', ntx_lag='', season=''):
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

    def validated(self):
        return True

    def update(self):
        row_data = (
            self.chain, self.ntx_count, self.block_height, self.kmd_ntx_blockhash,
            self.kmd_ntx_txid, self.kmd_ntx_blocktime, self.opret, self.ac_ntx_blockhash, 
            self.ac_ntx_height, self.ac_block_height, self.ntx_lag, self.season
        )
        if self.validated():
            logger.info(f"Updating notarised_chain_season TABLE {self.chain} {self.season}")
            update_season_notarised_chain_row(row_data)
        else:
            logger.warning(f"Row data invalid!")
            logger.warning(f"{row_data}")

    def delete(self):
        CURSOR.execute(f"DELETE FROM notarised_chain_season WHERE chain = '{self.chain}' and season = '{self.season}';")
        CONN.commit()
        
class last_notarised_row():
    def __init__(self, notary='', chain='', txid='', block_height='', \
            block_time='', season=''):
        self.notary = notary
        self.chain = chain
        self.txid = txid
        self.block_height = block_height
        self.block_time = block_time
        self.season = season

    def validated(self):
        return True

    def update(self):
        row_data = (
            self.notary, self.chain, self.txid, self.block_height, \
            self.block_time, self.season
        )
        if self.validated():
            logger.info(f"Updating last_notarised TABLE {self.notary} {self.chain} {self.block_height}")
            update_last_ntx_row(row_data)
        else:
            logger.warning(f"Row data invalid!")
            logger.warning(f"{row_data}")

    def delete(self):
        CURSOR.execute(f"DELETE FROM last_notarised WHERE notary = '{self.notary}' and chain = '{self.chain}';")
        CONN.commit()

class ntx_records_row():
    def __init__(self, chain='', block_height='', 
                block_time='', block_datetime='', block_hash='', 
                notaries='', ac_ntx_blockhash='', ac_ntx_height='', 
                txid='', opret='', season='', btc_validated=''):
        self.chain = chain
        self.block_height = block_height
        self.block_time = block_time
        self.block_datetime = block_datetime
        self.block_hash = block_hash
        self.notaries = notaries
        self.ac_ntx_blockhash = ac_ntx_blockhash
        self.ac_ntx_height = ac_ntx_height
        self.txid = txid
        self.opret = opret
        self.season = season
        self.btc_validated = btc_validated

    def validated(self):
        return True

    def update(self):
        row_data = (
            self.chain, self.block_height, 
            self.block_time, self.block_datetime, self.block_hash, 
            self.notaries, self.ac_ntx_blockhash, self.ac_ntx_height, 
            self.txid, self.opret, self.season, self.btc_validated
        )
        if self.validated():
            logger.info(f"Updating notarised TABLE {self.chain} {self.season}")
            update_ntx_row(row_data)
        else:
            logger.warning(f"Row data invalid!")
            logger.warning(f"{row_data}")

    def delete(self):
        CURSOR.execute(f"DELETE FROM notarised WHERE chain = '{self.chain}'and season='{self.season}';")
        CONN.commit()


        
class ntx_tenure_row():
    def __init__(self, chain='', first_ntx_block='', 
            last_ntx_block='', first_ntx_block_time='',
            last_ntx_block_time='', ntx_count='', season=''):
        self.chain = chain
        self.first_ntx_block = first_ntx_block
        self.last_ntx_block = last_ntx_block
        self.first_ntx_block_time = first_ntx_block_time
        self.last_ntx_block_time = last_ntx_block_time
        self.ntx_count = ntx_count
        self.season = season

    def validated(self):
        return True

    def update(self):
        row_data = (
            self.chain, self.first_ntx_block, 
            self.last_ntx_block, self.first_ntx_block_time,
            self.last_ntx_block_time, self.ntx_count, self.season
        )
        if self.validated():
            logger.info(f"Updating notarised_tenure TABLE {self.chain} {self.season}")
            update_notarised_tenure_row(row_data)
        else:
            logger.warning(f"Row data invalid!")
            logger.warning(f"{row_data}")

    def delete(self):
        CURSOR.execute(f"DELETE FROM notarised_tenure WHERE chain = '{self.chain}'and season='{self.season}';")
        CONN.commit()
        


## KMD MINING CLASSES ###

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
        return True

    def update(self):
        row_data = (
            self.block_height, self.block_time, self.block_datetime, 
            self.value, self.address, self.name, self.txid, self.season
        )
        if self.validated():
            update_mined_row(row_data)
            logger.info(f"Updated mined TABLE {self.block_height} | {self.name} | {self.value} ")
        else:
            logger.warning(f"Row data invalid!")
            logger.warning(f"{row_data}")

    def delete(self):
        CURSOR.execute(f"DELETE FROM mined WHERE name = '{self.name}';")
        CONN.commit()

class season_mined_count_row():
    def __init__(self, notary='', season='', blocks_mined='', sum_value_mined='', 
            max_value_mined='', last_mined_blocktime='', last_mined_block='', 
            time_stamp=int(time.time())):
        self.notary = notary
        self.season = season
        self.blocks_mined = blocks_mined
        self.sum_value_mined = sum_value_mined
        self.max_value_mined = max_value_mined
        self.last_mined_blocktime = last_mined_blocktime
        self.last_mined_block = last_mined_block
        self.time_stamp = time_stamp

    def validated(self):
        return True

    def update(self):
        row_data = (
            self.notary, self.season, self.blocks_mined, 
            self.sum_value_mined, self.max_value_mined,
            self.last_mined_blocktime, self.last_mined_block, self.time_stamp
        )
        if self.validated():
            logger.info(f"Updating season_mined_count TABLE {self.notary} ")
            update_season_mined_count_row(row_data)
        else:
            logger.warning(f"Row data invalid!")
            logger.warning(f"{row_data}")

    def delete(self):
        CURSOR.execute(f"DELETE FROM season_mined_count WHERE notary = '{self.notary}';")
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
            logger.info(f"Updating mined_count_daily TABLE {self.notary} {self.mined_date} ")
            update_daily_mined_count_row(row_data)
        else:
            logger.warning(f"Row data invalid!")
            logger.warning(f"{row_data}")

    def delete(self):
        CURSOR.execute(f"DELETE FROM mined_count_daily WHERE notary = '{self.notary}';")
        CONN.commit()

