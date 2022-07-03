NAV_DATA = {
    "Notarisation": {
        "Notary Profiles": {
            "icon": "",
            "url": "/notary_profile"
        },
        "dPoW Coin Profiles": {
            "icon": "",
            "url": "/coin_profile"
        },
        "Season Scoreboard": {
            "icon": "",
            "url": "/ntx_scoreboard"
        },
        "24hr Scoreboard": {
            "icon": "",
            "url": "/ntx_scoreboard_24hrs"
        },
        "Seednode Version": {
            "icon": "",
            "url": "/atomicdex/seednode_version"
        },
        " Last Notarisation (Coin)": {
            "icon": "",
            "url": "/coins_last_ntx"
        },
        "Notarisations Last 24hrs": {
            "icon": "",
            "url": "/notarised_24hrs/?coin=RICK"
        },
        "Coin dPoW Tenure": {
            "icon": "",
            "url": "/notarised_tenure"
        },
        "dPoW Scoring Epochs": {
            "icon": "",
            "url": "/scoring_epochs"
        }
    },
    "Mining": {
        "Season Overview": {
            "icon": "",
            "url": "/mining_overview"
        },
        "Last 24hrs": {
            "icon": "",
            "url": "/mining_24hrs"
        },
        "Notary Last Mined": {
            "icon": "",
            "url": "/notary_last_mined"
        }
    },
    "Tools": {
        "Address from Pubkey": {
            "icon": "",
            "url": "/tools/pubkey_addresses"
        },
        "Address Conversion": {
            "icon": "",
            "url": "/tools/convert_addresses"
        },
        "Decode OP_RETURN": {
            "icon": "",
            "url": "/tools/decode_opreturn"
        },
        "Daemon CLIs": {
            "icon": "",
            "url": "/tools/daemon_clis"
        },
        "Launch Params": {
            "icon": "",
            "url": "/tools/launch_params"
        },
        "KMD Rewards": {
            "icon": "",
            "url": "/tools/kmd_rewards"
        },
        "RICK / MORTY Faucet": {
            "icon": "",
            "url": "/tools/faucet"
        },
        "Raw Transactions": {
            "icon": "",
            "url": "/tools/send_raw_tx"
        },
        "Scripthash from Address": {
            "icon": "",
            "url": "/tools/scripthash_from_address"
        },
        "Scripthashes from Pubkey": {
            "icon": "",
            "url": "/tools/scripthashes_from_pubkey"
        }
    },
    "Resources": {
        "DexStats": {
            "icon": "",
            "url": "https://www.dexstats.info/"
        },
        "Komodod": {
            "icon": "",
            "url": "https://komodod.com/"
        },
        "Notary Stats": {
            "icon": "",
            "url": "https://notarystats.info/"
        },
        "Komodo Stats": {
            "icon": "",
            "url": "https://komodostats.com/"
        },
        "dpow.io Notary Stats": {
            "icon": "",
            "url": "https://dpow.io/"
        },
        "iKomodo": {
            "icon": "",
            "url": "https://ikomodo.com/"
        },
        "Developer Docs": {
            "icon": "",
            "url": "https://developers.komodoplatform.com/"
        },
        "NN Setup Guide": {
            "icon": "",
            "url": "https://docs.komodoplatform.com/notary/setup-Komodo-Notary-Node.html#nn-repo-quick-reference"
        },
        "dPoW Guide": {
            "icon": "",
            "url": "https://github.com/komodoplatform/dpow/"
        },
        "JMJ's Dev blog": {
            "icon": "",
            "url": "https://www.jmjatlanta.com/"
        },
        "Notary Node Bible": {
            "icon": "",
            "url": "https://github.com/KomodoPlatform/dPoW/blob/dev/doc/bible.md"
        },
        "Webworkers NN Tools": {
            "icon": "",
            "url": "https://github.com/webworker01/nntools/"
        },
        "Mr Lynch's NN Utils": {
            "icon": "",
            "url": "https://github.com/MrMLynch/nnutils"
        },
        "KomodoTools": {
            "icon": "",
            "url": "https://github.com/KomodoPlatform/komodotools"
        },
        "Decker's Komodo Scripts": {
            "icon": "",
            "url": "https://github.com/DeckerSU/komodo_scripts"
        },
        "CG's Low Fee BTC Split Script": {
            "icon": "",
            "url": "https://github.com/TheComputerGenie/Misc_Stuff/blob/master/NN%20stuff/BTCsplit.sh"
        },
        "Decker's Wallet Cleaner Script": {
            "icon": "",
            "url": "https://github.com/DeckerSU/komodo_scripts/blob/master/resend_funds.sh"
        },
        "Shossain's Wallet Cleaner Notes": {
            "icon": "",
            "url": "https://techloverhd.com/2020/07/how-to-send-komodo-or-any-smart-chain-funds-from-your-address-without-rescanning-the-wallet/"
        }

    },
    "AtomicDEX": {
        "Activation": {
            "icon": "",
            "url": "/atomicdex/activation_commands"
        },
        "Batch Activation": {
            "icon": "",
            "url": "/atomicdex/batch_activation_form"
        },
        "Bestorders": {
            "icon": "",
            "url": "/atomicdex/bestorders"
        },
        "GUI Stats": {
            "icon": "",
            "hide": True,
            "url": "/atomicdex/gui_stats"
        },
        "Last 200 Swaps": {
            "icon": "",
            "url": "/atomicdex/last_200_swaps"
        },
        "Last 200 Failed Swaps": {
            "icon": "",
            "hide": True,
            "url": "/atomicdex/last_200_failed_swaps"
        },
        "Makerbot Config": {
            "icon": "",
            "url": "/atomicdex/makerbot_config_form"
        },
        "Orderbook": {
            "icon": "",
            "url": "/atomicdex/orderbook"
        }
    }
}

TESTNET_NAV = {
    "Notarisation": {
        "Vote Results": {
            "icon": "",
            "url": "/notary_vote"
        },
        "Testnet Leaderboard": {
            "icon": "",
            "url": "/testnet_ntx_scoreboard"
        },
        "Testnet Seednodes": {
            "icon": "",
            "url": "/seednode_version"
        }
    }
}

TESTNET = False
if TESTNET:
    NAV_DATA.update(TESTNET_NAV)