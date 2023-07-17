
def get_region_buttons():
    buttons = ["AR", "EU", "NA", "SH", "DEV"]
    return {
        "AR": {
            "action": f"show_card('AR', {buttons})",
            "width_pct": 19,
            "text": "Asia & Russia"
        },
        "EU": {
            "action": f"show_card('EU', {buttons})",
            "width_pct": 19,
            "text": "Europe"
        },
        "NA": {
            "action": f"show_card('NA', {buttons})",
            "width_pct": 19,
            "text": "North America"
        },
        "SH": {
            "action": f"show_card('SH', {buttons})",
            "width_pct": 19,
            "text": "Southern Hemisphere"
        },
        "DEV": {
            "action": f"show_card('DEV', {buttons})",
            "width_pct": 19,
            "text": "Developers"
        }
    }

def get_server_buttons():
    buttons = ["Main", "Third_Party"]
    return {
        "Main": {
            "action": f"show_card('Main', {buttons})",
            "width_pct": 19,
            "text": "Main"
        },
        "Third_Party": {
            "action": f"show_card('Third_Party', {buttons})",
            "width_pct": 19,
            "text": "Third Party"
        }
    }

def get_faucet_buttons():
    buttons = ["faucet_balances", "faucet_history"]
    return {
        "faucet_balances": {
            "action": f"show_card('faucet_balances', {buttons})",
            "width_pct": 17,
            "text": "Faucet Balances"
        },
        "faucet_history": {
            "action": f"show_card('faucet_history', {buttons})",
            "width_pct": 17,
            "text": "Faucet History"
        }
    }

def get_ntx_buttons():
    buttons = ["ntx", "ntx_24hr", "balances", "mining", "last_coin_ntx"]
    return {
        "ntx": {
            "action": f"show_card('ntx', {buttons})",
            "width_pct": 17,
            "text": "Notarisations"
        },
        "ntx_24hr": {
            "action": f"show_card('ntx_24hr', {buttons})",
            "width_pct": 17,
            "text": "Notarisations (24hrs)"
        },
        "balances": {
            "action": f"show_card('balances', {buttons})",
            "width_pct": 17,
            "text": "Addresses"
        },
        "mining": {
            "action": f"show_card('mining', {buttons})",
            "width_pct": 17,
            "text": "Mining"
        },
        "last_coin_ntx": {
            "action": f"show_card('last_coin_ntx', {buttons})",
            "width_pct": 17,
            "text": "Last Coin Ntx"
        }
    }