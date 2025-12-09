#!/usr/bin/env python3.12
import os 
import re
import platform
from slickrpc import Proxy
import lib_const
import lib_crypto
from logger import logger

# define data dir
def def_data_dir():
    operating_system = platform.system()
    if operating_system == 'Darwin':
        ac_dir = os.environ['HOME'] + '/Library/Application Support/Komodo'
    elif operating_system == 'Linux':
        ac_dir = os.environ['HOME'] + '/.komodo'
    elif operating_system == 'Windows':
        ac_dir = '%s/komodo/' % os.environ['APPDATA']
    return(ac_dir)

def _env_rpc_credentials():
    """Prefer host KMD RPC credentials from environment."""
    ip = os.getenv("RPC_IP")
    port = os.getenv("RPC_PORT")
    user = os.getenv("RPC_USERNAME")
    password = os.getenv("RPC_PASSWORD")
    if all([ip, port, user, password]):
        return ip, port, user, password
    return None


# function to define rpc_connection
def def_credentials(coin):
    env_creds = _env_rpc_credentials()
    if env_creds:
        rpc_ip, rpcport, rpcuser, rpcpassword = env_creds
    else:
        rpcport = ''
        ac_dir = def_data_dir()
        if coin == 'KMD':
            coin_config_file = str(ac_dir + '/komodo.conf')
        else:
            coin_config_file = str(ac_dir + '/' + coin + '/' + coin + '.conf')
        with open(coin_config_file, 'r') as f:
            for line in f:
                l = line.rstrip()
                if re.search('rpcuser', l):
                    rpcuser = l.replace('rpcuser=', '')
                elif re.search('rpcpassword', l):
                    rpcpassword = l.replace('rpcpassword=', '')
                elif re.search('rpcport', l):
                    rpcport = l.replace('rpcport=', '')
        if len(rpcport) == 0:
            if coin == 'KMD':
                rpcport = 7771
            else:
                logger.info("rpcport not in conf file, exiting")
                logger.info("check " + coin_config_file)
                exit(1)
        rpc_ip = "127.0.0.1"
    try:
        return Proxy(f"http://{rpcuser}:{rpcpassword}@{rpc_ip}:{int(rpcport)}", timeout=300)
    except Exception:
        logger.info("Unable to set RPC proxy, please confirm rpcuser, rpcpassword and rpcport are set in environment or config")

def get_ntx_txids(start, end):
    logger.info(f"Getting nxt txids from blocks {start}-{end}")
    return RPC["KMD"].getaddresstxids({"addresses": [lib_const.NTX_ADDR], "start":start, "end":end})


# KMD RPC Proxy
RPC = {}
for coin in ["KMD"]:
    try:
        RPC[coin] = def_credentials(coin)
    except:
        logger.info(f"{coin} RPC failed")
        pass