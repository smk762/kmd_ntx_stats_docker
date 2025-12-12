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
    ip = os.getenv("KMD_RPC_IP").split(":")[0] or "127.0.0.1"
    # Disallow binding to 0.0.0.0 for safety; fall back to localhost
    if ip in ["0.0.0.0", ""]:
        ip = "127.0.0.1"
    port = os.getenv("KMD_RPC_PORT")
    user = os.getenv("KMD_RPC_USERNAME")
    password = os.getenv("KMD_RPC_PASSWORD")
    if all([ip, port, user, password]):
        return ip, port, user, password
    if any([ip, port, user, password]):
        logger.info("KMD RPC env vars incomplete; set KMD_RPC_IP, KMD_RPC_PORT, KMD_RPC_USERNAME, KMD_RPC_PASSWORD or ensure komodo.conf is readable")
    return None


# function to define rpc_connection
def def_credentials(coin):
    env_creds = _env_rpc_credentials()
    if env_creds:
        rpc_ip, rpcport, rpcuser, rpcpassword = env_creds
    else:
        rpcport = ''
        rpcuser = None
        rpcpassword = None
        ac_dir = def_data_dir()
        if coin == 'KMD':
            coin_config_file = str(ac_dir + '/komodo.conf')
        else:
            coin_config_file = str(ac_dir + '/' + coin + '/' + coin + '.conf')
        try:
            with open(coin_config_file, 'r') as f:
                for line in f:
                    l = line.rstrip()
                    if re.search('rpcuser', l):
                        rpcuser = l.replace('rpcuser=', '')
                    elif re.search('rpcpassword', l):
                        rpcpassword = l.replace('rpcpassword=', '')
                    elif re.search('rpcport', l):
                        rpcport = l.replace('rpcport=', '')
        except FileNotFoundError:
            logger.info(f"RPC config not found: {coin_config_file}. Set KMD_RPC_IP, KMD_RPC_PORT, KMD_RPC_USERNAME, KMD_RPC_PASSWORD in environment.")
            return None

        if not rpcuser or not rpcpassword:
            logger.info(f"rpcuser/rpcpassword missing in {coin_config_file}. Set KMD_RPC_IP, KMD_RPC_PORT, KMD_RPC_USERNAME, KMD_RPC_PASSWORD in environment.")
            return None

        if len(str(rpcport)) == 0:
            if coin == 'KMD':
                rpcport = 7771
            else:
                logger.info("rpcport not in conf file; set KMD_RPC_PORT env or update config.")
                return None
        rpc_ip = "127.0.0.1"
    try:
        logger.info(f"Setting RPC proxy: http://{rpcuser}:{rpcpassword}@{rpc_ip}:{int(rpcport)}")
        return RestrictedRPC(f"http://{rpcuser}:{rpcpassword}@{rpc_ip}:{int(rpcport)}")
    except Exception as e:
        logger.info(f"Unable to set RPC proxy: {e}. Confirm KMD_RPC_IP/KMD_RPC_PORT/KMD_RPC_USERNAME/KMD_RPC_PASSWORD env or komodo.conf values.")
        return None


class RestrictedRPC:
    """Whitelisted, localhost-only RPC wrapper to avoid unsafe KMD calls."""
    ALLOWED_METHODS = {
        "getblock",
        "getblockcount",
        "getaddresstxids",
        "getrawtransaction",
        "coinsupply",
    }

    def __init__(self, uri: str, timeout: int = 300):
        self._proxy = Proxy(uri, timeout=timeout)

    def __getattr__(self, name):
        if name not in self.ALLOWED_METHODS:
            raise AttributeError(f"RPC method '{name}' is not permitted")
        return getattr(self._proxy, name)

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