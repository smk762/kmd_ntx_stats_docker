import os
from dotenv import load_dotenv
load_dotenv()

PLATFORM_URLS = {
	"BNB" : {
        "urls": [
            "http://bsc1.cipig.net:8655",
            "http://bsc2.cipig.net:8655",
            "http://bsc3.cipig.net:8655"
        ]		
	},
	"ETHR" : {
        "urls": [
            "https://ropsten.infura.io/v3/1d059a9aca7d49a3a380c71068bffb1c"
        ]		
	},
	"ETH" : {
        "urls": [
            "http://eth1.cipig.net:8555",
            "http://eth2.cipig.net:8555",
            "http://eth3.cipig.net:8555"
        ],
        "gas_station_url":"https://ethgasstation.info/json/ethgasAPI.json"
	},
	"ETH-ARB20" : {
        "urls": [
            "https://rinkeby.arbitrum.io/rpc"
        ]
	},
	"ONE" : {
        "urls": [
            "https://api.harmony.one",
            "https://api.s0.t.hmny.io"
        ]
	},
	"MATIC" : {
        "urls": [
            "https://polygon-rpc.com"
        ]
	},
	"MATICTEST" : {
        "urls": [
            "https://polygon-rpc.com"
        ]
	},
	"AVAX" : {
        "urls": [
            "https://api.avax.network/ext/bc/C/rpc"
        ]
	},
	"AVAXT" : {
        "urls": [
            "https://api.avax.network/ext/bc/C/rpc"
        ]
	},
	"BNBT" : {
        "urls": [
            "https://data-seed-prebsc-1-s2.binance.org:8545"
        ]
	},
	"MOVR" : {
        "urls": [
            "https://rpc.moonriver.moonbeam.network"
        ]
	},
	"FTM" : {
        "urls": [
            "https://rpc.ftm.tools/"
        ]
	},
	"FTMT" : {
        "urls": [
            "https://rpc.testnet.fantom.network/"
        ]
	},
	"KCS" : {
        "urls": [
            "https://rpc-mainnet.kcc.network"
        ]
	},
	"HT" : {
        "urls": [
            "https://http-mainnet.hecochain.com"
        ]
	},
	"UBQ" : {
        "urls": [
            "https://rpc.octano.dev/"
        ]
	},
	"ETC" : {
        "urls": [
            "https://www.ethercluster.com/etc"
        ]
	},
	"OPT20" : {
        "urls": [
            "https://kovan.optimism.io"
        ]
	}
}


MM2_USERPASS = os.getenv("MM2_USERPASS")
MM2_IP = "http://mm2:7783"
TESTNET_COINS = ["BNBT", "ETHR", "AVAXT", "tQTUM", "MATICTEST", "AVAXT", "FTMT"]

SWAP_CONTRACTS = {
    "ETH": {
        "mainnet": {
            "swap_contract": "0x24ABE4c71FC658C91313b6552cd40cD808b3Ea80",
            "fallback_contract": "0x8500AFc0bc5214728082163326C2FF0C73f4a871",
            "gas_station": "https://ethgasstation.info/json/ethgasAPI.json"
        }
    },
    "ETHR": {
        "testnet": {
            "swap_contract": "0x6b5A52217006B965BB190864D62dc3d270F7AaFD",
            "fallback_contract": "0x7Bc1bBDD6A0a722fC9bffC49c921B685ECB84b94"
        }
    },
    "MOVR": {
        "mainnet": {
            "swap_contract": "0x9130b257D37A52E52F21054c4DA3450c72f595CE",
            "fallback_contract": "0x9130b257D37A52E52F21054c4DA3450c72f595CE"
        }
    },
    "FTM": {
        "mainnet": {
            "swap_contract": "0x9130b257D37A52E52F21054c4DA3450c72f595CE",
            "fallback_contract": "0x9130b257D37A52E52F21054c4DA3450c72f595CE"
        }
    },
    "FTMT": {
        "testnet": {
            "swap_contract": "0x9130b257D37A52E52F21054c4DA3450c72f595CE",
            "fallback_contract": "0x9130b257D37A52E52F21054c4DA3450c72f595CE"
        }
    },
    "ONE": {
        "mainnet": {
            "swap_contract": "0x9130b257D37A52E52F21054c4DA3450c72f595CE",
            "fallback_contract": "0x9130b257D37A52E52F21054c4DA3450c72f595CE"
        }
    },
    "MATIC": {
        "mainnet": {
            "swap_contract": "0x9130b257D37A52E52F21054c4DA3450c72f595CE",
            "fallback_contract": "0x9130b257D37A52E52F21054c4DA3450c72f595CE",
            "gas_station": "https://gasstation-mainnet.matic.network/"
        }
    },
    "MATICTEST": {
        "testnet": {
            "swap_contract": "0x73c1Dd989218c3A154C71Fc08Eb55A24Bd2B3A10",
            "fallback_contract": "0x73c1Dd989218c3A154C71Fc08Eb55A24Bd2B3A10",
            "gas_station": "https://gasstation-mumbai.matic.today/"
        }
    },
    "AVAX": {
        "mainnet": {
            "swap_contract": "0x9130b257D37A52E52F21054c4DA3450c72f595CE",
            "fallback_contract": "0x9130b257D37A52E52F21054c4DA3450c72f595CE"
        }
    },
    "AVAXT": {
        "testnet": {
            "swap_contract": "0x9130b257D37A52E52F21054c4DA3450c72f595CE",
            "fallback_contract": "0x9130b257D37A52E52F21054c4DA3450c72f595CE"
        }
    },
    "BNB": {
        "mainnet": {
            "swap_contract": "0xeDc5b89Fe1f0382F9E4316069971D90a0951DB31",
            "fallback_contract": "0xeDc5b89Fe1f0382F9E4316069971D90a0951DB31"
        }
    },
    "BNBT": {
        "testnet": {
            "swap_contract": "0xcCD17C913aD7b772755Ad4F0BDFF7B34C6339150",
            "fallback_contract": "0xcCD17C913aD7b772755Ad4F0BDFF7B34C6339150"
        }
    },
    "ETH-ARB20": {
        "mainnet": {
            "swap_contract": "0x9130b257d37a52e52f21054c4da3450c72f595ce",
            "fallback_contract": "0x9130b257d37a52e52f21054c4da3450c72f595ce"
        }
    },
    "UBIQ": {
        "mainnet": {
            "swap_contract": "0x9130b257D37A52E52F21054c4DA3450c72f595CE",
            "fallback_contract": "0x9130b257D37A52E52F21054c4DA3450c72f595CE"
        }
    },
    "KCS": {
        "mainnet": {
            "swap_contract": "0x9130b257D37A52E52F21054c4DA3450c72f595CE",
            "fallback_contract": "0x9130b257D37A52E52F21054c4DA3450c72f595CE"
        }
    },
    "HT": {
        "mainnet": {
            "swap_contract": "0x9130b257D37A52E52F21054c4DA3450c72f595CE",
            "fallback_contract": "0x9130b257D37A52E52F21054c4DA3450c72f595CE"
        }
    },
    "OPTIMISM": {
        "mainnet": {
            "swap_contract": "0x9130b257d37a52e52f21054c4da3450c72f595ce",
            "fallback_contract": "0x9130b257d37a52e52f21054c4da3450c72f595ce"
        }
    },
    "QTUM": {
        "mainnet": {
            "swap_contract": "0x2f754733acd6d753731c00fee32cb484551cc15d",
            "fallback_contract": "0x2f754733acd6d753731c00fee32cb484551cc15d"
        },
        "testnet": {
            "swap_contract": "0xba8b71f3544b93e2f681f996da519a98ace0107a",
            "fallback_contract": "0xba8b71f3544b93e2f681f996da519a98ace0107a"
        }
    },
    "tQTUM": {
        "mainnet": {
            "swap_contract": "0x2f754733acd6d753731c00fee32cb484551cc15d",
            "fallback_contract": "0x2f754733acd6d753731c00fee32cb484551cc15d"
        },
        "testnet": {
            "swap_contract": "0xba8b71f3544b93e2f681f996da519a98ace0107a",
            "fallback_contract": "0xba8b71f3544b93e2f681f996da519a98ace0107a"
        }
    },
    "ARB": {
        "mainnet": {
            "swap_contract": "0x9130b257d37a52e52f21054c4da3450c72f595ce",
            "fallback_contract": "0x9130b257d37a52e52f21054c4da3450c72f595ce"
        }
    },
    "OPT": {
        "mainnet": {
            "swap_contract": "0x9130b257d37a52e52f21054c4da3450c72f595ce",
            "fallback_contract": "0x9130b257d37a52e52f21054c4da3450c72f595ce"
        }
    },
    "SBCH": {
        "mainnet": {
            "swap_contract": "0x25bF2AAB8749AD2e4360b3e0B738f3Cd700C4D68",
            "fallback_contract": "0x25bF2AAB8749AD2e4360b3e0B738f3Cd700C4D68"
        }
    }
}
