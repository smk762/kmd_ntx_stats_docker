from lib_const import *
from lib_helper import *
import lib_validate
import lib_crypto
from lib_update import *
import lib_filter as filters
import lib_helper as helper
from datetime import datetime as dt

class addresses_row():
    def __init__(self, season='', server='', notary='',
                 notary_id='', address='', pubkey='', coin=''):
        self.season = season
        self.server = server
        self.notary = notary
        self.notary_id = notary_id
        self.address = address
        self.pubkey = pubkey
        self.coin = coin

    def validated(self):
        for i in [self.season, self.server, self.notary,
                  self.notary_id, self.address, self.pubkey,
                  self.coin]:
            if i == '':
                return False
        return True

    def update(self):

        self.server, self.coin = lib_validate.handle_dual_server_coins(self.server, self.coin)
        self.address = lib_crypto.get_addr_from_pubkey(self.coin, self.pubkey)

        row_data = (self.season, self.server, self.notary,
                    self.notary_id, self.address, self.pubkey,
                    self.coin)
        if self.validated():
            update_addresses_row(row_data)
            logger.info(f"Updated [addresses] | {self.season} | {self.server} | {self.notary} | {self.address} | {self.coin}")
        else:
            logger.warning(f"[addresses] Row data invalid!")
            logger.warning(f"{row_data}")

    def delete(self):
        delete_addresses_row(self.season, self.coin, self.address)
        logger.info(f"Deleted [addresses] row {self.season} | {self.coin} | {self.address}")


class balance_row():
    def __init__(self, season='', server='', notary='', address='',
                 coin='', balance=0, update_time=0):
        self.notary = notary
        self.coin = coin
        self.balance = balance
        self.address = address
        self.season = season
        self.server = server
        self.update_time = update_time

    def validated(self):
        for i in [self.season, self.server, self.notary,
                  self.address, self.coin, self.update_time]:
            if i == '':
                return False
        return True

    def update(self):
        self.update_time = int(time.time())
        self.server, self.coin = lib_validate.handle_dual_server_coins(
                                    self.server, self.coin
                                )
        self.balance = lib_validate.get_balance(self.coin, self.pubkey, self.address)
        row_data = (self.season, self.server, self.notary,
            self.address, self.coin, self.balance,
            self.update_time)

        if self.validated():
            logger.info(f"Updating [balance] {self.season} | {self.server} | {self.notary} | {self.coin} | {self.balance} | {self.address} | {self.update_time}")
            update_balances_row(row_data)
        else:
            logger.warning(f"[balance] Row data invalid!")
            logger.warning(f"{row_data}")

    def delete(self):
        delete_balances_row(self.coin, self.address, self.season)
        logger.info(f"Deleted balance row {self.season} | {self.coin} | \
                      {self.address}")

   
class coins_row():
    def __init__(self, coin='', coins_info='',
     electrums='', electrums_ssl='', electrums_wss='', explorers='', lightwallets='',
     dpow='', dpow_tenure=dict, dpow_active='', mm2_compatible=''):
        self.coin = coin
        self.coins_info = coins_info
        self.electrums = electrums
        self.electrums_ssl = electrums_ssl
        self.electrums_wss = electrums_wss
        self.explorers = explorers
        self.lightwallets = lightwallets
        self.dpow = dpow
        self.dpow_tenure = dpow_tenure
        self.dpow_active = dpow_active
        self.mm2_compatible = mm2_compatible

    def validated(self):
        return True

    def update(self):
        row_data = (self.coin, self.coins_info, self.electrums,
            self.electrums_ssl, self.electrums_wss, self.explorers, self.lightwallets, self.dpow,
            self.dpow_tenure, self.dpow_active, self.mm2_compatible)
        if self.validated():
            update_coins_row(row_data)
        else:
            logger.warning(f"[coins] Row data invalid!")
            logger.warning(f"{row_data}")

    def delete(self):
        CURSOR.execute(f"DELETE FROM coins WHERE coin = '{self.coin}';")
        CONN.commit()
        logger.info(f"Deleted {self.coin} from [coins] ")
  

class kmd_supply_row():
    def __init__(self, block_height='', block_time='', total_supply='', delta=''):
        self.block_time = block_time
        self.block_height = block_height
        self.total_supply = total_supply
        self.delta = delta

    def validated(self):
        return True

    def update(self):
        row_data = (self.block_height, self.block_time, self.total_supply, self.delta)
        if self.validated():
            logger.info(f"Updating [kmd_supply_row] {self.total_supply} at height {self.block_height} with delta {self.delta}")
            update_kmd_supply_row(row_data)
        else:
            logger.warning(f"[kmd_supply_row] Row data invalid!")
            logger.warning(f"{row_data}")

    def delete(self, block=None):
        if block:
            CURSOR.execute(f"DELETE FROM kmd_supply WHERE block_height = {self.block_height};")
        else:
            CURSOR.execute(f"DELETE FROM kmd_supply;")
        CONN.commit()
        logger.info(f"Deleted {self.block_height} from [kmd_supply] ")
  

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
            self.notary = lib_validate.get_name_from_address(self.address)

        self.season = lib_validate.get_season(self.block_time)

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
    def __init__(self='', coin='', discord='', email='', explorers=list,
                 github='', icon='', linkedin='', mining_pools=list,
                 reddit='', telegram='', twitter='', youtube='',
                 website='', season=''):
        self.coin = coin
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
        self.coin = handle_translate_coins(self.coin)

        row_data = (self.coin, self.discord, self.email, self.explorers,
                    self.github, self.icon, self.linkedin, self.mining_pools,
                    self.reddit, self.telegram, self.twitter, self.youtube,
                    self.website, self.season)
        if self.validated():
            update_coin_social_row(row_data)
            logger.info(f"Updated [coin_social] {self.season} | {self.coin}")
        else:
            logger.warning(f"[coin_social] Row data invalid!")
            logger.warning(f"{row_data}")

    def delete(self):
        pass

        
class funding_row():
    def __init__(self, coin='', txid='', vout='', amount='',
            block_hash='', block_height='', block_time='',
            category='', fee='', address='', notary='', season=''):
        self.coin = coin
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
        self.coin = handle_translate_coins(self.coin)
        row_data = (self.coin, self.txid, self.vout, self.amount,
                    self.block_hash, self.block_height, self.block_time,
                    self.category, self.fee, self.address, self.notary,
                    self.season)
        if self.validated():
            logger.info(f"Updating [funding] {self.coin} | {self.notary} ")
            update_funding_row(row_data)
        else:
            logger.warning(f"[funding] Row data invalid!")
            logger.warning(f"{row_data}")

    def delete(self):
        sql = f"DELETE FROM funding_transactions WHERE coin = '{self.coin}';"
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
            self.notary = lib_validate.get_name_from_address(self.address)

        self.season = lib_validate.get_season(self.block_time)

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



######### NTX Related ##########
class notarised_row():
    def __init__(self, coin='', block_height='', 
                 block_time='', block_datetime='', block_hash='', 
                 notaries=list, notary_addresses=list, ac_ntx_blockhash='',
                 ac_ntx_height='', txid='', opret='', season='', server='',
                 scored=True, score_value=0, epoch=''):
        self.coin = coin
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
        if len(self.coin) in ["CHIPS", "MIL", "VRSC"] and self.season == "Season_6":
            if self.epoch == "Epoch_0":
                self.score_value = 0
                self.scored = False
                self.epoch = "Unofficial"
                self.season = "Season_5"

        if len(self.coin) > 12:
            return False

        for notary in self.notaries:
            if len(notary) > 20:
                return False

        if self.season.find('Testnet') != -1 and self.block_height < 2903777:
            logger.warning("Testnet block below 2903777")
            return False

        return True

    def update(self):

        if self.season.find('Testnet') != -1:
            testnet = True
        else:
            testnet = False            

        self.server, self.coin = lib_validate.handle_dual_server_coins(
            self.server, self.coin
        )

        self.season, self.server, self.epoch, testnet = lib_validate.validate_season_server_epoch(
            self.season, self.notary_addresses,
            self.block_time, self.coin, testnet
        )

        if self.season == "Unofficial":
            logger.warning(f"[notarised] Unofficial {self.block_datetime} {self.txid} {self.season} {self.server} {self.epoch} | {self.scored} {self.score_value} {self.coin}")
            return

        self.score_value = lib_validate.get_coin_epoch_score_at(
            self.season, self.server, self.coin, int(self.block_time), testnet
        )
      
        self.scored = lib_validate.get_scored(self.score_value)

        # Sort lists for slightly simpler aggregation
        self.notaries.sort()
        self.notary_addresses.sort()

        row_data = (self.coin, self.block_height, 
                    self.block_time, self.block_datetime, self.block_hash, 
                    self.notaries, self.notary_addresses,
                    self.ac_ntx_blockhash, self.ac_ntx_height, self.txid,
                    self.opret, self.season, self.server, self.scored,
                    self.score_value, self.epoch)

        if self.validated():
            logger.info(f"Updating [notarised] {self.block_datetime} [{self.block_height}] {self.txid} {self.season} {self.server} {self.epoch} | {self.scored} {self.score_value} {self.coin} ")
            update_ntx_row(row_data)
        else:
            logger.warning(f"[notarised] row invalid {self.block_datetime} {self.txid} {self.season} {self.server} {self.epoch} | {self.scored} {self.score_value} {self.coin}")
            logger.warning(f"{row_data}")

    def delete(self):
        CURSOR.execute(f"DELETE FROM notarised WHERE txid = '{self.txid}';")
        CONN.commit()


class notarised_coin_daily_row():
    def __init__(self, season='', server='', coin='',
                 ntx_count='', notarised_date=''):
        self.season = season
        self.server = server
        self.coin = coin
        self.ntx_count = ntx_count
        self.notarised_date = notarised_date

    def validated(self):
        return True

    def update(self):
        if season == "Unofficial":
            logger.info(f"[notarised_coin_daily_row] {coin} season unofficial?")
        self.server = lib_validate.get_dpow_coin_server(self.season, self.coin)

        self.server, self.coin = lib_validate.handle_dual_server_coins(
            self.server, self.coin
        )
        row_data = (self.season, self.server, self.coin,
                    self.ntx_count, self.notarised_date
        )
        if self.validated():
            logger.info(f"Updating [notarised_coin_daily] {self.coin} {self.notarised_date}")
            update_daily_notarised_coin_row(row_data)
        else:
            logger.warning(f"[notarised_coin_daily] Row data invalid!")
            logger.warning(f"{row_data}")

    def delete(self):
        sql = f"DELETE FROM notarised_coin_daily \
                WHERE coin = '{self.coin}' \
                AND notarised_date = '{self.notarised_date}';"
        CURSOR.execute(sql)
        CONN.commit()


class notarised_count_daily_row():
    def __init__(self, notary='', master_server_count='', main_server_count='', 
        third_party_server_count='', other_server_count='', 
        total_ntx_count='', coin_ntx_counts='', 
        coin_ntx_pct='', timestamp=int(time.time()),
        season='', notarised_date=''):
        self.notary = notary
        self.master_server_count = master_server_count
        self.main_server_count = main_server_count
        self.third_party_server_count = third_party_server_count
        self.other_server_count = other_server_count
        self.total_ntx_count = total_ntx_count
        self.coin_ntx_counts = coin_ntx_counts
        self.coin_ntx_pct = coin_ntx_pct
        self.timestamp = timestamp
        self.season = season
        self.notarised_date = notarised_date

    def validated(self):
        return True

    def update(self):
        row_data = (self.notary, self.master_server_count, self.main_server_count,
                    self.third_party_server_count, self.other_server_count, 
                    self.total_ntx_count, self.coin_ntx_counts, 
                    self.coin_ntx_pct, self.timestamp, self.season,
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

       
class coin_ntx_season_row():
    def __init__(self, season='', coin='', coin_data='{}',
                 timestamp=int(time.time())):
        self.season = season
        self.coin = coin
        self.coin_data = coin_data
        self.timestamp = timestamp

    def validated(self):
        valid_coins = helper.get_season_coins(self.season)
        for i in [self.season, self.coin]:
            if i == '':
                return False
        if self.coin not in valid_coins:
            logger.warning(f"{self.coin} not in {valid_coins}!")
            return False
        return True

    def update(self):
        row_data = (self.season, self.coin, self.coin_data, self.timestamp)
        if self.validated():
            logger.info(f"Updating [coin_ntx_season_row] {self.coin} {self.season}")
            update_coin_ntx_season_row(row_data)
        else:
            logger.warning(f"[coin_ntx_season_row] Row data invalid! {self.coin} {self.season}")
            #logger.warning(f"{row_data}")

    def delete(self, season, coin=None):
        sql = f"DELETE FROM coin_ntx_season"
        sql = filters.simple_filter(sql, season=season, coin=coin)
        CURSOR.execute(sql)
        CONN.commit()
        logger.warning(f"[coin_ntx_season] {season} {coin} deleted")

       
class notary_ntx_season_row():
    def __init__(self, season='', notary='', notary_data='{}',
                 timestamp=int(time.time())):
        self.season = season
        self.notary = notary
        self.notary_data = notary_data
        self.timestamp = timestamp

    def validated(self):
        for i in [self.season, self.notary]:
            if i == '':
                return False
        valid_notaries = helper.get_season_notaries(self.season)
        if self.notary not in valid_notaries:
            logger.warning(f"{self.notary} not in {valid_notaries}!")
            return False
        return True

    def update(self):
        row_data = (self.season, self.notary, self.notary_data, self.timestamp)
        if self.validated():
            logger.info(f"Updating [notary_ntx_season] {self.notary} {self.season}")
            update_notary_ntx_season_row(row_data)
        else:
            logger.warning(f"[notary_ntx_season] Row data invalid! {self.notary} {self.season}")
            #logger.warning(f"{row_data}")

    def delete(self, season, notary=None):
        sql = f"DELETE FROM notary_ntx_season"
        sql = filters.simple_filter(sql, season=season, notary=notary)
        CURSOR.execute(sql)
        CONN.commit()
        logger.warning(f"[notary_ntx_season] {season} {notary} deleted")

       
class server_ntx_season_row():
    def __init__(self, season='', server='', server_data='{}',
                 timestamp=int(time.time())):
        self.season = season
        self.server = server
        self.server_data = server_data
        self.timestamp = timestamp
        


    def validated(self):
        for i in [self.season, self.server]:
            if i == '':
                return False
        valid_servers = list(set(helper.get_season_servers(self.season)).difference({"Unofficial", "LTC", "BTC"}))
        if self.server not in valid_servers:
            logger.warning(f"{self.server} not in {valid_servers}!")
            return False
        return True

    def update(self):
        row_data = (self.season, self.server, self.server_data, self.timestamp)
        if self.validated():
            logger.info(f"Updating [server_ntx_season] {self.server} {self.season}")
            update_server_ntx_season_row(row_data)
        else:
            logger.warning(f"[server_ntx_season] Row data invalid! {self.server} {self.season}")
            #logger.warning(f"{row_data}")

    def delete(self, season, server=None):
        sql = f"DELETE FROM server_ntx_season"
        sql = filters.simple_filter(sql, season=season, server=server)
        CURSOR.execute(sql)
        CONN.commit()
        logger.warning(f"[server_ntx_season] {season} {server} deleted")


class coin_last_ntx_row():
    def __init__(self, season='', server='', coin='',
                 notaries='', opret='', kmd_ntx_blockhash='',
                 kmd_ntx_blockheight='', kmd_ntx_blocktime='',
                 kmd_ntx_txid='', ac_ntx_blockhash='',
                 ac_ntx_height=''):
        self.season = season
        self.server = server
        self.coin = coin
        self.notaries = notaries
        self.opret = opret
        self.kmd_ntx_blockhash = kmd_ntx_blockhash
        self.kmd_ntx_blockheight = kmd_ntx_blockheight
        self.kmd_ntx_blocktime = kmd_ntx_blocktime
        self.kmd_ntx_txid = kmd_ntx_txid
        self.ac_ntx_blockhash =  ac_ntx_blockhash
        self.ac_ntx_height =  ac_ntx_height

    def validated(self):
        return True

    def update(self):

        self.server = lib_validate.get_dpow_coin_server(self.season, self.coin)
        self.server, self.coin = lib_validate.handle_dual_server_coins(self.server, self.coin)
        row_data = (self.season, self.server, self.coin,\
                     self.notaries, self.opret, self.kmd_ntx_blockhash,\
                     self.kmd_ntx_blockheight, self.kmd_ntx_blocktime,\
                     self.kmd_ntx_txid, self.ac_ntx_blockhash,\
                     self.ac_ntx_height)
        if self.validated():
            msg = f"{self.season} {self.server} {self.coin} "
            logger.info(f"Updating [coin_last_ntx] {msg}")
            update_coin_last_ntx_row(row_data)
        else:
            logger.warning(f"[coin_last_ntx] Row data invalid!")
            logger.warning(f"{row_data}")

    def delete(self):
        sql = f"DELETE FROM coin_last_ntx \
                WHERE coin = '{self.coin}' \
                AND season = '{self.season}';"
        CURSOR.execute(sql)
        CONN.commit()

      
class notary_last_ntx_row():
    def __init__(self, season='', server="N/A", coin='', notary='',
                 notaries='[]', opret="N/A", kmd_ntx_blockhash="N/A",
                 kmd_ntx_blockheight=0, kmd_ntx_blocktime=0,
                 kmd_ntx_txid="N/A", ac_ntx_blockhash="N/A",
                 ac_ntx_height=0, ntx_count=0):
        self.season = season
        self.server = server
        self.coin = coin
        self.notary = notary
        self.notaries = notaries
        self.opret = opret
        self.kmd_ntx_blockhash = kmd_ntx_blockhash
        self.kmd_ntx_blockheight = kmd_ntx_blockheight
        self.kmd_ntx_blocktime = kmd_ntx_blocktime
        self.kmd_ntx_txid = kmd_ntx_txid
        self.ac_ntx_blockhash =  ac_ntx_blockhash
        self.ac_ntx_height =  ac_ntx_height

    def validated(self):
        for i in [self.notary, self.coin, self.season]:
            if i == "":
                logger.warning(f"{i} has no value for [notary_last_ntx_row]")
                return False
        if "Unofficial" in [self.season, self.server]:
            logger.warning(f"Ignoring unofficial [notary_last_ntx_row]")
            return False
        return True

    def update(self):
        self.server = lib_validate.get_dpow_coin_server(self.season, self.coin)
        self.server, self.coin = lib_validate.handle_dual_server_coins(self.server, self.coin)
        row_data = (self.season, self.server, self.coin, self.notary,\
                     self.notaries, self.opret, self.kmd_ntx_blockhash,\
                     self.kmd_ntx_blockheight, self.kmd_ntx_blocktime,\
                     self.kmd_ntx_txid, self.ac_ntx_blockhash,\
                     self.ac_ntx_height)
        if self.validated():
            logger.info(f"[notary_last_ntx] Updating {self.season} {self.notary} {self.coin} [{self.kmd_ntx_blockheight}] {self.kmd_ntx_txid}")
            update_notary_last_ntx_row(row_data)
        else:
            logger.warning(f"[notary_last_ntx] Row data invalid!")
            logger.warning(f"{row_data}")

    def delete(self):
        logger.warning(f"[notary_last_ntx_row] DELETING {self.season} \
            {self.server} {self.notary} {self.coin}")
        sql = f"DELETE FROM notary_last_ntx"

        conditions = []
        if self.season:
            conditions.append(f"season = '{self.season}'")
        if self.server:
            conditions.append(f"server = '{self.server}'")
        if self.notary:
            conditions.append(f"notary = '{self.notary}'")
        if self.coin:
            conditions.append(f"coin = '{self.coin}'")
        if len(conditions) > 0:
            sql += " WHERE "
            sql += " AND ".join(conditions)    
        sql += ";"

        CURSOR.execute(sql)
        CONN.commit()


class notary_candidates_row():
    def __init__(self='', year='', season='', name='', proposal_url=''):
        self.name = name
        self.year = year
        self.season = season
        self.proposal_url = proposal_url

    def validated(self):
        return True

    def update(self):
        row_data = (self.year, self.season, self.name, self.proposal_url)
        update_notary_candidates_row(row_data)

    def delete(self):
        pass

        
class ntx_tenure_row():
    def __init__(self, coin='', first_ntx_block='', 
            last_ntx_block='', first_ntx_block_time='',
            last_ntx_block_time='',official_start_block_time='',
            official_end_block_time='', unscored_ntx_count='',
            scored_ntx_count='', season='', server=''):
        self.coin = coin
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

        if self.season not in ['Season_5', 'Season_5_Testnet', 'Season_4', 'Season_6', 'Season_7']:
            logger.warning(f"[notarised_tenure] Invalid season {season}")
            
            return False
        return True

    def update(self):
        # TODO: Validation start / end within season window
        self.server, self.coin = lib_validate.handle_dual_server_coins(self.server, self.coin)

        if self.coin in ["KMD" ,"LTC", "BTC"]:
            self.server = self.coin

        if self.coin in ["LTC", "BTC"]:
            self.unscored_ntx_count = self.unscored_ntx_count \
                                    + self.scored_ntx_count
            self.scored_ntx_count = 0

        row_data = (self.coin, self.first_ntx_block, 
                    self.last_ntx_block, self.first_ntx_block_time,
                    self.last_ntx_block_time, self.official_start_block_time, 
                    self.official_end_block_time, self.unscored_ntx_count, 
                    self.scored_ntx_count, self.season, self.server)

        if self.validated():
            logger.info(f">>> Updating [notarised_tenure] {self.season} {self.server} {self.coin} | {self.scored_ntx_count} scored | {self.unscored_ntx_count} unscored")
            update_notarised_tenure_row(row_data)

        else:
            logger.warning(f"Invalid row [notarised_tenure] {self.coin} \
                             {self.season} | {self.server} | \
                             {self.scored_ntx_count} scored | \
                             {self.unscored_ntx_count} unscored")
            logger.warning(f"{row_data}")

    def delete(self, season=None, server=None, coin=None):
        if not season and not server and not coin:
            logger.error("Not deleting, need to specify at \
                          least one of coin, season or server")
        else:
            sql = f"DELETE FROM notarised_tenure"
            conditions = []
            if season:
                conditions.append(f"season = '{season}'")
            if server:
                conditions.append(f"server = '{server}'")
            if coin:
                conditions.append(f"coin = '{coin}'")

            if len(conditions) > 0:
                sql += " WHERE "
                sql += " AND ".join(conditions)    
            sql += ";"
            logger.warning(f"Deleting [notarised_tenure] row: {sql}")

            CURSOR.execute(sql)
            CONN.commit()


class notary_vote_row():
    def __init__(self, txid='', block_hash='', block_time=0, \
            lock_time=0, block_height=0, votes=0, candidate='', 
            candidate_address='', mined_by='', difficulty='',\
            notes='', year='', valid=True):
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
        self.year = year
        self.valid = valid

    def validated(self):
        for i in [self.block_time, self.lock_time, self.block_time,
                  self.votes]:
            if i in [0, None]:
                return False

        for i in [self.txid, self.block_hash, self.candidate,
                  self.candidate_address]:
            if i in ['', None]:
                return False

        if self.candidate_address not in CANDIDATE_ADDRESSES[self.year]:
            return False

        if self.candidate.find("_") == -1:
            return False

        return True

    def update(self):
        logger.info(f"Updating votes for {self.candidate}")
        if self.lock_time == 0:
            self.lock_time = self.block_time
        row_data = (self.txid, self.block_hash, self.block_time, \
                    self.lock_time, self.block_height, self.votes, \
                    self.candidate, self.candidate_address, self.mined_by,
                    self.difficulty, self.notes, self.year, self.valid)
        if self.validated():
            logger.info(f"Updating [notary_vote_row] {self.txid} | \
                          {self.block_height} | {self.candidate} | \
                          {self.votes} | {self.valid} | {self.notes}") 
            update_notary_vote_row(row_data)
        else:
            logger.warning(f"[notary_vote_row] Row data invalid!")
            logger.warning(f"{row_data}")

    def delete_txid(self):
        sql = f"DELETE FROM [notary_vote_row] WHERE txid = '{self.txid}';"
        CURSOR.execute(sql)
        CONN.commit()


class scoring_epoch_row():
    def __init__(self, season='', server='', epoch='',epoch_start=0,
                 epoch_end=0, start_event='', end_event='',
                 epoch_coins=list, score_per_ntx=0):
        self.season = season
        self.server = server
        self.epoch = epoch
        self.epoch_start = epoch_start
        self.epoch_end = epoch_end
        self.start_event = start_event
        self.end_event = end_event
        self.epoch_coins = epoch_coins
        self.score_per_ntx = score_per_ntx

    def validated(self):
        if self.season in EXCLUDED_SEASONS:
            logger.warning(f"{self.season} in EXCLUDED_SEASONS")
            return False
        if self.server in EXCLUDED_SERVERS:
            logger.warning(f"{self.server} in EXCLUDED_SERVERS")
            return False
        epoch_coins_validated = lib_validate.validate_epoch_coins(
                                        self.epoch_coins, self.season)
        return epoch_coins_validated

    def update(self):

        if self.season.find("Testnet") > -1:
            self.server == "Main"

        if len(self.epoch_coins) == 0:
            self.epoch_coins = [None]

        row_data = (self.season, self.server, self.epoch, self.epoch_start, \
                    self.epoch_end, self.start_event, self.end_event, \
                    self.epoch_coins, self.score_per_ntx)

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


######### AtomicDEX Related ##########
class swaps_row():
    def __init__(self, uuid='', started_at='', taker_coin='', 
                 taker_amount=0, taker_gui='', taker_version='',
                 taker_pubkey='', maker_coin='', maker_amount=0,
                 maker_gui='', maker_version='', maker_pubkey='', timestamp=''):
        self.uuid = uuid
        self.started_at = started_at
        self.taker_coin = lib_validate.override_ticker(taker_coin)
        self.taker_amount = taker_amount
        self.taker_gui = taker_gui
        self.taker_version = taker_version
        self.taker_pubkey = taker_pubkey
        self.maker_coin = lib_validate.override_ticker(taker_coin)
        self.maker_amount = maker_amount
        self.maker_gui = maker_gui
        self.maker_version = maker_version
        self.maker_pubkey = maker_pubkey
        self.timestamp = timestamp

    def validated(self):
        return True

    def update(self):
        row_data = (self.uuid, self.started_at, self.taker_coin,
                    self.taker_amount, self.taker_gui, self.taker_version,
                    self.taker_pubkey, self.maker_coin, self.maker_amount,
                    self.maker_gui, self.maker_version, self.maker_pubkey, self.timestamp)
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
                 maker_pubkey='', timestamp=''):
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
        self.timestamp = timestamp

    def validated(self):
        return True

    def update(self):
        row_data = (self.uuid, self.started_at, self.taker_coin,
                    self.taker_amount, self.taker_error_type, self.taker_error_msg,
                    self.taker_gui, self.taker_version, self.taker_pubkey,
                    self.maker_coin, self.maker_amount,
                    self.maker_error_type, self.maker_error_msg,
                    self.maker_gui, self.maker_version, self.maker_pubkey, self.timestamp)
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


######### Mining Related #########

class mined_row():
    def __init__(self, block_height='', block_time='', block_datetime='', 
             value='', address='', name='', txid='', diff=0, season='',
             btc_price=0, usd_price=0, category=''):
        self.block_height = block_height
        self.block_time = block_time
        self.block_datetime = block_datetime
        self.value = value
        self.address = address
        self.name = name
        self.txid = txid
        self.diff = diff
        self.season = season
        self.btc_price = btc_price
        self.usd_price = usd_price
        self.category = category

    def validated(self):
        for item in [self.address, self.name, self.season]:
            if item == '':
                logger.warning(f"No value for {item}!")
                return False

        if self.season in SEASONS_INFO:
            if self.name in SEASONS_INFO[self.season]["notaries"]:
                if self.address not in SEASONS_INFO[self.season]["servers"]["Main"]["addresses"]["KMD"]:
                    logger.warning(f'{self.address} not in SEASONS_INFO[self.season]["servers"]["Main"]["addresses"]["KMD"]')
                    for season in SEASONS_INFO:
                        if season.find("Testnet") == -1:
                            if "Main" in SEASONS_INFO[season]["servers"]:
                                if self.address in SEASONS_INFO[season]["servers"]["Main"]["addresses"]["KMD"]:
                                    self.season = season
                                    return True
        return True

    def update(self):
        self.season = lib_validate.get_season(self.block_time)
        self.name = lib_validate.get_name_from_address(self.address)
        self.category = lib_validate.get_category_from_name(self.name)
        self.block_datetime = dt.utcfromtimestamp(self.block_time)
        row_data = (
            self.block_height, self.block_time, self.block_datetime, 
            self.value, self.address, self.name, self.txid, self.diff,
            self.season, self.btc_price, self.usd_price, self.category
        )

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
                 timestamp=int(time.time())):
        self.name = name
        self.season = season
        self.address = address
        self.blocks_mined = blocks_mined
        self.sum_value_mined = sum_value_mined
        self.max_value_mined = max_value_mined
        self.max_value_txid = max_value_txid
        self.last_mined_blocktime = last_mined_blocktime
        self.last_mined_block = last_mined_block
        self.timestamp = timestamp

    def validated(self):
        for item in [self.address, self.name, self.season]:
            if item == '':
                logger.warning(f"No value for {item}!")
                return False

        

        if self.name in SEASONS_INFO[self.season]["notaries"]:
            if self.address != SEASONS_INFO[self.season]["servers"]["Main"]["addresses"]["KMD"]:
                logger.warning(f'{self.address} not in SEASONS_INFO[self.season]["servers"]["Main"]["addresses"]["KMD"]')
                for season in SEASONS_INFO:
                    if season.find("Testnet") == -1:
                        
                        if "Main" in SEASONS_INFO[season]["servers"]:
                            if self.address == SEASONS_INFO[season]["servers"]["Main"]["addresses"]["KMD"]:
                                self.season = season
                                return True
                return False
        return True

    def update(self):
        self.name = lib_validate.get_name_from_address(self.address)

        row_data = (self.name, self.season, self.address, self.blocks_mined, 
            self.sum_value_mined, self.max_value_mined, self.max_value_txid,
            self.last_mined_blocktime, self.last_mined_block, self.timestamp) 

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
            btc_price=0, usd_price=0, mined_date='', timestamp=int(time.time()),
            ):
        self.notary = notary
        self.blocks_mined = blocks_mined
        self.sum_value_mined = sum_value_mined
        self.mined_date = mined_date
        self.btc_price = btc_price
        self.usd_price = usd_price
        self.timestamp = timestamp

    def validated(self):
        for item in [self.notary, self.mined_date]:
            if item == '':
                logger.warning(f"No value for {item}!")
                return False
        return True

    def update(self):
        row_data = (self.notary, self.blocks_mined, self.sum_value_mined, \
                    self.mined_date, self.btc_price, self.usd_price, self.timestamp)
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


######### Other ##########
class rewards_tx_row():
    def __init__(self, txid='', block_hash='', block_height=0, block_time=0,
                 block_datetime='', sum_of_inputs=0, address='',
                 sum_of_outputs=0, btc_price=0, usd_price=0, rewards_value=0):
        self.txid = txid
        self.block_hash = block_hash
        self.block_height = block_height
        self.block_time = block_time
        self.block_datetime = block_datetime
        self.sum_of_inputs = sum_of_inputs
        self.sum_of_outputs = sum_of_outputs
        self.address = address
        self.rewards_value = rewards_value
        self.btc_price = btc_price
        self.usd_price = usd_price


    def validated(self):
        row_list = [self.txid, self.block_hash, self.block_height,
                  self.block_time, self.block_datetime,
                  self.sum_of_inputs, self.sum_of_outputs, self.address,
                  self.rewards_value, self.btc_price, self.usd_price]
        for i in row_list:
            if i == '':
                logger.warning(f"Row list index {row_list.index(i)} is empty!")

                return False
        return True

    def update(self):

        self.block_datetime = dt.utcfromtimestamp(self.block_time)
        row_data = (self.txid, self.block_hash, self.block_height,
                    self.block_time, self.block_datetime,
                    self.address, self.rewards_value,
                    self.sum_of_inputs, self.sum_of_outputs,
                    self.btc_price, self.usd_price)
        if self.validated():
            update_rewards_tx_row(row_data)
            logger.info(f"{self.txid} {self.block_height} {self.address} {self.rewards_value}")
        else:
            logger.warning("[rewards_tx] Row data invalid!")
            logger.warning(row_data)

    def delete(self):
        delete_rewards_tx_transaction(self.txid)
