#!/usr/bin/env python3.12
import os 
import re
import json
import platform
from slickrpc import Proxy
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

# function to define rpc_connection
def def_credentials(coin):
    env_ip = os.getenv("KMD_RPC_IP")
    if env_ip == "0.0.0.0":
        env_ip = "127.0.0.1"
    env_port = os.getenv("KMD_RPC_PORT")
    env_user = os.getenv("KMD_RPC_USERNAME")
    env_password = os.getenv("KMD_RPC_PASSWORD")
    if all([env_ip, env_port, env_user, env_password]):
        rpc_ip, rpcport, rpcuser, rpcpassword = env_ip, env_port, env_user, env_password
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
        return Proxy(f"http://{rpcuser}:{rpcpassword}@{rpc_ip}:{int(rpcport)}", timeout=90)
    except Exception as e:
        logger.info(f"Unable to set RPC proxy: {e}. Confirm KMD_RPC_IP/KMD_RPC_PORT/KMD_RPC_USERNAME/KMD_RPC_PASSWORD env or komodo.conf values.")
        return None




if __name__ == "__main__":
    kmd_rpc = def_credentials("KMD")

    output_addr = "RP81MSVu39QgXhGDHfnk9d9KMnp4vhEVBu"
    output_value = 7.77

    unspent = kmd_rpc.listunspent()



    input_txids = []
    for txid in unspent:
        input_txids.append({"txid":txid["txid"], "vout":txid["vout"]})


    logger.info("komodo-cli createrawtransaction '"+json.dumps(input_txids).replace('"', '\"')+"' '{\""+output_addr+"\":"+str(output_value)+"}'")
