#!/usr/bin/env python3
import os 
import re
import platform
from slickrpc import Proxy
import lib_const
import lib_crypto

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

# fucntion to define rpc_connection
def def_credentials(coin):
    rpcport = '';
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
            print("rpcport not in conf file, exiting")
            print("check " + coin_config_file)
            exit(1)
    try:
        return (Proxy("http://%s:%s@127.0.0.1:%d" % (rpcuser, rpcpassword, int(rpcport)), timeout=300))
    except:
        print("Unable to set RPC proxy, please confirm rpcuser, rpcpassword and rpcport are set in "+coin_config_file)

def get_ntx_txids(start, end):
    return RPC["KMD"].getaddresstxids({"addresses": [lib_const.NTX_ADDR], "start":start, "end":end})


# KMD RPC Proxy
RPC = {}
for coin in lib_crypto.COIN_PARAMS:
    try:
        RPC[coin] = def_credentials(coin)
    except:
        #print(f"{coin} RPC failed")
        pass