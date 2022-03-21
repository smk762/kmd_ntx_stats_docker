#!/usr/bin/env python3
import pytest
from lib_api import *
from lib_rpc import *
from lib_crypto import *
from lib_notarisation import *
from lib_mining import *
from lib_helper import *
from lib_electrum import *

pubkey = "0366a87a476a09e05560c5aae0e44d2ab9ba56e69701cee24307871ddd37c86258"
scriptPubKey_asm = "6c04e92a03800016c69bc2cd5e818cddbd37f07c999212ae7f97db7d98b6ab00c6891b00484f444c00f1deb2b25d3e69b1ab59236ce5bee41fe1f1fa08fd682be92f6eea6b30f6ed3908000000"

class TestLibRpc:
    def test_RPC(self):
        assert RPC["KMD"].getblockcount() > 0

    def test_get_ntx_txids(self):
        assert get_ntx_txids(
            "RXL3YXG2ceaB6C5hfJcN4fvmLH2C34knhA",
             2827762,
             2827763) == [
                "824686b7a27db779447fe24992c9c026abac8adc855b6b0ccc53384385786df4",
                "e8bb7aaa4ccb28d544d24cb7dca50deb83bd5da7fac30a8dc373cde0e34f741a",
                "b2e244a7d2ff909fd07671e0f64b96658d4ed3b6c7fb364293c2b0f2735cde8f"
            ]


class TestLibCrypto:
    def test_get_ticker(self):
        assert get_opret_ticker(scriptPubKey_asm) == "HODL"

    def test_lil_endian(self):
        assert lil_endian("deadbeef") == "efbeadde"

    def test_get_addr_from_pubkey(self):
        assert get_addr_from_pubkey("KMD", "038e010c33c56b61389409eea5597fe17967398731e23185c84c472a16fc5d34ab") == "RDragoNHdwovvsDLSLMiAEzEArAD3kq6FN"
        assert get_addr_from_pubkey("MIL", "02b3c168ed4acd96594288cee3114c77de51b6afe1ab6a866887a13a96ee80f33c") == "MGRswY9WjB4jALKCrRrvW4KhdtAjif1ztf"

    def test_get_p2pk_scripthash_from_pubkey(self):
        assert get_p2pk_scripthash_from_pubkey(pubkey) == "a0ecece80abbb1f76e00f034c9ffdf88d8e173c8895945020d27792cadf3aedd"

    def test_get_p2pkh_scripthash_from_pubkey(self):
        assert get_p2pkh_scripthash_from_pubkey(pubkey) == "71417d476001c7a2c56eb72820d7d84b476aa7061da3f860af1c8c0f3fe20772"


class TestLibMining:
    def test_get_mined_row(self):
        row = get_mined_row(2824869)
        assert row.block_height == 2824869
        assert row.block_time == 1647487930
        assert row.address == "RKytuA1ubrCD66hNNemcsvyDhDbcR2S1sU"
        assert row.name == "mrlynch_AR"
        assert row.txid == "8202597ca6a07d5f03d6bcfe37c102d14ecaa7860815279e3d0f0efd6173d40b"
        assert row.diff == 197318030.6073029
        assert row.season == "Season_5"
        assert row.value == 3.00005000


class TestLibHelper:

    def test_safe_div(self):
        assert safe_div(10,2) == 5
        assert safe_div(10,0) == 0

    def test_has_season_started(self):
        assert has_season_started("Season_5") == True
        assert has_season_started("Season_6") == False
        assert has_season_started("Season_12") == False

    def test_handle_dual_server_chains(self):
        assert handle_dual_server_chains("Third_Party", "GLEEC") == ("Third_Party", "GLEEC-OLD")
        assert handle_dual_server_chains("Main", "GLEEC", "FUbr4EfszR3NKbZTV1Cd9mDsjYth3KFq8E") == ("Third_Party", "GLEEC-OLD")
        assert handle_dual_server_chains("Main", "GLEEC") == ("Main", "GLEEC")
        assert handle_dual_server_chains("Third_Party", "VRSC") == ("Third_Party", "VRSC")
        assert handle_dual_server_chains("Main", "DEX") == ("Main", "DEX")

    def test_handle_translate_chains(self):
        assert handle_translate_chains("GleecBTC") == "GLEEC-OLD"
        assert handle_translate_chains("TKL") == "TOKEL"
        assert handle_translate_chains("ARRR") == "PIRATE"
        assert handle_translate_chains("KMD") == "KMD"

    def test_get_pubkeys(self):
        assert len(get_pubkeys("Season_5", "Third_Party")) == 64
        assert len(get_pubkeys("Season_5", "Main")) == 64
        assert len(get_pubkeys("Season_777", "Main")) == 0
        assert len(get_pubkeys("Season_5", "Minecraft")) == 0

    def test_get_scored(self):
        assert get_scored(0) == False
        assert get_scored(1) == True

    def test_get_season_from_block(self):
        assert get_season_from_block(15000000) == None
        assert get_season_from_block("15000000") == None
        assert get_season_from_block(2436999) == "Season_4"
        assert get_season_from_block("2436999") == "Season_4"
        assert get_season_from_block(2437000) == "Season_5"
        assert get_season_from_block("2437000") == "Season_5"

    def test_get_name_from_address(self):
        assert get_name_from_address("RRDRX84ETUUeAU2bFZr2TScYazYxziofYd") == "Luxor (Mining Pool)"
        assert get_name_from_address("RDragoNHdwovvsDLSLMiAEzEArAD3kq6FN") == "dragonhound_DEV"
        assert get_name_from_address("MGRswY9WjB4jALKCrRrvW4KhdtAjif1ztf") == "dragonhound_DEV"

    def test_get_address_from_notary(self):
        assert get_address_from_notary("Season_5_Third_Party", "dragonhound_NA", "KMD") == "RHound1gvLqhSfvpS1DAPkKp3Y1D4TRxKZ"
        assert get_address_from_notary("Season_5", "dragonhound_DEV", "KMD") == "RDragoNHdwovvsDLSLMiAEzEArAD3kq6FN"
        assert get_address_from_notary("Season_5", "mrlynch_AR", "DEX") == "RKytuA1ubrCD66hNNemcsvyDhDbcR2S1sU"
    
    def test_get_chain_epoch_at(self):
        assert get_chain_epoch_at("Season_5", "Main", "KMD", 1623683000) == "KMD"
        assert get_chain_epoch_at("Season_5", "Main", "LTC", 1623683000) == "LTC"
        assert get_chain_epoch_at("Season_5", "Main", "DEX", 1623683000) != "Unofficial"
        assert get_chain_epoch_at("Season_5", "Main", "BLUR", 1623683000) == "Unofficial"
        assert get_chain_epoch_at("Season_5", "Third_Party", "GLEEC-OLD", 1647120730) != "Unofficial"
        assert get_chain_epoch_at("Season_5", "Third_Party", "GLEEC-OLD", 1647120740) == "Unofficial"

    def test_get_chain_epoch_score_at(self):
        assert get_chain_epoch_score_at("Season_5", "Main", "KMD", 1623683000) == 0.0325
        assert get_chain_epoch_score_at("Season_5", "Main", "LTC", 1623683000) == 0
        assert get_chain_epoch_score_at("Season_5", "Main", "DEX", 1623683000) > 0
        assert get_chain_epoch_score_at("Season_5", "Main", "BLUR", 1623683000) == 0
        assert get_chain_epoch_score_at("Season_5", "Third_Party", "GLEEC-OLD", 1647120730) > 0
        assert get_chain_epoch_score_at("Season_5", "Third_Party", "GLEEC-OLD", 1647120740) == 0

    def test_get_season(self):
        assert get_season(1623683000) == "Season_5"
        assert get_season(1647480279) == "Season_5"
        assert get_season(1623683000000) == "Season_5"
        assert get_season(5623683000) == "Unofficial"

    def test_get_season_server_from_addresses(self):
        valid_main_address_list = [
            "RVrtLPvKrszs7zSggTsXPYsbxc5SwALiEN", "RALiENAgeHExyyEnBARdZdwWbHWokoUbtc",
            "RDZaLiENRUnckP57oRxLznYmFM5bV9PaZV", "RALienLQZxF5JeJxWyLfFTw5Y3ohmdU4gU",
            "RP4bAeJGc6b21J6UA4TqNRr6hdiGTALien", "RMmPakZ7R3bap78JeKVcxygpS2fTy6NYxX",
            "RNyD2yYVzC9Jv3Gqhju62RZmRMZ2n1qaSS", "RLxmmwsjtCsEC6sfjjxsWoTrnpcmgC9cfv",
            "RLopsvKfmtSgBESeteApG3D1NMudg6XJ8t", "RPEAampRWYacYse3gAud48DsiLttzhAYHV",
            "RNFTgUWvx8zUsdVL56uuffiKXZTU4q45cr", "RWvfkt8UjbPWXgeZEcgYmKw2vA1bbAx5t2",
            "RVNQWLPdPG1AabQvzmwGpE5pxd1Yt8SkYL"
        ]

        valid_3p_address_list = [
            "RDosr7iNVe26tcErCBGHZ2YwE2JxcALiEN", "RALiENfYqijwdDuKUwtQmXFYWURq27S98S",
            "RSUALiEnuYzcudwcAxSjeMiB7SwQMRR3Xu", "RALienKsZ36cUVDZSRMtNTGyG5jDtvDDcK",
            "RQJQY3LTSZZKq4Z2f6rRV4oxvGzZALienb", "RHX2k1DN87BFfEkwGxnV7EhopRiDU8uqvu",
            "RG9VXFkVYh4BuPWELt7uJrYee77wFmvMYL", "RJEeHP91rc84U5ArfbTQzYQsv4T8GNqNWF",
            "RB9Tgwdc5oPKVmHMssd7LZvKG44zX7jTWD", "RRMw2A7qeJ61LsT777Z9JuTGWfA1M3Uznx",
            "RHHzesqTHS8Mi8hT5EyU2hmhJXmNVuPD7S", "REx2EibDGdNZLpLV36AA9duzchDHaC4hSC",
            "RP8buuL4L1BzrNarKq4aLpWXfVmGWU4HrZ"
        ]

        too_few_address_list = valid_main_address_list[:-1]
        too_many_address_list = valid_main_address_list + ["R9iBY1oyt4aMocyMbScxqzC1JtWa1XNn5K"]
        invalid_address_in_list = too_few_address_list + ["R9iBY1oyt4aMocyMbScxqzC1JtWa1XNn5K"]

        season, server = get_season_server_from_addresses(too_many_address_list, "DEX")
        assert server == "Unofficial" and season == "Unofficial"
        season, server = get_season_server_from_addresses(too_few_address_list, "DEX")
        assert server == "Unofficial" and season == "Unofficial"
        season, server = get_season_server_from_addresses(invalid_address_in_list, "DEX")
        assert server == "Unofficial" and season == "Unofficial"

        season, server = get_season_server_from_addresses(valid_main_address_list, "DEX")
        assert server == "Main" and season == "Season_5"
        season, server = get_season_server_from_addresses(valid_main_address_list, "KMD")
        assert server == "KMD" and season == "Season_5"
        season, server = get_season_server_from_addresses(valid_3p_address_list, "GLEEC-OLD")
        assert server == "Third_Party" and season == "Season_5"

    def test_get_chain_server(self):
        assert get_chain_server("GLEEC-OLD", "Season_5") == "Third_Party"
        assert get_chain_server("DEX", "Season_5") == "Main"
        assert get_chain_server("KMD", "Season_5") == "KMD"

    def test_get_season_notaries(self):
        assert len(get_season_notaries("Season_5")) == 64

    def test_get_dpow_coin_src(self):
        assert get_dpow_coin_src("(https://github.com/chips-blockchain/chips)") == "https://github.com/chips-blockchain/chips"

    def test_get_dpow_coin_server(self):
        assert get_dpow_coin_server("dPoW-3P") == "Third_Party"
        assert get_dpow_coin_server("dPoW-MainNet") == "Main"

    def test_get_assetchain_launch_params(self):
        assert get_assetchain_launch_params({
            "ac_name": "DEX",
            "ac_supply": "999999"
        }) == "~/komodo/src/komodod -ac_name=DEX -ac_supply=999999"
        assert get_assetchain_launch_params({
            "ac_name": "MORTY",
            "ac_supply": "90000000000",
            "ac_reward": "100000000",
            "ac_cc": "3",
            "ac_staked": "10",
            "addnode": ["138.201.136.145", "95.217.44.58"]
        }) == "~/komodo/src/komodod -ac_name=MORTY -ac_supply=90000000000 -ac_reward=100000000 -ac_cc=3 -ac_staked=10 -addnode=138.201.136.145 -addnode=95.217.44.58"

    def test_get_assetchain_conf_path(self):
        assert get_assetchain_conf_path("DEX") == "~/.komodo/DEX/DEX.conf"

    def test_get_assetchain_cli(self):
        assert get_assetchain_cli("DEX") == "~/komodo/src/komodo-cli -ac_name=DEX"

    def test_pre_populate_coins_data(self):
        assert pre_populate_coins_data({}, "DEX") == {
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

    def test_get_coins_repo_electrums(self):
        assert get_coins_repo_electrums({
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
        }, "TOKEL") == {
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
                "explorers": [],
                "mm2_compatible": 0
            }
        }
        assert get_coins_repo_electrums({
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
        }, "PIRATE") == {
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
        assert get_coins_repo_electrums({
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
        }, "KMD") == {
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
        assert get_coins_repo_explorers({
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
        }, "TOKEL") == {
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
        assert get_coins_repo_explorers({
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
        }, "PIRATE") == {
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
        assert get_coins_repo_explorers({
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
        }, "KMD") == {
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
        assert get_coins_repo_icons({
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
        }, "TOKEL") == {
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
        assert get_coins_repo_icons({
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
        }, "PIRATE") == {
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
        assert get_coins_repo_icons({
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
        }, "KMD") == {
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

    def test_is_notary_ltc_address(self):
        assert is_notary_ltc_address("LfmssDyX6iZvbVqHv6t9P6JWXia2JG7mdb") == False
        assert is_notary_ltc_address("LPoLsVnq7nFR7fYJ9JMtLjinco4taNqzkU") == True

    def test_get_local_addresses(self):
        url = get_notary_ltc_txid_url("adc04856562fd8d8abfe8487d0d77c26c680cba36400025b1e9235a38ac76a2e")
        local_info = requests.get(url).json()["results"]
        assert get_local_addresses(local_info) == [
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
        url = get_notary_ltc_txid_url("deadbeef")
        local_info = requests.get(url).json()["results"]
        assert get_local_addresses(local_info) == []


class TestLibElectrum:
    def test_get_full_electrum_balance(self):
        assert get_full_electrum_balance(pubkey, "electrum1.cipig.net", 10001) > 0


class TestLibApi:
    def test_get_dexstats_balance(self):
        assert get_dexstats_balance("KMD", "RDragoNHdwovvsDLSLMiAEzEArAD3kq6FN") > 0


class TestLibNotary:
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
                    'Season_4', 'Main', 'N/A')

        actual = get_notarised_data("2e8732b608a37b47307a67abce11922db968435552f2ea6ad0b5b4fda82123d5")
        assert actual == expected

    def test_get_season_ntx_dict(season):
        season_ntx_dict = get_season_ntx_dict("Season_5")
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
        assert int(sum_count_pct) == 1300
        assert int(sum_score_pct) == 100

        sum_count = 0
        sum_score = 0
        for server in season_ntx_dict["notaries"]["alien_AR"]:
            sum_count += season_ntx_dict["notaries"]["alien_AR"]["servers"][server]["notary_server_ntx_count"]
            sum_score += season_ntx_dict["notaries"]["alien_AR"]["servers"][server]["notary_server_ntx_score"]
        assert round(season_count, 4) == round(season_ntx_dict["notaries"]["alien_AR"]["notary_ntx_count"], 2)
        assert round(season_score, 4) == rouns(season_ntx_dict["notaries"]["alien_AR"]["notary_ntx_score"], 2)

        sum_count = 0
        sum_score = 0
        for epoch in season_ntx_dict["notaries"]["alien_AR"]["servers"]["Main"]["epochs"]:
            if epoch != "Unofficial":
                sum_count += season_ntx_dict["notaries"]["alien_AR"]["servers"]["Main"]["epochs"][epoch]["notary_server_epoch_ntx_count"]
                sum_score += season_ntx_dict["notaries"]["alien_AR"]["servers"]["Main"]["epochs"][epoch]["notary_server_epoch_ntx_score"]
        assert round(season_count, 4) == round(season_ntx_dict["notaries"]["alien_AR"]["servers"]["Main"]["notary_server_ntx_count"], 4)
        assert round(season_score, 4) == round(season_ntx_dict["notaries"]["alien_AR"]["servers"]["Main"]["notary_server_ntx_score"], 4)

        sum_count = 0
        sum_score = 0
        for chain in season_ntx_dict["notaries"]["alien_AR"]["servers"]["Main"]["epochs"]["Epoch_0"]["chains"]:
            sum_count += season_ntx_dict["notaries"]["alien_AR"]["servers"]["Main"]["epochs"]["Epoch_0"]["chains"][chain]["notary_server_epoch_ntx_count"]
            sum_score += season_ntx_dict["notaries"]["alien_AR"]["servers"]["Main"]["epochs"]["Epoch_0"]["chains"][chain]["notary_server_epoch_ntx_score"]
        assert round(season_count, 4) == round(season_ntx_dict["notaries"]["alien_AR"]["servers"]["Main"]["epochs"]["Epoch_0"]["notary_server_epoch_ntx_count"], 4)
        assert round(season_score, 4) == round(season_ntx_dict["notaries"]["alien_AR"]["servers"]["Main"]["epochs"]["Epoch_0"]["notary_server_epoch_ntx_score"], 4)
