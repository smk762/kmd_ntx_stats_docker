def default_swap_totals():
	return {
	    "taker": {
	        "swap_total": 0,
	        "pubkey_total": 0,
	        "desktop": {"swap_total": 0, "swap_pct":0, "pubkey_total": 0},
	        "android": {"swap_total": 0, "swap_pct":0, "pubkey_total": 0},
	        "ios": {"swap_total": 0, "swap_pct":0, "pubkey_total": 0},
	        "dogedex": {"swap_total": 0, "swap_pct":0, "pubkey_total": 0},
	        "other": {"swap_total": 0, "swap_pct":0, "pubkey_total": 0}
	    },
	    "maker": {
	        "swap_total": 0,
	        "pubkey_total": 0,
	        "desktop": {"swap_total": 0, "swap_pct":0, "pubkey_total": 0},
	        "android": {"swap_total": 0, "swap_pct":0, "pubkey_total": 0},
	        "ios": {"swap_total": 0, "swap_pct":0, "pubkey_total": 0},
	        "dogedex": {"swap_total": 0, "swap_pct":0, "pubkey_total": 0},
	        "other": {"swap_total": 0, "swap_pct":0, "pubkey_total": 0}
	    }
	}


def default_regions_info():
	return {
	    'AR':{ 
	        "name": "Asia and Russia",
	        "nodes": []
	        },
	    'EU':{ 
	        "name": "Europe",
	        "nodes": []
	        },
	    'NA':{ 
	        "name": "North America",
	        "nodes": []
	        },
	    'SH':{ 
	        "name": "Southern Hemisphere",
	        "nodes": []
	        },
	    'DEV':{ 
	        "name": "Developers",
	        "nodes": []
	        }
	}


def default_top_region_notarisers():
	return {
	    "AR": {},
	    "EU": {},
	    "NA": {},
	    "SH": {},
	    "DEV": {}
	}
