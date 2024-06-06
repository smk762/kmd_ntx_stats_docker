#!/usr/bin/env python3
import pytest
import math
from lib_const import *
import lib_api
import lib_coins
import lib_const
import lib_crypto
import lib_db
import lib_dpow_const
import lib_electrum
import lib_epochs
import lib_github
import lib_helper
import lib_mining
import lib_ntx
import lib_query
import lib_rpc
import lib_urls
import lib_validate
import lib_wallet


# TODO: For CI, these tests need to be separated.
# - No data in actions, so get from urls while testing them
# Test non-query functions separately.
# Test adding to db (limit use of external api)

pubkey = "0366a87a476a09e05560c5aae0e44d2ab9ba56e69701cee24307871ddd37c86258"

explorers_data = lib_github.get_github_folder_contents("KomodoPlatform", "coins", "explorers")
explorers = {}
for item in explorers_data:
    explorers.update({item["name"]:item["download_url"]})

electrums_data = lib_github.get_github_folder_contents("KomodoPlatform", "coins", "electrums")
electrums = {}
for item in electrums_data:
    electrums.update({item["name"]:item["download_url"]})

icons_data = lib_github.get_github_folder_contents("KomodoPlatform", "coins", "icons")
icons = {}
for item in icons_data:
    icons.update({item["name"]:item["download_url"]})

class TestLibApi:
    def test_get_ac_block_info(self):
        assert "KMD" in lib_api.get_ac_block_info()

    def test_get_btc_address_txids(self):
        assert "err" not in lib_api.get_btc_address_txids("1CgahRzTHP4f86WUGZykRH8f2ZAB8J9VFr")

    def test_get_btc_tx_info(self):
        assert "err" not in lib_api.get_btc_tx_info("a6d699afddd8a3c810793b182d3e628a2faddf149efc752c2eaf10ac11179e59")

    def test_get_btc_block_info(self):
        assert "err" not in lib_api.get_btc_block_info(729124)

    def test_get_dexstats_balance(self):
        assert lib_api.get_dexstats_balance("KMD", "RDragoNHdwovvsDLSLMiAEzEArAD3kq6FN") > 0

    def test_get_ltc_address_txids(self):
        assert "err" not in lib_api.get_ltc_address_txids("LYuyDfy3U2ao6qboQhuGCvJKsJTiFRcHN1")

    def test_get_ltc_tx_info(self):
        assert "err" not in lib_api.get_ltc_tx_info("67e1b5e774c683a46753f466cdd34c012023750e47f55503227110accc50d398")

    def test_get_ltc_block_info(self):
        assert "err" not in lib_api.get_ltc_block_info(2234494)


class TestLibCoins:

    def test_get_assetchain_conf_path(self):
        assert lib_coins.get_assetchain_conf_path("DEX") == "~/.komodo/DEX/DEX.conf"

    def test_get_assetchain_cli(self):
        assert lib_coins.get_assetchain_cli("DEX") == "~/komodo/src/komodo-cli -ac_name=DEX"

    def test_get_coins_repo_electrums(self):
        coins_data = lib_coins.get_coins_repo_electrums(electrums, {"KMD": {"electrums":[], "electrums_ssl":[], }})
        assert coins_data["KMD"]["electrums_ssl"] == [
            "electrum1.cipig.net:20001",
            "electrum2.cipig.net:20001",
            "electrum3.cipig.net:20001"
        ]
        assert coins_data["KMD"]["electrums"] == [
            "electrum1.cipig.net:10001",
            "electrum2.cipig.net:10001",
            "electrum3.cipig.net:10001"
        ]
        assert coins_data["KMD"]["electrums_wss"] == [
            "electrum1.cipig.net:30001",
            "electrum2.cipig.net:30001",
            "electrum3.cipig.net:30001"
        ]
        assert lib_coins.get_coins_repo_electrums(electrums, {
            "TOKEL": {
                "coins_info": {},
                "dpow": {},
                "dpow_tenure": {},
                "dpow_active": 0,
                "electrums": [],
                "electrums_ssl": [],
                "electrums_wss": [],
                "explorers": [],
                "mm2_compatible": 0
            }
        }) == {
            "TOKEL": {
                "coins_info": {},
                "dpow": {},
                "dpow_tenure": {},
                "dpow_active": 0,
                "electrums": [
                    "1.eu.tokel.electrum.dexstats.info:10077",
                    "2.eu.tokel.electrum.dexstats.info:10077"
                ],
                "electrums_ssl": [],
                "electrums_wss": [],
                "explorers": [],
                "mm2_compatible": 0
            }
        }
        assert lib_coins.get_coins_repo_electrums(electrums, {
            "PIRATE": {
                "coins_info": {},
                "dpow": {},
                "dpow_tenure": {},
                "dpow_active": 0,
                "electrums": [],
                "electrums_ssl": [],
                "explorers": [],
                "mm2_compatible": 0
            }
        }) == {
            "PIRATE": {
                "coins_info": {},
                "dpow": {},
                "dpow_tenure": {},
                "dpow_active": 0,
                "electrums": [],
                "electrums_ssl": [],
                "explorers": [],
                "mm2_compatible": 0
            }
        }
        assert lib_coins.get_coins_repo_electrums(electrums, {
            "KMD": {
                "coins_info": {},
                "dpow": {},
                "dpow_tenure": {},
                "dpow_active": 0,
                "electrums": [],
                "electrums_ssl": [],
                "explorers": [],
                "mm2_compatible": 0
            }
        }) == {
            "KMD": {
                "coins_info": {},
                "dpow": {},
                "dpow_tenure": {},
                "dpow_active": 0,
                "electrums": [
                    "electrum1.cipig.net:10001",
                    "electrum2.cipig.net:10001",
                    "electrum3.cipig.net:10001"
                ],
                "electrums_ssl": [
                    "electrum1.cipig.net:20001",
                    "electrum2.cipig.net:20001",
                    "electrum3.cipig.net:20001"
                ],
                "explorers": [],
                "mm2_compatible": 0
            }
        }

    def test_get_coins_repo_explorers(self):
        coins_data = lib_coins.get_coins_repo_explorers(explorers, {"KMD": {"explorers":[]}})
        assert "https://kmd.explorer.dexstats.info/" in coins_data["KMD"]["explorers"]
        assert lib_coins.get_coins_repo_explorers(explorers, {
            "TOKEL": {
                "coins_info": {},
                "dpow": {},
                "dpow_tenure": {},
                "dpow_active": 0,
                "electrums": [],
                "electrums_ssl": [],
                "explorers": [],
                "mm2_compatible": 0
            }
        }) == {
            "TOKEL": {
                "coins_info": {},
                "dpow": {},
                "dpow_tenure": {},
                "dpow_active": 0,
                "electrums": [],
                "electrums_ssl": [],
                "explorers": [
                    "https://explorer.tokel.io/",
                    "https://tokel.explorer.dexstats.info/"
                ],
                "mm2_compatible": 0
            }
        }
        assert lib_coins.get_coins_repo_explorers(explorers, {
            "PIRATE": {
                "coins_info": {},
                "dpow": {},
                "dpow_tenure": {},
                "dpow_active": 0,
                "electrums": [],
                "electrums_ssl": [],
                "explorers": [],
                "mm2_compatible": 0
            }
        }) == {
            "PIRATE": {
                "coins_info": {},
                "dpow": {},
                "dpow_tenure": {},
                "dpow_active": 0,
                "electrums": [],
                "electrums_ssl": [],
                "explorers": [
                    "https://pirate.kmdexplorer.io/",
                    "https://pirate.explorer.dexstats.info/"
                ],
                "mm2_compatible": 0
            }
        }
        assert lib_coins.get_coins_repo_explorers(explorers, {
            "KMD": {
                "coins_info": {},
                "dpow": {},
                "dpow_tenure": {},
                "dpow_active": 0,
                "electrums": [],
                "electrums_ssl": [],
                "explorers": [],
                "mm2_compatible": 0
            }
        }) == {
            "KMD": {
                "coins_info": {},
                "dpow": {},
                "dpow_tenure": {},
                "dpow_active": 0,
                "electrums": [],
                "electrums_ssl": [],
                "explorers": [
                    "https://kmdexplorer.io/",
                    "https://kmd.explorer.dexstats.info/",
                    "https://komodod.com/",
                    "https://www.kmdexplorer.ru/"
                ],
                "mm2_compatible": 0
            }
        }

    def test_get_coins_repo_icons(self):
        coins_data = lib_coins.get_coins_repo_icons(icons, {"KMD": {"coins_info":{}}})
        assert coins_data["KMD"]["coins_info"]["icon"] == "https://raw.githubusercontent.com/KomodoPlatform/coins/master/icons/kmd.png"
        assert lib_coins.get_coins_repo_icons(icons, {
            "TOKEL": {
                "coins_info": {},
                "dpow": {},
                "dpow_tenure": {},
                "dpow_active": 0,
                "electrums": [],
                "electrums_ssl": [],
                "explorers": [],
                "mm2_compatible": 0
            }
        }) == {
            "TOKEL": {
                "coins_info": {
                    "icon": "https://raw.githubusercontent.com/KomodoPlatform/coins/master/icons/tkl.png"
                },
                "dpow": {},
                "dpow_tenure": {},
                "dpow_active": 0,
                "electrums": [],
                "electrums_ssl": [],
                "explorers": [],
                "mm2_compatible": 0
            }
        }
        assert lib_coins.get_coins_repo_icons(icons, {
            "PIRATE": {
                "coins_info": {},
                "dpow": {},
                "dpow_tenure": {},
                "dpow_active": 0,
                "electrums": [],
                "electrums_ssl": [],
                "explorers": [],
                "mm2_compatible": 0
            }
        }) == {
            "PIRATE": {
                "coins_info": {
                    "icon": "https://raw.githubusercontent.com/KomodoPlatform/coins/master/icons/arrr.png"
                },
                "dpow": {},
                "dpow_tenure": {},
                "dpow_active": 0,
                "electrums": [],
                "electrums_ssl": [],
                "explorers": [],
                "mm2_compatible": 0
            }
        }
        assert lib_coins.get_coins_repo_icons(icons, {
            "KMD": {
                "coins_info": {},
                "dpow": {},
                "dpow_tenure": {},
                "dpow_active": 0,
                "electrums": [],
                "electrums_ssl": [],
                "explorers": [],
                "mm2_compatible": 0
            }
        }) == {
            "KMD": {
                "coins_info": {
                    "icon": "https://raw.githubusercontent.com/KomodoPlatform/coins/master/icons/kmd.png"
                },
                "dpow": {},
                "dpow_tenure": {},
                "dpow_active": 0,
                "electrums": [],
                "electrums_ssl": [],
                "explorers": [],
                "mm2_compatible": 0
            }
        }

    def test_get_dpow_tenure(self):
        coins_data = lib_coins.get_dpow_tenure({"CLC": {"dpow_tenure":{}}})
        assert "Season_5" in coins_data["CLC"]["dpow_tenure"]
        assert "Main" in coins_data["CLC"]["dpow_tenure"]["Season_5"]
        assert "start_time" in coins_data["CLC"]["dpow_tenure"]["Season_5"]["Main"]
        assert "end_time" in coins_data["CLC"]["dpow_tenure"]["Season_5"]["Main"]
        assert coins_data["CLC"]["dpow_tenure"]["Season_5"]["Main"]["start_time"] == 1647207139
        assert coins_data["CLC"]["dpow_tenure"]["Season_5"]["Main"]["end_time"] == 1751328000

    def test_parse_assetchains(self):
        coins_data = lib_coins.parse_assetchains({})
        assert coins_data["DEX"]["coins_info"]["cli"] == "~/komodo/src/komodo-cli -ac_name=DEX"
        assert coins_data["CHIPS"]["coins_info"]["conf_path"] == "~/.chips/chips.conf"
        assert coins_data["CHIPS"]["coins_info"]["launch_params"] == "~/chips/src/chipsd"

    def test_parse_coins_repo(self):
        coins_data = lib_coins.parse_coins_repo()
        assert "KMD" in coins_data
        assert coins_data["KMD"]["coins_info"]["pubtype"] == 60
        assert coins_data["KMD"]["mm2_compatible"] == 1

    def test_parse_electrum_explorer(self):
        coins_data = lib_coins.parse_electrum_explorer({"KMD": {}})
        assert "KMD" in coins_data
        assert coins_data["KMD"]["electrums_wss"] == [
            "electrum1.cipig.net:30001",
            "electrum2.cipig.net:30001",
            "electrum3.cipig.net:30001"
        ]
        assert coins_data["KMD"]["electrums_ssl"] == [
            "electrum1.cipig.net:20001",
            "electrum2.cipig.net:20001",
            "electrum3.cipig.net:20001"
        ]
        assert coins_data["KMD"]["electrums"] == [
            "electrum1.cipig.net:10001",
            "electrum2.cipig.net:10001",
            "electrum3.cipig.net:10001"
        ]
        assert "https://kmd.explorer.dexstats.info/" in coins_data["KMD"]["explorers"]

    def test_pre_populate_coins_data(self):
        coins_data = lib_coins.pre_populate_coins_data({"KMD": {"dpow_active":1}}, "KMD")
        assert coins_data["KMD"]["dpow_active"] == 1
        assert coins_data["KMD"]["mm2_compatible"] == 0
        assert lib_coins.pre_populate_coins_data({}, "DEX") == {
            "DEX": {
                "coins_info": {},
                "dpow": {},
                "dpow_tenure": {},
                "dpow_active": 0,
                "electrums": [],
                "electrums_ssl": [],
                "explorers": [],
                "mm2_compatible": 0
            }
        }


class TestLibCrypto:
    def test_get_addr_from_pubkey(self):
        assert lib_crypto.get_addr_from_pubkey("KMD", "038e010c33c56b61389409eea5597fe17967398731e23185c84c472a16fc5d34ab") == "RDragoNHdwovvsDLSLMiAEzEArAD3kq6FN"
        assert lib_crypto.get_addr_from_pubkey("MIL", "02b3c168ed4acd96594288cee3114c77de51b6afe1ab6a866887a13a96ee80f33c") == "MGRswY9WjB4jALKCrRrvW4KhdtAjif1ztf"

    def test_get_opret_ticker(self):
        assert lib_crypto.get_opret_ticker("6c04e92a03800016c69bc2cd5e818cddbd37f07c999212ae7f97db7d98b6ab00c6891b00484f444c00f1deb2b25d3e69b1ab59236ce5bee41fe1f1fa08fd682be92f6eea6b30f6ed3908000000") == "HODL"

    def test_get_p2pk_scripthash_from_pubkey(self):
        assert lib_crypto.get_p2pk_scripthash_from_pubkey(pubkey) == "a0ecece80abbb1f76e00f034c9ffdf88d8e173c8895945020d27792cadf3aedd"

    def test_get_p2pkh_scripthash_from_pubkey(self):
        assert lib_crypto.get_p2pkh_scripthash_from_pubkey(pubkey) == "71417d476001c7a2c56eb72820d7d84b476aa7061da3f860af1c8c0f3fe20772"

    def test_lil_endian(self):
        assert lib_crypto.lil_endian("deadbeef") == "efbeadde"


class TestLibElectrum:
    def test_get_full_electrum_balance(self):
        assert lib_electrum.get_full_electrum_balance(pubkey, "KMD") > 0

    def test_get_version(self):
        assert 'result' in lib_electrum.get_version("KMD")

    def test_get_notary_utxo_count(self):
        assert isinstance(lib_electrum.get_notary_utxo_count("KMD", pubkey), int)
        assert isinstance(lib_electrum.get_notary_utxo_count("DEX", pubkey), int)


class TestLibEpochs:
    def test_get_ntx_tenure(self):
        tenure = lib_epochs.get_ntx_tenure("Season_5", "Main", "OOT")
        assert tenure.official_start_block_time >= SEASONS_INFO["Season_5"]["servers"]["Main"]["epochs"]["Epoch_0"]["start_time"]
        assert tenure.official_start_block_time <= SEASONS_INFO["Season_5"]["servers"]["Main"]["epochs"]["Epoch_0"]["end_time"]
        tenure = lib_epochs.get_ntx_tenure("Season_5", "Main", "CLC")
        assert tenure.official_start_block_time >= SEASONS_INFO["Season_5"]["servers"]["Main"]["epochs"]["Epoch_2"]["start_time"]
        assert tenure.official_start_block_time <= SEASONS_INFO["Season_5"]["servers"]["Main"]["epochs"]["Epoch_2"]["end_time"]
        tenure = lib_epochs.get_ntx_tenure("Season_5", "Third_Party", "MIL")
        assert tenure.official_start_block_time >= SEASONS_INFO["Season_5"]["servers"]["Third_Party"]["epochs"]["Epoch_4"]["start_time"]
        assert tenure.official_start_block_time <= SEASONS_INFO["Season_5"]["servers"]["Third_Party"]["epochs"]["Epoch_4"]["end_time"]
        tenure = lib_epochs.get_ntx_tenure("Season_5", "Third_Party", "GLEEC-OLD")
        assert tenure.official_start_block_time >= SEASONS_INFO["Season_5"]["servers"]["Third_Party"]["epochs"]["Epoch_0"]["start_time"]
        assert tenure.official_start_block_time <= SEASONS_INFO["Season_5"]["servers"]["Third_Party"]["epochs"]["Epoch_3"]["end_time"]

    def test_get_dpow_scoring_window(self):
        window = lib_epochs.get_dpow_scoring_window("Season_5", "Third_Party", "MIL")
        assert window[0] == SEASONS_INFO["Season_5"]["servers"]["Third_Party"]["epochs"]["Epoch_4"]["start_time"]
        assert window[1] == SEASONS_INFO["Season_5"]["servers"]["Third_Party"]["epochs"]["Epoch_4"]["end_time"]

        window = lib_epochs.get_dpow_scoring_window("Season_5", "Third_Party", "GLEEC-OLD")
        assert window[0] == SEASONS_INFO["Season_5"]["servers"]["Third_Party"]["epochs"]["Epoch_0"]["start_time"]
        assert window[1] == SEASONS_INFO["Season_5"]["servers"]["Third_Party"]["epochs"]["Epoch_2"]["end_time"]


class TestLibHelper:

    def test_safe_div(self):
        assert lib_helper.safe_div(10,2) == 5
        assert lib_helper.safe_div(10,0) == 0

    def test_has_season_started(self):
        assert lib_helper.has_season_started("Season_5") == True
        assert lib_helper.has_season_started("Season_6") == True
        assert lib_helper.has_season_started("Season_12") == False


    def test_handle_translate_coins(self):
        assert lib_helper.handle_translate_coins("GleecBTC") == "GLEEC-OLD"
        assert lib_helper.handle_translate_coins("TKL") == "TOKEL"
        assert lib_helper.handle_translate_coins("ARRR") == "PIRATE"
        assert lib_helper.handle_translate_coins("KMD") == "KMD"

    def test_get_pubkeys(self):
        assert len(lib_helper.get_pubkeys("Season_5", "Third_Party")) == 64
        assert len(lib_helper.get_pubkeys("Season_7", "Main")) == 64
        assert len(lib_helper.get_pubkeys("Season_777", "Main")) == 0
        assert len(lib_helper.get_pubkeys("Season_5", "Minecraft")) == 0

    def test_get_address_from_notary(self):
        assert lib_helper.get_address_from_notary("Season_5", "dragonhound_NA", "LTC") == "LPNLTVnhQasABRUk64VmdyajFjxRCiZvUo"
        assert lib_helper.get_address_from_notary("Season_5", "dragonhound_DEV", "KMD") == "RDragoNHdwovvsDLSLMiAEzEArAD3kq6FN"
        assert lib_helper.get_address_from_notary("Season_5", "mrlynch_AR", "DEX") == "RKytuA1ubrCD66hNNemcsvyDhDbcR2S1sU"

    def test_get_season_notaries(self):
        assert len(lib_helper.get_season_notaries("Season_5")) == 64

    def test_get_dpow_coin_src(self):
        assert lib_helper.get_dpow_coin_src("(https://github.com/chips-blockchain/chips)") == "https://github.com/chips-blockchain/chips"

    def test_get_dpow_coin_server(self):
        assert lib_helper.get_dpow_coin_server("dPoW-3P") == "Third_Party"
        assert lib_helper.get_dpow_coin_server("dPoW-MainNet") == "Main"

    def test_get_assetchain_launch_params(self):
        assert lib_helper.get_assetchain_launch_params({
            "ac_name": "DEX",
            "ac_supply": "999999"
        }) == "~/komodo/src/komodod -ac_name=DEX -ac_supply=999999"
        assert lib_helper.get_assetchain_launch_params({
            "ac_name": "MARTY",
            "ac_supply": "90000000000",
            "ac_reward": "100000000",
            "ac_cc": "3",
            "ac_staked": "10",
            "addnode": ["138.201.136.145", "95.217.44.58"]
        }) == "~/komodo/src/komodod -ac_name=MARTY -ac_supply=90000000000 -ac_reward=100000000 -ac_cc=3 -ac_staked=10 -addnode=138.201.136.145 -addnode=95.217.44.58"

    def test_is_notary_ltc_address(self):
        assert lib_helper.is_notary_ltc_address("LfmssDyX6iZvbVqHv6t9P6JWXia2JG7mdb") == False
        assert lib_helper.is_notary_ltc_address("LPoLsVnq7nFR7fYJ9JMtLjinco4taNqzkU") == True

    def test_get_local_addresses(self):
        url = lib_urls.get_notary_ltc_txid_url("adc04856562fd8d8abfe8487d0d77c26c680cba36400025b1e9235a38ac76a2e")
        local_info = requests.get(url).json()["results"]
        assert lib_helper.get_local_addresses(local_info) == [
            "LfoeX6LsLiSMJnmePRsha3cAQYz8UvdF1Z",
            "LgXKKfeC3sAa1SV413g4NWSTqvrdoks1AS",
            "LTkNqHCnyPuKWaKd5E26ifLBqcY8WADgMd",
            "Lbd5LRYFcVG7T763BY1nt3ar4fmtQEJQvd",
            "LYuyDfy3U2ao6qboQhuGCvJKsJTiFRcHN1",
            "LLHUR4bE87gTAmZjt8Rok8g53ERV9b5W37",
            "LX1JXn6w9DVHzhyNfQqA6aLtZeinU7GNcu",
            "LdhpcCwpeHXSexeVxPzR8CG79fGR6LPuCk",
            "LXXPRB7dCt7JNeW8ZSTdbDc9vopZbDR4AA",
            "LfXYRBP24kCyz4FSKukpA1TyvsUwx2kuEH",
            "LNDiYrSVmZDowQX4Pd7N1SuSVtFLGCqeyP",
            "LPNLTVnhQasABRUk64VmdyajFjxRCiZvUo",
            "LNzt9wDhYKiLue4cRJdXfpXTg4roPU6hd6"
        ]
        url = lib_urls.get_notary_ltc_txid_url("deadbeef")
        local_info = requests.get(url).json()["results"]
        assert lib_helper.get_local_addresses(local_info) == []


class TestLibMining:
    def test_get_mined_row(self):
        row = lib_mining.get_mined_row(2824869)
        assert row.block_height == 2824869
        assert row.block_time == 1647487930
        assert row.address == "RKytuA1ubrCD66hNNemcsvyDhDbcR2S1sU"
        assert row.txid == "8202597ca6a07d5f03d6bcfe37c102d14ecaa7860815279e3d0f0efd6173d40b"
        assert row.diff == 197318030.6073029
        assert row.value == 3.00005000


class TestLibNtx:
    def test_get_notarised_data(self):
        expected = ('HODL', 1939649, 1593250479, datetime.datetime(2020, 6, 27, 9, 34, 39),
                    '0ddce76cc7c3d63254e81f1f1d76912734537ea0cfe71a125e1766ba73075cfb',\
                    ['chmex_AR', 'decker_AR', 'decker_EU', 'etszombi_AR', 'fullmoon_NA', 'madmax_NA',\
                    'mihailo_EU', 'mrlynch_AR', 'node9_EU', 'peer2cloud_AR', 'phba2061_EU', 'pirate_NA',\
                    'titomane_SH'],
                    ['RLKHdM3qeTqFEiSXyUbQuWcmDmvGStefqX', 'RPHbA2o61qxMcJojBpXHeJ9QFFUV32A4KD',
                    'RFovZtwXCjAE8fAtB6xULQype7BVCQsxd1', 'RSKDECKERyuopK3gd3SQHH9qkngsfWrjXy',
                    'RMadNAGn63C3EsBJzn3UT1XfsWdSnwCDqp', 'RPJrNnXwNjmppCTZSpkxEyr4eQvszJwyqG',
                    'RHw84GCY3AiqDmWd8AsGQAGZcttcoB9F19', 'RC9VUfpU7WwSwj4Uwr9hJHhi4rdkspDPn6',
                    'RCkkWuQRW8eXinaHZjPPbS4q69iVPwKqQQ', 'RX1DiFJTrz86jEVJh4JzDJeVz9DQRxWPjG',
                    'RNFTgUWvx8zUsdVL56uuffiKXZTU4q45cr', 'RKytuA1ubrCD66hNNemcsvyDhDbcR2S1sU',
                    'RS4S9b9aG1yfeXFoBj2NcPoBE21XKfJDgc'],\
                    '020e7b611131fa2cc99a31878583f2b1a6a2a25bf1adcec024212a3202027aab', 957854,\
                    '2e8732b608a37b47307a67abce11922db968435552f2ea6ad0b5b4fda82123d5',\
                    'OP_RETURN ab7a0202322a2124c0ceadf15ba2a2a6b1f2838587319ac92cfa3111617b0e029e9d0e00484f444c00e1956043b84a6fe3c8db130ab43d75d26d84b1e681de90e4f3a2b57676cf1b510c000000',\
                    'N/A')

        actual = lib_ntx.get_notarised_data("2e8732b608a37b47307a67abce11922db968435552f2ea6ad0b5b4fda82123d5")
        assert actual == expected

    def test_get_season_ntx_dict(season):
        season_ntx_dict = lib_ntx.get_season_ntx_dict("Season_5")
        season_count = season_ntx_dict["season_ntx_count"]
        season_score = season_ntx_dict["season_ntx_score"]
        assert len(season_ntx_dict["notaries"]) == 64

        sum_count = 0
        sum_score = 0
        sum_count_pct = 0
        sum_score_pct = 0
        for notary in season_ntx_dict["notaries"]:
            sum_count += season_ntx_dict["notaries"][notary]["notary_ntx_count"]
            sum_score += season_ntx_dict["notaries"][notary]["notary_ntx_score"]
            sum_count_pct += season_ntx_dict["notaries"][notary]["notary_ntx_count_pct"]
            sum_score_pct += season_ntx_dict["notaries"][notary]["notary_ntx_score_pct"]
        assert round(season_count, 4) == round(sum_count,4)
        assert round(season_score, 4) == round(sum_score, 4)
        assert round(sum_count_pct) == 1300
        assert round(sum_score_pct) == 100

        sum_count = 0
        sum_score = 0
        for server in season_ntx_dict["notaries"]["alien_AR"]["servers"]:
            print(season_ntx_dict["notaries"]["alien_AR"]["servers"][server])
            sum_count += season_ntx_dict["notaries"]["alien_AR"]["servers"][server]["notary_server_ntx_count"]
            sum_score += season_ntx_dict["notaries"]["alien_AR"]["servers"][server]["notary_server_ntx_score"]
        assert round(sum_count, 4) == round(season_ntx_dict["notaries"]["alien_AR"]["notary_ntx_count"], 4)
        assert round(sum_score, 4) == round(season_ntx_dict["notaries"]["alien_AR"]["notary_ntx_score"], 4)

        sum_count = 0
        sum_score = 0
        for epoch in season_ntx_dict["notaries"]["alien_AR"]["servers"]["Main"]["epochs"]:
            if epoch != "Unofficial":
                sum_count += season_ntx_dict["notaries"]["alien_AR"]["servers"]["Main"]["epochs"][epoch]["notary_server_epoch_ntx_count"]
                sum_score += season_ntx_dict["notaries"]["alien_AR"]["servers"]["Main"]["epochs"][epoch]["notary_server_epoch_ntx_score"]
        assert round(sum_count, 4) == round(season_ntx_dict["notaries"]["alien_AR"]["servers"]["Main"]["notary_server_ntx_count"], 4)
        assert round(sum_score, 4) == round(season_ntx_dict["notaries"]["alien_AR"]["servers"]["Main"]["notary_server_ntx_score"], 4)

        sum_count = 0
        sum_score = 0
        for coin in season_ntx_dict["notaries"]["alien_AR"]["servers"]["Main"]["epochs"]["Epoch_0"]["coins"]:
            sum_count += season_ntx_dict["notaries"]["alien_AR"]["servers"]["Main"]["epochs"]["Epoch_0"]["coins"][coin]["notary_server_epoch_coin_ntx_count"]
            sum_score += season_ntx_dict["notaries"]["alien_AR"]["servers"]["Main"]["epochs"]["Epoch_0"]["coins"][coin]["notary_server_epoch_coin_ntx_score"]
        assert round(sum_count, 4) == round(season_ntx_dict["notaries"]["alien_AR"]["servers"]["Main"]["epochs"]["Epoch_0"]["notary_server_epoch_ntx_count"], 4)
        assert round(sum_score, 4) == round(season_ntx_dict["notaries"]["alien_AR"]["servers"]["Main"]["epochs"]["Epoch_0"]["notary_server_epoch_ntx_score"], 4)


class TestLibRpc:
    def test_RPC(self):
        assert lib_rpc.RPC["KMD"].getblockcount() > 0

    def test_get_ntx_txids(self):
        assert lib_rpc.get_ntx_txids(
            "RXL3YXG2ceaB6C5hfJcN4fvmLH2C34knhA",
             2827762,
             2827763) == [
                "824686b7a27db779447fe24992c9c026abac8adc855b6b0ccc53384385786df4",
                "e8bb7aaa4ccb28d544d24cb7dca50deb83bd5da7fac30a8dc373cde0e34f741a",
                "b2e244a7d2ff909fd07671e0f64b96658d4ed3b6c7fb364293c2b0f2735cde8f"
            ]


class TestLibTableSelect:
    pass


class TestLibTableUpdate:
    pass


class TestLibUrls:
    pass


class TestLibValidate:
    def test_handle_dual_server_coins(self):
        assert lib_validate.handle_dual_server_coins("Third_Party", "GLEEC") == ("Third_Party", "GLEEC-OLD")
        assert lib_validate.handle_dual_server_coins("Main", "GleecBTC")     == ("Third_Party", "GLEEC-OLD")
        assert lib_validate.handle_dual_server_coins("Main", "GLEEC")        == ("Main", "GLEEC")
        assert lib_validate.handle_dual_server_coins("Third_Party", "VRSC")  == ("Third_Party", "VRSC")
        assert lib_validate.handle_dual_server_coins("Main", "DEX")          == ("Main", "DEX")

    def test_get_scored(self):
        assert lib_validate.get_scored(0) == False
        assert lib_validate.get_scored(1) == True

    def test_calc_epoch_score(self):
        assert lib_validate.calc_epoch_score("LTC", 1) == 0
        assert lib_validate.calc_epoch_score("KMD", 1) == 0.0325
        assert lib_validate.calc_epoch_score("Main", 10) == 0.08698
        assert lib_validate.calc_epoch_score("Third_Party", 10) == 0.00977

    def test_get_season_from_block(self):
        assert lib_validate.get_season_from_block(15000000) == None
        assert lib_validate.get_season_from_block("15000000") == None
        assert lib_validate.get_season_from_block(2436999) == "Season_4"
        assert lib_validate.get_season_from_block("2436999") == "Season_4"
        assert lib_validate.get_season_from_block(2437000) == "Season_5"
        assert lib_validate.get_season_from_block("2437000") == "Season_5"

    def test_get_name_from_address(self):
        assert lib_validate.get_name_from_address("RRDRX84ETUUeAU2bFZr2TScYazYxziofYd") == "Luxor (Mining Pool)"
        assert lib_validate.get_name_from_address("RDragoNHdwovvsDLSLMiAEzEArAD3kq6FN") == "dragonhound_DEV"
        assert lib_validate.get_name_from_address("MGRswY9WjB4jALKCrRrvW4KhdtAjif1ztf") == "dragonhound_DEV"

    def test_get_coin_epoch_at(self):
        assert lib_validate.get_coin_epoch_at("Season_5", "Main", "KMD", 1623683000) == "KMD"
        assert lib_validate.get_coin_epoch_at("Season_5", "Main", "LTC", 1623683000) == "LTC"
        assert lib_validate.get_coin_epoch_at("Season_5", "Main", "DEX", 1623683000) != "Unofficial"
        assert lib_validate.get_coin_epoch_at("Season_5", "Main", "BLUR", 1623683000) == "Unofficial"
        assert lib_validate.get_coin_epoch_at("Season_5", "Third_Party", "GLEEC-OLD", 1647120730) != "Unofficial"
        assert lib_validate.get_coin_epoch_at("Season_5", "Third_Party", "GLEEC-OLD", 1647120740) == "Unofficial"

    def test_get_coin_epoch_score_at(self):
        assert lib_validate.get_coin_epoch_score_at("Season_5", "Main", "KMD", 1623683000) == 0.0325
        assert lib_validate.get_coin_epoch_score_at("Season_5", "Main", "LTC", 1623683000) == 0
        assert lib_validate.get_coin_epoch_score_at("Season_5", "Main", "DEX", 1623683000) > 0
        assert lib_validate.get_coin_epoch_score_at("Season_5", "Main", "BLUR", 1623683000) == 0
        assert lib_validate.get_coin_epoch_score_at("Season_5", "Third_Party", "GLEEC-OLD", 1647120730) > 0
        assert lib_validate.get_coin_epoch_score_at("Season_5", "Third_Party", "GLEEC-OLD", 1647120740) == 0

    def test_get_season(self):
        assert lib_validate.get_season(1623683000) == "Season_5"
        assert lib_validate.get_season(1647480279) == "Season_5"
        assert lib_validate.get_season(1623683000000) == "Season_5"
        assert lib_validate.get_season(5623683000) == "Unofficial"

    def test_get_coin_server(self):
        assert lib_validate.get_dpow_coin_server("GLEEC-OLD", "Season_5") == "Third_Party"
        assert lib_validate.get_dpow_coin_server("DEX", "Season_5") == "Main"
        assert lib_validate.get_dpow_coin_server("KMD", "Season_5") == "KMD"

    def test_check_notarised_epochs(self):
        for season in SEASONS_INFO:
            if season not in EXCLUDED_SEASONS:
                notarised_server_epoch_coins = lib_query.get_notarised_server_epoch_coins(season)
                notarised_server_epoch_scores = lib_query.get_notarised_server_epoch_scores(season)

                for server in SEASONS_INFO[season]["servers"]:
                    for epoch in SEASONS_INFO[season]["servers"][server]["epochs"]:
                        epoch_data = SEASONS_INFO[season]["servers"][server]["epochs"][epoch]
                        epoch_start = epoch_data["start_time"]
                        epoch_end = epoch_data["end_time"]
                        epoch_coins = epoch_data["coins"]
                        epoch_score = lib_validate.calc_epoch_score(server, len(epoch_coins))

                        min_max = lib_query.get_ntx_min_max(season, server, epoch)
                        min_time = min_max[1]
                        max_time = min_max[3]

                        assert epoch_start <= min_time and epoch_end >= max_time
                        assert epoch_coins == notarised_server_epoch_coins[server][epoch]
                        assert len(notarised_server_epoch_scores[server][epoch]) == 1
                        assert float(epoch_score) == float(notarised_server_epoch_scores[server][epoch][0])

                        # Any entries where epoch coin not tagged with correct epoch?
                        assert len(lib_query.select_from_notarised_tbl_where(
                                season=season, server=server,
                                include_coins=epoch_coins,
                                lowest_blocktime=epoch_start,
                                highest_blocktime=epoch_end, 
                                not_epoch=epoch
                                )) == 0 
                        assert len(lib_query.select_from_notarised_tbl_where(
                                season=season,
                                include_coins=epoch_coins,
                                lowest_blocktime=epoch_start,
                                highest_blocktime=epoch_end, 
                                not_server=server
                                )) == 0 
                        assert len(lib_query.select_from_notarised_tbl_where(
                                server=server,
                                include_coins=epoch_coins,
                                lowest_blocktime=epoch_start,
                                highest_blocktime=epoch_end, 
                                not_season=season
                                )) == 0 

                        """
                        select from notarised where
                            - timestamp within epoch_start to epoch_end
                            - coin within epoch coins
                                - confirm score

                            - epoch but outside timespan
                            - epoch but wrong score
                            - coin but not in epoch coins
                        """

class TestLibWallet:
    pass
