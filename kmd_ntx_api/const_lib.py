
import requests
 # Need to confirm and fill this in correctly later...
seasons_info = {
    "Season_1": {
            "start_block":1,
            "end_block":813999,
            "start_time":1473793441,
            "end_time":1530921600,
            "notaries":[]
        },
    "Season_2": {
            "start_block":814000,
            "end_block":1443999,
            "start_time":1530921600,
            "end_time":1563148799,
            "notaries":[]
        },
    "Season_3": {
            "start_block":1444000,
            "end_block":1921999,
            "start_time":1563148800,
            "end_time":1592146799,
            "notaries":[]
        },
    "Season_4": {
            "start_block":1922000,
            "end_block":2444000,
            "start_time":1592146800,
            "end_time":1751328000,
            "notaries":[]
        }
}

s4_numchains = {
    "1921458": {
        "phase":"S4 start",
        "main": ['KMD', 'BTC', 'AXO', 'BET', 'BOTS', 'BTCH', 'CCL',
                 'COQUICASH', 'CRYPTO', 'DEX', 'HODL', 'ILN', 'JUMBLR',
                 'KOIN', 'MESH', 'MGW', 'MORTY', 'MSHARK', 'NINJA', 'OOT',
                 'PANGEA', 'PGT', 'PIRATE', 'REVS', 'RFOX', 'RICK', 'STBL',
                 'SUPERNET', 'THC', 'WLC21', 'ZILLA'],
        "third party": ['AYA', 'CHIPS', 'EMC2', 'HUSH3', 'VRSC']
    },
    "1939795": {
        "phase":"add MCL",
        "main": ['KMD', 'BTC', 'AXO', 'BET', 'BOTS', 'BTCH', 'CCL',
                 'COQUICASH', 'CRYPTO', 'DEX', 'HODL', 'ILN', 'JUMBLR',
                 'KOIN', 'MESH', 'MGW', 'MORTY', 'MSHARK', 'NINJA', 'OOT',
                 'PANGEA', 'PGT', 'PIRATE', 'REVS', 'RFOX', 'RICK', 'STBL',
                 'SUPERNET', 'THC', 'WLC21', 'ZILLA'],
        "third party": ['AYA', 'CHIPS', 'EMC2', 'HUSH3', 'MCL', 'VRSC']
    },
}

# convert timestamp to human time 
intervals = (
    ('wks', 604800),  # 60 * 60 * 24 * 7
    ('days', 86400),    # 60 * 60 * 24
    ('hrs', 3600),    # 60 * 60
    ('mins', 60),
    ('sec', 1),
    )

noMoM = ['CHIPS', 'GAME', 'HUSH3', 'EMC2', 'GIN', 'AYA', 'MCL', 'VRSC']

url = "https://raw.githubusercontent.com/gcharang/data/master/info/ecosystem.json"
r = requests.get(url)
eco_data = r.json()