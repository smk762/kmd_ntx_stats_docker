#!/usr/bin/env python3
from lib_const import *
from lib_helper import *

def validate_epoch_chains(epoch_chains, season):
    if len(epoch_chains) == 0:
        return False
    for chain in epoch_chains:
        if season in DPOW_EXCLUDED_CHAINS:
            if chain in DPOW_EXCLUDED_CHAINS[season]:
                logger.warning(f"{chain} in DPOW_EXCLUDED_CHAINS[{season}]")
                return False
    return True


def validate_season_server_epoch(season, server, epoch, notary_addresses, block_time, chain, txid, notaries):
    if season in DPOW_EXCLUDED_CHAINS:
        if chain in DPOW_EXCLUDED_CHAINS[season]:
            season = "Unofficial"
            server = "Unofficial"
            epoch = "Unofficial"
    season, server = get_season_server_from_addresses(notary_addresses, chain)
    epoch = get_chain_epoch_at(season, server, chain, block_time)
    return season, server, epoch
