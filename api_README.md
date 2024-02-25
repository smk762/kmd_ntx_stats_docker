# Komodo Earth API

## /api/info/addresses/

**notary addresses information**

The `/api/info/addresses/` endpoint returns Notary Node addresses, nested by Name > Season > Chain 
    Default filter returns current NN Season 

### GET parameters

| Name              | Type                 | Description                                                           |
| ----------------- | -------------------- | --------------------------------------------------------------------- |
| season            | (string, optional)   | Filter results to return addresses for a specific Notary Season       |
| notary            | (string, optional)   | Filter results to return addresses for a specific Notary Operator     |
| chain             | (string, optional)   | Filter results to return addresses for a specific Coin                |
| pubkey            | (string, optional)   | Filter results to return addresses for a specific Pubkey              |
| address           | (string, optional)   | Filter results to information relaed to a specific Address            |


### Response

| Name                            | Type      | Description                                                      |
| ------------------------------- | --------- | ---------------------------------------------------------------- |
| count                           | (integer) | Number of coins matching the filter                              |
| results                         | (json)    | A json dictionary of address information                         |
| results.notary                  | (json)    | Notary Node name                                                 |
| results.notary.season           | (json)    | Notary season                                                    |
| results.notary.season.pubkey    | (json)    | Notary Node's pubkey for the season                              |
| results.notary.season.notary_id | (json)    | Notary Node's notary_id for the season                           |
| results.notary.season.addresses | (json)    | Dict of addresses linked to pubkey for each chain                |

#### :pushpin: Examples

URL:

```
http://notary.earth:8762/info/addresses/?chain=KMD&notary=alien_AR
```

<collapse-text hidden title="Response">

```json
{
    "count": 1,
    "results": [
        {
            "alien_AR": {
                "Season_2": {
                    "notary_id": "56",
                    "pubkey": "0348d9b1fc6acf81290405580f525ee49b4749ed4637b51a28b18caa26543b20f0",
                    "addresses": {
                        "KMD": "RBHzJTW73U3nyHyxBwiG92bJckxZowPY87"
                    }
                },
                "Season_3": {
                    "notary_id": "53",
                    "pubkey": "03911a60395801082194b6834244fa78a3c30ff3e888667498e157b4aa80b0a65f",
                    "addresses": {
                        "KMD": "RVrtLPvKrszs7zSggTsXPYsbxc5SwALiEN"
                    }
                },
                "Season_3.5": {
                    "notary_id": "53",
                    "pubkey": "03911a60395801082194b6834244fa78a3c30ff3e888667498e157b4aa80b0a65f",
                    "addresses": {
                        "KMD": "RVrtLPvKrszs7zSggTsXPYsbxc5SwALiEN"
                    }
                },
                "Season_3_Third_Party": {
                    "notary_id": "53",
                    "pubkey": "024f20c096b085308e21893383f44b4faf1cdedea9ad53cc7d7e7fbfa0c30c1e71",
                    "addresses": {
                        "KMD": "RDosr7iNVe26tcErCBGHZ2YwE2JxcALiEN"
                    }
                }
            }
        }
    ]
}
```
</collapse-text>


## /api/info/balances/

**notary balances information**

The `/api/info/balances/` endpoint returns Notary Node balances, nested by Name > Season > Chain 
    Default filter returns current NN Season 

::: tip
You can use this endpoint for setting up "low balance" alerts!
:::

### GET parameters

| Name              | Type                 | Description                                                           |
| ----------------- | -------------------- | --------------------------------------------------------------------- |
| season            | (string, optional)   | Filter results to return balances for a specific Notary Season        |
| notary            | (string, optional)   | Filter results to return balances for a specific Notary Operator      |
| chain             | (string, optional)   | Filter results to return balances for a specific Coin                 |
| address           | (string, optional)   | Filter results to return balances for to a specific Address           |


### Response

| Name                         | Type      | Description                                                      |
| ---------------------------- | --------- | ---------------------------------------------------------------- |
| count                        | (integer) | Number of coins matching the filter                              |
| results                     | (json)    | A json dictionary of address information                         |
| results.season               | (json)    | The name of the address owner (as a key)                         |
| results.season.notary        | (json)    | Ticker for all dPoW protected coins                              |
| results.season.notary.chain  | (json)    | Dict with address / balance for all dPoW protected coins         |

#### :pushpin: Examples

URL:

```bash
http://notary.earth:8762/info/balances/?notary=pirate_AR&chain=OOT
```

<collapse-text hidden title="Response">

```json

{
    "count": 1,
    "results": [
        {
            "Season_3": {
                "pirate_AR": {
                    "OOT": {
                        "RV3B97zSjT8qsZ54XXE3iEWMv2oQsToz55": 0.0,
                        "RU2RqFrjwy4kauANnzK1JWyDVAx47z51qw": 0.20816681
                    }
                }
            }
        }
    ]
}
```
</collapse-text>

## /api/info/coins/

**coins information**

The `/api/info/coins/` endpoint shows information about coins from the [KomodoPlatform/coins](https://github.com/komodoplatform/coins) and [KomodoPlatform/dPoW](https://github.com/KomodoPlatform/dPoW) repositories.

Information includes mm2 compatibility, electrum/explorer availability, and dPoW status.

::: tip
You can use this endpoint for:
 - creating scripts used in notary node management.
 - setup coin configs for marketmaker2
 - define electrum servers for scripts
 - generate links to block explorer pages
:::

### GET parameters

| Name            | Type                 | Description                                                           |
| --------------- | -------------------- | --------------------------------------------------------------------- |
| chain           | (string, optional)   | Filter results to return a specific coin                              |
| mm2_compatible  | (integer, optional)  | Filter results to return a mm2 compatible coins (0 = false, 1 = true) |
| dpow_active     | (integer, optional)  | Filter results to return a coins being notarised with dPoW            |

### Response

| Name                        | Type      | Description                                                                        |
| --------------------------- | --------- | ---------------------------------------------------------------------------------- |
| count                       | (integer) | Number of coins matching the filter                                                |
| results                     | (json)    | A json dictionary of coin information                                              |
| results.coin                | (json)    | the name of the coin (as a key)                                                    |
| results.coin.coins_info     | (json)    | information about the coin as listed in https://github.com/KomodoPlatform/coins    |
| results.coin.dpow           | (json)    | information about the coin as listed in https://github.com/KomodoPlatform/dPoW/    |
| results.coin.explorers      | (list)    | list of block explorers for the coin from https://github.com/KomodoPlatform/coins  |
| results.coin.electrums      | (list)    | list of electrum servers for the coin from https://github.com/KomodoPlatform/coins |
| results.coin.electrums_ssl  | (list)    | list of SSL electrum servers for the coin                                          |
| results.coin.electrums_wss  | (list)    | list of WSS electrum servers for the coin                                          |
| results.coin.mm2_compatible | (integer) | 0 = not mm2 compatible; 1 = mm2 compatible                                         |
| results.coin.dpow_active    | (integer) | 0 = not being notarised by dPoW; 1 = being notarised by dPoW                       |

#### :pushpin: Examples

URL:

```bash
http://notary.earth:8762/info/coins/?chain=DOC&mm2_compatible=1&dpow_active=1
```

<collapse-text hidden title="Response">

```json
{
    "count": 1,
    "results": [
        {
            "DOC": {
                "coins_info": {
                    "mm2": 1,
                    "coin": "DOC",
                    "asset": "DOC",
                    "fname": "DOC (TESTCOIN)",
                    "rpcport": 25435,
                    "txversion": 4,
                    "overwintered": 1
                },
                "dpow": {
                    "src": "https://github.com/komodoplatform/komodo",
                    "server": "dPoW-mainnet",
                    "version": "0.5.2",
                    "launch_params": " -ac_name=DOC -ac_supply=90000000000 -ac_reward=100000000 -ac_cc=3 -ac_staked=10 -addnode=138.201.136.145 -addnode=95.217.44.58"
                },
                "explorers": [
                    "https://doc.kmd.dev/tx/"
                ],
                "electrums": [
                    "electrum1.cipig.net:10017",
                    "electrum2.cipig.net:10017",
                    "electrum3.cipig.net:10017"
                ],
                "electrums_ssl": [
                    "electrum1.cipig.net:20017",
                    "electrum2.cipig.net:20017",
                    "electrum3.cipig.net:20017"
                ],
                "electrums_wss": [
                    "electrum1.cipig.net:30017",
                    "electrum2.cipig.net:30017",
                    "electrum3.cipig.net:30017"
                ],
                "mm2_compatible": 1,
                "dpow_active": 1
            }
        }
    ]
}
```
</collapse-text>



## /api/info/notary_rewards/

**rewards information**

The `/api/info/notary_rewards/` endpoint shows the sum of unclaimed active user rewards pending for each notary address.

::: tip
The notary rewards endpoint also displays the block height of your oldest UTXO, which can be used import a private key without needing to rescan the whole blockchain (see [importprivkey](https://developers.komodoplatform.com/basic-docs/smart-chains/smart-chain-api/wallet.html#importprivkey))
:::

### GET parameters

| Name              | Type                 | Description                                                           |
| ----------------- | -------------------- | --------------------------------------------------------------------- |
| notary            | (string, optional)   | Filter results to return rewards for a specific Notary Operator       |
| address           | (string, optional)   | Filter results to return rewards for a specific Address               |

### Response

| Name                                       | Type      | Description                                                           |
| ------------------------------------------ | --------- | --------------------------------------------------------------------- |
| count                                      | (integer) | Number of results matching the filter                                 |
| results                                    | (json)    | A json list of source table rows of notarised transaction information |
| results.season                             | (json)    | The name of the address owner (as a key)                              |
| results.season.notary                      | (json)    | Ticker for all dPoW protected coins                                   |
| results.season.notary.address              | (string)  | Notary Node wallet address for the season                             |
| results.season.notary.notary               | (string)  | Name of notary in ownership of wallet address                         |
| results.season.notary.utxo_count           | (string)  | Number of unspent transaction outputs in the wallet address           |
| results.season.notary.eligible_utxo_count  | (string)  | Number of unspent transaction outputs eligible for rewards            |
| results.season.notary.oldest_utxo_block    | (integer) | The block height of the oldest UTXO in the wallet address             | 
| results.season.notary.balance              | (integer) | Balance of the Notary Node wallet address for the season              |
| results.season.notary.rewards              | (date)    | Sum value of the unclaimed active user rewards for the wallet address |
| results.season.notary.update_time          | (integer) | Timestamp when rewards data for wallet address was last updated       |

#### :pushpin: Examples

URL:

```bash
http://notary.earth:8762/info/notary_rewards/?notary=dragonhound_NA
```

<collapse-text hidden title="Response">

```json
{
    "count": 1,
    "results": [
        {
            "Season_3": {
                "dragonhound_NA": {
                    "RRfUCLxfT5NMpxsC9GHVbdfVy5WJnJFQLV": {
                        "utxo_count": 20341,
                        "eligible_utxo_count": 1,
                        "oldest_utxo_block": 1572256,
                        "balance": 1884.86390212,
                        "rewards": 0.0007828,
                        "update_time": 1588665302
                    },
                    "RHCTCqY5dwLUibLPE2iPnTbaMVzEA4LPML": {
                        "utxo_count": 614,
                        "eligible_utxo_count": 0,
                        "oldest_utxo_block": 1828599,
                        "balance": 5.45998508,
                        "rewards": 0.0,
                        "update_time": 1588665321
                    }
                }
            }
        }
    ]
}
```
</collapse-text>



## /api/info/notary_nodes/

**Notary Node Operator Names**

The `/api/info/notary_nodes/` endpoint is a simple list of Notary Node Operator names for each season

### GET parameters

| Name              | Type                 | Description                                                           |
| ----------------- | -------------------- | --------------------------------------------------------------------- |
| season            | (string, optional)   | Filter results to return notary names for a specific Notary Season    |

### Response

| Name                                 | Type      | Description |
| ------------------------------------ | --------- | ----------------------------------------------------- |
| count                                | (integer) | Number of results matching the filter                 |
| results                              | (json)    | A list of Notary Node seasons                         |
| results.season                       | (list)    | A list of Notary Node names for the season            |

#### :pushpin: Examples

URL:

```bash
http://notary.earth:8762/info/notary_nodes/?season=Season_3
```

<collapse-text hidden title="Response">

```json
{
    "count": 1,
    "results": [
        {
            "Season_3": [
                "alien_AR",
                "alien_EU",
                "alright_AR",
                "and1-89_EU",
                "blackjok3r_SH",
                "ca333_DEV",
                "chainmakers_EU",
                "chainmakers_NA",
                "chainstrike_SH",
                "chainzilla_SH",
                "chmex_EU",
                "cipi_AR",
                "cipi_NA",
                "computergenie_NA",
                "cryptoeconomy_EU",
                "d0ct0r_NA",
                "decker_AR",
                "decker_DEV",
                "dragonhound_NA",
                "dwy_EU",
                "dwy_SH",
                "etszombi_AR",
                "etszombi_EU",
                "fullmoon_AR",
                "fullmoon_NA",
                "fullmoon_SH",
                "gt_AR",
                "indenodes_AR",
                "indenodes_EU",
                "indenodes_NA",
                "indenodes_SH",
                "infotech_DEV",
                "jeezy_EU",
                "karasugoi_NA",
                "kolo_DEV",
                "komodopioneers_EU",
                "komodopioneers_SH",
                "lukechilds_AR",
                "lukechilds_NA",
                "madmax_AR",
                "madmax_NA",
                "metaphilibert_AR",
                "metaphilibert_SH",
                "node-9_EU",
                "nutellalicka_SH",
                "patchkez_SH",
                "pbca26_NA",
                "peer2cloud_AR",
                "phba2061_EU",
                "phm87_SH",
                "pirate_AR",
                "pirate_EU",
                "pirate_NA",
                "pungocloud_SH",
                "strob_NA",
                "thegaltmines_NA",
                "titomane_AR",
                "titomane_EU",
                "titomane_SH",
                "tonyl_AR",
                "voskcoin_EU",
                "webworker01_NA",
                "webworker01_SH",
                "zatjum_SH"
            ]
        }
    ]
}
```
</collapse-text>



## /api/mined_stats/daily/

**Mining information by day**

The `/api/mined_stats/daily/` endpoint


::: tip
Using the `from_date` and `to_date` parameters might be slow or unresponsive if the range is too wide.
:::

### GET parameters

| Name              | Type                 | Description                                                                  |
| ----------------- | -------------------- | ---------------------------------------------------------------------------- |
| mined_date        | (date, optional)     | Filter results to return mining info for a specific date (defaults to today) |
| notary            | (string, optional)   | Filter results to return mining info for a specific Notary Node              |
| from_date         | (date, optional)     | Filter results to return data from a specific date                           |
| to_date           | (date, optional)     | Filter results to return data to a specific date                             |

### Response

| Name                                 | Type      | Description |
| ------------------------------------ | --------- | ----------------------------------------------------- |
| count                                | (integer) | Number of results matching the filter                 |
| next                                 | (url)     | Link to next day's results                            |
| previous                             | (url)     | Link to previous day's results                        |
| results                              | (json)    | A list of dates                                       |
| results.date                         | (json)    | List of Notary Nodes for the date                     |
| results.date.notary                  | (string)  | Name of Notary Node                                   |
| results.date.notary.blocks_mined     | (string)  | Number of blocks mined by Notary Node for the date    |
| results.date.notary.sum_value_mined  | (float)   | Sum value of blocks mined by Notary Node for the date |
| results.date.notary.time_stamp       | (float)   | Timestamp of last update                              |

#### :pushpin: Examples

URL:

```bash
http://notary.earth:8762/mined_stats/daily/?mined_date=2020-05-11&notary=node-9_EU
```

<collapse-text hidden title="Response">

```json
{
    "count": 1,
    "next": "http://notary.earth:8762/mined_count_date/?mined_date=2020-05-12",
    "previous": "http://notary.earth:8762/mined_count_date/?mined_date=2020-05-10",
    "results": [
        {
            "2020-05-11": {
                "node-9_EU": {
                    "blocks_mined": 19,
                    "sum_value_mined": 57.03936743,
                    "time_stamp": 1589215741
                }
            }
        }
    ]
}
```
</collapse-text>



## /api/chain_stats/daily/

**Notarisation counts for each chain grouped by date**

The `/api/chain_stats/daily/` endpoint


::: tip
Using the `from_date` and `to_date` parameters might be slow or unresponsive if the range is too wide.
:::

### GET parameters

| Name              | Type                 | Description                                                                          |
| ----------------- | -------------------- | ------------------------------------------------------------------------------------ |
| notarised_date    | (date, optional)     | Filter results to return notarisation counts for a specific date (defaults to today) |
| chain             | (string, optional)   | Filter results to return notarisation counts for a specific chain                    |
| season            | (string, optional)   | Filter results to return notarisation counts for a specific Notary season            |
| from_date         | (date, optional)     | Filter results to return data from a specific date                           |
| to_date           | (date, optional)     | Filter results to return data to a specific date                             |

### Response

| Name                           | Type      | Description                                           |
| ------------------------------ | --------- | ----------------------------------------------------- |
| count                          | (integer) | Number of results matching the filter                 |
| next                           | (url)     | Link to next day's results                            |
| previous                       | (url)     | Link to previous day's results                        |
| results                        | (json)    | A list of dates                                       |
| results.date                   | (date)    | List of Notary Nodes for the date                     |
| results.date.chain             | (string)  | Name of Notary Node                                   |

#### :pushpin: Examples

URL:

```bash
http://notary.earth:8762/chain_stats/daily/?notarised_date=2019-07-27&chain=CHIPS
```

<collapse-text hidden title="Response">

```json
{
    "count": 1,
    "next": "http://notary.earth:8762/chain_stats/daily/?notarised_date=2019-07-28",
    "previous": "http://notary.earth:8762/chain_stats/daily/?notarised_date=2019-07-26",
    "results": [
        {
            "2019-07-27": {
                "CHIPS": 74
            }
        }
    ]
}
```
</collapse-text>


## /api/notary_stats/daily/

**notarised information**

The `/api/notary_stats/daily/` endpoint


### GET parameters

| Name              | Type                 | Description                                                                          |
| ----------------- | -------------------- | ------------------------------------------------------------------------------------ |
| notarised_date    | (date, optional)     | Filter results to return notarisation counts for a specific date (defaults to today) |
| notary            | (string, optional)   | Filter results to return notarisation counts for a Notary Node                       |
| from_date         | (date, optional)     | Filter results to return data from a specific date                                   |
| to_date           | (date, optional)     | Filter results to return data to a specific date                                     |

### Response

| Name                                   | Type      | Description                                                        |
| -------------------------------------- | --------- | ------------------------------------------------------------------ |
| count                                  | (integer) | Number of results matching the filter                              |
| next                                   | (url)     | Link to next day's results                                         |
| previous                               | (url)     | Link to previous day's results                                     |
| results                                | (json)    | A list of dates                                                    |
| results.date                           | (json)    | List of Notary Nodes for the date                                  |
| results.date.notary                    | (string)  | Name of Notary Node                                                |
| results.date.notary.btc_count          | (integer) | Total KMD -> BTC notarisation transactions                         |
| results.date.notary.antara_count       | (integer) | Total Antara smartchain -> KMD notarisation transactions           |
| results.date.notary.third_party_count  | (integer) | Total Third Party chain -> KMD notarisation transactions           |
| results.date.notary.other_count        | (integer) | Total Other -> KMD notarisation transactions (testing, not scored) |
| results.date.notary.total_ntx_count    | (integer) | Total notarisation transactions                                    |
| results.date.notary.time_stamp         | (integer) | Last update time                                                   |
| results.date.notary.chains             | (json)    | A list of dPoW protected chains                                    |
| results.date.notary.chains.count       | (integer) | Total notarisation transactions for chain                          |
| results.date.notary.chains.percentage  | (float) | Percentage of global notarisation transaction for chain              |


#### :pushpin: Examples

URL:

```bash
http://notary.earth:8762/notary_stats/daily/?notarised_date=2020-04-20&notary=computergenie_NA
```

<collapse-text hidden title="Response">

```json
{
    "count": 1,
    "next": "http://notary.earth:8762/notary_stats/daily/?notarised_date=2020-04-21",
    "previous": "http://notary.earth:8762/notary_stats/daily/?notarised_date=2020-04-19",
    "results": [
        {
            "2020-04-20": {
                "computergenie_NA": {
                    "btc_count": 28,
                    "antara_count": 1004,
                    "third_party_count": 156,
                    "other_count": 0,
                    "total_ntx_count": 1188,
                    "time_stamp": 1589193077,
                    "chains": {
                        "AYA": {
                            "count": 46,
                            "percentage": 46.46
                        },
                        "BET": {
                            "count": 54,
                            "percentage": 40.3
                        },
                        "CCL": {
                            "count": 7,
                            "percentage": 31.82
                        },
                        "DEX": {
                            "count": 34,
                            "percentage": 27.87
                        },
                        "GIN": {
                            "count": 33,
                            "percentage": 27.5
                        },
                        "ILN": {
                            "count": 54,
                            "percentage": 38.85
                        },
                        "KMD": {
                            "count": 28,
                            "percentage": 20.0
                        },
                        "MGW": {
                            "count": 51,
                            "percentage": 38.64
                        },
                        "OOT": {
                            "count": 40,
                            "percentage": 38.1
                        },
                        "OUR": {
                            "count": 40,
                            "percentage": 28.17
                        },
                        "PGT": {
                            "count": 1,
                            "percentage": 100.0
                        },
                        "THC": {
                            "count": 60,
                            "percentage": 41.1
                        },
                        "BOTS": {
                            "count": 49,
                            "percentage": 35.0
                        },
                        "EMC2": {
                            "count": 11,
                            "percentage": 11.7
                        },
                        "GAME": {
                            "count": 9,
                            "percentage": 16.67
                        },
                        "HODL": {
                            "count": 36,
                            "percentage": 27.91
                        },
                        "REVS": {
                            "count": 43,
                            "percentage": 33.33
                        },
                        "RFOX": {
                            "count": 43,
                            "percentage": 48.31
                        },
                        "DOC": {
                            "count": 37,
                            "percentage": 30.08
                        },
                        "VRSC": {
                            "count": 11,
                            "percentage": 9.57
                        },
                        "ZEXO": {
                            "count": 53,
                            "percentage": 33.97
                        },
                        "CHIPS": {
                            "count": 1,
                            "percentage": 2.0
                        },
                        "HUSH3": {
                            "count": 56,
                            "percentage": 53.85
                        },
                        "MARTY": {
                            "count": 43,
                            "percentage": 33.08
                        },
                        "WLC21": {
                            "count": 41,
                            "percentage": 32.03
                        },
                        "CRYPTO": {
                            "count": 36,
                            "percentage": 28.12
                        },
                        "ETOMIC": {
                            "count": 2,
                            "percentage": 40.0
                        },
                        "JUMBLR": {
                            "count": 46,
                            "percentage": 36.51
                        },
                        "MSHARK": {
                            "count": 45,
                            "percentage": 35.43
                        },
                        "PANGEA": {
                            "count": 43,
                            "percentage": 34.13
                        },
                        "PIRATE": {
                            "count": 46,
                            "percentage": 30.87
                        },
                        "SUPERNET": {
                            "count": 47,
                            "percentage": 36.72
                        },
                        "VOTE2020": {
                            "count": 10,
                            "percentage": 62.5
                        },
                        "COQUICASH": {
                            "count": 32,
                            "percentage": 24.43
                        }
                    }
                }
            }
        }
    ]
}
```
</collapse-text>


























## /api/mined_stats/season/

**Season aggregated mining data**

The `/api/mined_stats/season/` endpoint shows aggregated mining information for each season and notary node.


### GET parameters

| Name              | Type                 | Description                                                           |
| ----------------- | -------------------- | --------------------------------------------------------------------- |
| notary            | (string, optional)   | Filter results to return mining info for a Notary Node in each season |
| season            | (string, optional)   | Filter results to return mining info for a specific Notary season     |

### Response

| Name                                   | Type      | Description                                             |
| -------------------------------------- | --------- | --------------------------------------------------------- |
| count                                  | (integer) | Number of results matching the filter                     |
| results                                | (json)    | A list of seasons                                         |
| results.season                         | (json)    | List of Notary Nodes for the season                       |
| results.season.notary                  | (string)  | Name of Notary Node                                       |
| results.season.notary.blocks_mined     | (integer) | Number of blocks mined by Notary Node for the season      |
| results.season.notary.sum_value_mined  | (float)   | Sum value of blocks mined by Notary Node for the season   |
| results.season.notary.max_value_mined  | (float)   | Value of largest block mined by Notary Node in the season |
| results.season.notary.sum_value_mined  | (float)   | Sum value of blocks mined by Notary Node for the season   |
| results.season.notary.sum_value_mined  | (float)   | Sum value of blocks mined by Notary Node for the season   |
| results.season.notary.time_stamp       | (integer) | Timestamp of last update                                  |

#### :pushpin: Examples

URL:

```bash
http://notary.earth:8762/mined_stats/season/?notary=komodopioneers_SH
```

<collapse-text hidden title="Response">

```json
{
    "count": 3,
    "results": [
        {
            "Season_1": {
                "komodopioneers_SH": {
                    "blocks_mined": 1152,
                    "sum_value_mined": 3476.67063497,
                    "max_value_mined": 8.29459686,
                    "last_mined_block": 909931,
                    "last_mined_blocktime": 1530915345,
                    "time_stamp": 1589198631
                }
            },
            "Season_2": {
                "komodopioneers_SH": {
                    "blocks_mined": 5985,
                    "sum_value_mined": 18885.05669644,
                    "max_value_mined": 611.17373324,
                    "last_mined_block": 1443056,
                    "last_mined_blocktime": 1563144724,
                    "time_stamp": 1589198673
                }
            },
            "Season_3": {
                "komodopioneers_SH": {
                    "blocks_mined": 4780,
                    "sum_value_mined": 16828.85130682,
                    "max_value_mined": 2386.02913723,
                    "last_mined_block": 1873076,
                    "last_mined_blocktime": 1589203985,
                    "time_stamp": 1589209576
                }
            }
        }
    ]
}
```
</collapse-text>

## /api/chain_stats/season/

**Notarisation counts for each chain grouped by season**

The `/api/chain_stats/season/` endpoint

### GET parameters

| Name              | Type                 | Description                                                           |
| ----------------- | -------------------- | --------------------------------------------------------------------- |
| season            | (string, optional)   | Filter results to return notarisations for a specific Notary Season   |
| chain             | (string, optional)   | Filter results to return notarisations for a specific Coin            |

### Response

| Name                                    | Type      | Description                                                        |
| --------------------------------------- | --------- | ------------------------------------------------------------------ |
| count                                   | (integer) | Number of results matching the filter                              |
| results                                 | (json)    | A json list of aggregated notarisation information for each season |
| results.season                          | (json)    | Notary seasons (as a json key)                                     |
| results.season.chain                    | (json)    | dPoW protected chains (as a key)                                   |
| results.season.chain.ntx_count          | (integer) | Season notarisation transactions count season for chain            |
| results.season.chain.kmd_ntx_height     | (integer) | KMD block height of most recent notarisation for chain             |
| results.season.chain.kmd_ntx_blockhash  | (string)  | KMD block hash of most recent notarisation for chain               |
| results.season.chain.kmd_ntx_txid       | (string)  | KMD transaction ID of most recent notarisation for chain           |
| results.season.chain.kmd_ntx_blocktime  | (integer) | KMD block timestamp of most recent notarisation for chain          |
| results.season.chain.ac_ntx_height      | (integer) | dPow chain block height of most recent notarisation                |
| results.season.chain.ac_ntx_blockhash   | (string)  | dPow chain block hash of most recent notarisation                  |
| results.season.chain.ac_block_height    | (string)  | dPow chain transaction ID of most recent notarisation              |
| results.season.chain.opret              | (string)  | Encoded OP_RETURN forn the KMD notarisation transaction            |
| results.season.chain.ntx_lag            | (integer) | Number of blocks passed on dPoW chain since a notarisation         |


#### :pushpin: Examples

URL:

```bash
http://notary.earth:8762/chain_stats/season/?season=Season_3&chain=RFOX
```

<collapse-text hidden title="Response">

```json
{
    "count": 1,
    "results": [
        {
            "Season_3": {
                "RFOX": {
                    "ntx_count": 27759,
                    "kmd_ntx_height": 1873977,
                    "kmd_ntx_blockhash": "0000000128bdf74e4b5a40d6f7e6a9854b7bea6fe9170aa4da92d8ff5eccf609",
                    "kmd_ntx_txid": "512066aa16cb79819ec58586cb456890973d925853425b26dd33f2fc07fb8c46",
                    "kmd_ntx_blocktime": 1589259852,
                    "ac_ntx_blockhash": "00000262ecfe5ff11349e0711437863bc1e6718198a48adf89ee9fcec1eb46e4",
                    "ac_ntx_height": 977780,
                    "ac_block_height": "977792",
                    "opret": "OP_RETURN e446ebc1ce9fee89df8aa4988171e6c13b86371471e04913f15ffeec6202000074eb0e0052464f580024095d2bc4c281a935b9d1d916069094065a99c37993d113949b6c5f5da7b9f90a000000",
                    "ntx_lag": "12"
                }
            }
        }
    ]
}
```
</collapse-text>

## /api/notary_stats/season/

**Notarisation counts for each notary node grouped by season**

The `/api/notary_stats/season/` endpoint

### GET parameters

| Name              | Type                 | Description                                                           |
| ----------------- | -------------------- | --------------------------------------------------------------------- |
| notary            | (string, optional)   | Filter results to return notarisation counts for a Notary Node                       |
| season            | (string, optional)   | Filter results to return notarisation counts for a specific Notary season            |

### Response

| Name                                     | Type      | Description                                                        |
| ---------------------------------------- | --------- | ------------------------------------------------------------------ |
| count                                    | (integer) | Number of results matching the filter                              |
| results                                  | (json)    | A list of seasons                                                  |
| results.season                           | (json)    | List of Notary Nodes for the season                                |
| results.season.notary                    | (string)  | Name of Notary Node                                                |
| results.season.notary.btc_count          | (integer) | Total KMD -> BTC notarisation transactions                         |
| results.season.notary.antara_count       | (integer) | Total Antara smartchain -> KMD notarisation transactions           |
| results.season.notary.third_party_count  | (integer) | Total Third Party chain -> KMD notarisation transactions           |
| results.season.notary.other_count        | (integer) | Total Other -> KMD notarisation transactions (testing, not scored) |
| results.season.notary.total_ntx_count    | (integer) | Total notarisation transactions                                    |
| results.season.notary.time_stamp         | (integer) | Last update time                                                   |
| results.season.notary.chains             | (json)    | A list of dPoW protected chains                                    |
| results.season.notary.chains.count       | (integer) | Total notarisation transactions for chain                          |
| results.season.notary.chains.percentage  | (float)   | Percentage of global notarisation transaction for chain            |

#### :pushpin: Examples

URL:

```bash
http://notary.earth:8762/notary_stats/season/?notary=alien_AR&season=Season_3
```

<collapse-text hidden title="Response">

```json
{
    "count": 1,
    "results": [
        {
            "Season_3": {
                "alien_AR": {
                    "btc_count": 19666,
                    "antara_count": 357174,
                    "third_party_count": 57987,
                    "other_count": 0,
                    "total_ntx_count": 434827,
                    "time_stamp": 1589263037,
                    "chains": {
                        "KV": {
                            "count": 4102,
                            "percentage": 28.79
                        },
                        "AXO": {
                            "count": 4484,
                            "percentage": 32.36
                        },
                        "AYA": {
                            "count": 2312,
                            "percentage": 71.51
                        },
                        "BET": {
                            "count": 10406,
                            "percentage": 28.67
                        },
                        "CCL": {
                            "count": 2883,
                            "percentage": 32.53
                        },
                        "DEX": {
                            "count": 11039,
                            "percentage": 30.93
                        },
                        "EQL": {
                            "count": 4394,
                            "percentage": 31.7
                        },
                        "GIN": {
                            "count": 13273,
                            "percentage": 40.55
                        },
                        "ILN": {
                            "count": 7575,
                            "percentage": 30.11
                        },
                        "K64": {
                            "count": 5971,
                            "percentage": 30.66
                        },
                        "KMD": {
                            "count": 19666,
                            "percentage": 46.18
                        },
                        "KSB": {
                            "count": 3518,
                            "percentage": 28.59
                        },
                        "MCL": {
                            "count": 171,
                            "percentage": 32.26
                        },
                        "MGW": {
                            "count": 10838,
                            "percentage": 28.6
                        },
                        "OOT": {
                            "count": 9439,
                            "percentage": 30.72
                        },
                        "OUR": {
                            "count": 13255,
                            "percentage": 32.13
                        },
                        "PGT": {
                            "count": 4166,
                            "percentage": 29.67
                        },
                        "SEC": {
                            "count": 4324,
                            "percentage": 31.49
                        },
                        "THC": {
                            "count": 13548,
                            "percentage": 32.67
                        },
                        "WLC": {
                            "count": 4126,
                            "percentage": 30.13
                        },
                        "BNTN": {
                            "count": 3937,
                            "percentage": 29.13
                        },
                        "BOTS": {
                            "count": 10632,
                            "percentage": 28.8
                        },
                        "BTCH": {
                            "count": 2363,
                            "percentage": 27.63
                        },
                        "CEAL": {
                            "count": 3781,
                            "percentage": 28.29
                        },
                        "DION": {
                            "count": 7540,
                            "percentage": 31.7
                        },
                        "DSEC": {
                            "count": 4084,
                            "percentage": 30.12
                        },
                        "EMC2": {
                            "count": 13035,
                            "percentage": 44.55
                        },
                        "GAME": {
                            "count": 7707,
                            "percentage": 41.68
                        },
                        "GLXT": {
                            "count": 40,
                            "percentage": 18.6
                        },
                        "HODL": {
                            "count": 10922,
                            "percentage": 30.05
                        },
                        "KOIN": {
                            "count": 4025,
                            "percentage": 28.94
                        },
                        "MESH": {
                            "count": 3947,
                            "percentage": 29.02
                        },
                        "REVS": {
                            "count": 11083,
                            "percentage": 29.43
                        },
                        "RFOX": {
                            "count": 7539,
                            "percentage": 27.16
                        },
                        "DOC": {
                            "count": 13602,
                            "percentage": 34.52
                        },
                        "STBL": {
                            "count": 30,
                            "percentage": 60.0
                        },
                        "VRSC": {
                            "count": 12282,
                            "percentage": 33.01
                        },
                        "ZEXO": {
                            "count": 13594,
                            "percentage": 32.02
                        },
                        "CHAIN": {
                            "count": 4899,
                            "percentage": 30.04
                        },
                        "CHIPS": {
                            "count": 9457,
                            "percentage": 48.33
                        },
                        "HUSH3": {
                            "count": 12203,
                            "percentage": 43.86
                        },
                        "MARTY": {
                            "count": 14091,
                            "percentage": 35.42
                        },
                        "NINJA": {
                            "count": 3808,
                            "percentage": 27.73
                        },
                        "WLC21": {
                            "count": 8531,
                            "percentage": 33.59
                        },
                        "ZILLA": {
                            "count": 5162,
                            "percentage": 30.27
                        },
                        "COMMOD": {
                            "count": 3116,
                            "percentage": 30.75
                        },
                        "CRYPTO": {
                            "count": 11601,
                            "percentage": 30.64
                        },
                        "ETOMIC": {
                            "count": 2719,
                            "percentage": 30.19
                        },
                        "JUMBLR": {
                            "count": 10771,
                            "percentage": 28.61
                        },
                        "KMDICE": {
                            "count": 7665,
                            "percentage": 31.23
                        },
                        "MSHARK": {
                            "count": 10813,
                            "percentage": 28.38
                        },
                        "PANGEA": {
                            "count": 10994,
                            "percentage": 29.08
                        },
                        "PIRATE": {
                            "count": 11950,
                            "percentage": 31.36
                        },
                        "PRLPAY": {
                            "count": 4516,
                            "percentage": 31.65
                        },
                        "SUPERNET": {
                            "count": 10692,
                            "percentage": 30.28
                        },
                        "VOTE2020": {
                            "count": 394,
                            "percentage": 64.7
                        },
                        "COQUICASH": {
                            "count": 11812,
                            "percentage": 35.35
                        }
                    }
                }
            }
        }
    ]
}
```
</collapse-text>




















## /api/source/notarised/

**notarisation information**

The `/api/source/notarised/` endpoint contains information decoded from OP_RETURN messages within notarisation transactions.

### GET parameters

| Name            | Type                 | Description                                                                         |
| --------------- | -------------------- | ----------------------------------------------------------------------------------- |
| season          | (string, optional)   | Filter results to return notarisations for a specific Notary season                 |
| chain           | (string, optional)   | Filter results to return notarisations for a specific Coin                          |
| block_height    | (integer, optional)  | Filter results to return notarisations for a KMD block height                       |
| min_block       | (integer, optional)  | Filter results to return notarisations after a KMD block height (inclusive)         |
| max_block       | (integer, optional)  | Filter results to return notarisations before a KMD block height (inclusive)        |
| min_ac_block    | (integer, optional)  | Filter results to return notarisations after a KMD block time (inclusive)           |
| max_ac_block    | (integer, optional)  | Filter results to return notarisations before a KMD block time (inclusive)          |
| min_blocktime   | (integer, optional)  | Filter results to return notarisations after a dPoW chain block height (inclusive)  |
| min_blocktime   | (integer, optional)  | Filter results to return notarisations before a dPoW chain block height (inclusive) |

### Response

| Name                         | Type      | Description                                                                     |
| ---------------------------- | --------- | ------------------------------------------------------------------------------- |
| count                        | (integer) | Number of results matching the filter                                           |
| results                      | (json)    | A json list of source table rows of notarised transaction information           |
| results.txid                 | (string)  | KMD Transaction ID of the notarisation                                          |
| results.chain                | (string)  | The chain being secured by dPoW                                                 |
| results.block_hash           | (string)  | The block hash of the KMD block containing the notarisation transaction         |
| results.block_height         | (integer) | The block height of the KMD block containing the notarisation transaction       |
| results.block_time           | (integer) | Unix timestamp of the KMD block containing the notarisation transaction         |
| results.block_datetime       | (date)    | ISO 8601 date/time of the KMD block containing the notarisation transaction     |
| results.notaries             | (list)    | List of 13 notary operators participating in the notarisation                   |
| results.ac_ntx_blockhash     | (string)  | The OP_RETURN decoded block hash of the chain being protected by dPoW           |
| results.ac_ntx_height        | (string)  | The OP_RETURN decoded block height of the chain being protected by dPoW         |
| results.opret                | (string)  | Raw OP_RETURN string from the KMD notarisation transaction                      |
| results.season               | (string)  | Notary Season during which the notarisation occurred                            |


#### :pushpin: Examples

URL:

```bash
http://notary.earth:8762/source/notarised/?chain=DEX&block_height=1872716
```

<collapse-text hidden title="Response">

```json
        {
            "txid": "99b97364d9f1def303d311ee61997f206c9d92fc3a0da074343a39353e53ef7d",
            "chain": "DEX",
            "block_height": 1872716,
            "block_time": 1589182233,
            "block_datetime": "2020-05-11T07:30:33Z",
            "block_hash": "000000003e7d335db8f82f7f12a585c7a40d703fc2e9c44af4ef73fcfa95415a",
            "ac_ntx_blockhash": "0015dce9f2bf620355bcb366dd8901d6c2716c1639e0605b089c67396e6d1665",
            "ac_ntx_height": 1117488,
            "opret": "OP_RETURN 65166d6e39679c085b60e039166c71c2d60189dd66b3bc550362bff2e9dc1500300d110044455800cd99fda04cc2990170697b82a99eef90f947b3f2f9e82d2edb782baaabebbd3c04000000",
            "notaries": [
                "alien_EU",
                "chainmakers_NA",
                "cipi_NA",
                "decker_AR",
                "fullmoon_AR",
                "fullmoon_NA",
                "fullmoon_SH",
                "gt_AR",
                "indenodes_NA",
                "infotech_DEV",
                "karasugoi_NA",
                "madmax_NA",
                "titomane_EU"
            ],
            "season": "Season_3"
        }
```
</collapse-text>


## /api/source/mined/

**mining information**

The `/api/source/mined/` endpoint returns the address / notary mining information

### GET parameters

| Name            | Type                 | Description                                                                        |
| --------------- | -------------------- | ---------------------------------------------------------------------------------- |
| name            | (string, optional)   | Filter results to return blocks mined by a specific Notary Operator                |
| address         | (string, optional)   | Filter results to return blocks mined by a specific Address                        |
| season          | (string, optional)   | Filter results to return blocks mined in a specific Notary Season                  |
| block_height    | (integer, optional)  | Filter results to return mining information about a specific Block                 |
| min_block       | (integer, optional)  | Filter results to return blocks mined after a KMD block height (inclusive)         |
| max_block       | (integer, optional)  | Filter results to return blocks mined before a KMD block height (inclusive)        |
| min_blocktime   | (integer, optional)  | Filter results to return blocks mined after a dPoW chain block height (inclusive)  |
| min_blocktime   | (integer, optional)  | Filter results to return blocks mined before a dPoW chain block height (inclusive) |

### Response

| Name                         | Type      | Description                                                                     |
| ---------------------------- | --------- | ------------------------------------------------------------------------------- |
| count                        | (integer) | Number of results matching the filter                                           |
| results                      | (json)    | A json list of source table rows of notarised transaction information           |
| results.txid                 | (string)  | Transaction ID of the mined block                                               |
| results.block_hash           | (string)  | The block hash of the block containing the mined transaction                    |
| results.block_height         | (integer) | The block height of the block containing the mined transaction                  |
| results.block_time           | (integer) | Unix timestamp of the block containing the mined transaction                    |
| results.block_datetime       | (date)    | ISO 8601 date/time of the block containing the mined transaction                |
| results.name                 | (string)  | Name of notary (or pool operator) who mined the block                           |
| results.value                | (integer) | Value in KMD of he mined block                                                  |
| results.address              | (string)  | Receiving address of the mined block                                            |
| results.season               | (string)  | Notary Season during which the mined block occurred                             |

#### :pushpin: Examples

URL:

```bash
http://notary.earth:8762/source/mined/?block_height=1872522
```

<collapse-text hidden title="Response">

```json
        {
            "block_height": 1872522,
            "block_time": 1589171052,
            "block_datetime": "2020-05-11T04:24:12Z",
            "value": "3.00041200",
            "address": "RSKDECKERyuopK3gd3SQHH9qkngsfWrjXy",
            "name": "decker_AR",
            "txid": "a36ebaee17fce8f4341ce2011c3a750bb7cb83a5cc4ab1f496f2cd787fd4ba19",
            "season": "Season_3"
        }
```
</collapse-text>
























## /api/tools/decode_opreturn/

**Notarisation counts for each notary node grouped by season**

The `/api/tools/decode_opreturn/` endpoint

### GET parameters

| Name              | Type                 | Description                                                           |
| ----------------- | -------------------- | --------------------------------------------------------------------- |
| OP_RETURN         | (string, required)   | OP_RETURN string (from notarisation transaction) to be decoded        |

### Response

| Name                           | Type      | Description                                      |
| ------------------------------ | --------- | ------------------------------------------------ |
| results.chain                 | (string)  | The chain being notarised                        |
| results.notarised_block       | (string)  | dPow chain block height of this notarisation     |
| results.notarised_blockhash   | (integer) | dPow chain block hash of this notarisation       |

#### :pushpin: Examples

URL:

```bash
http://notary.earth:8762/tools/decode_opreturn/?OP_RETURN=f29d08e9f3460c8a21ba5f1ba0bd66fcfbd95c9f8facf8b86138ae5c6131f601f8b3110053555045524e45540028ba17b90d6278909fa77a4fe4aa1a099791cc4516531616b240956b35bfa80706000000
```

<collapse-text hidden title="Response">

```json
{
    "chain": "SUPERNET",
    "notarised_block": 1160184,
    "notarised_blockhash": "01f631615cae3861b8f8ac8f9f5cd9fbfc66bda01b5fba218a0c46f3e9089df2"
}
```
</collapse-text>
