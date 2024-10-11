#!/usr/bin/env python3.12
import json
import time
import ssl
import socket
import asyncio
import websockets
from lib_helper import get_electrum_url_port
from lib_const import ELECTRUMS, ELECTRUMS_SSL, ELECTRUMS_WSS, logger
from lib_crypto import *
from logger import logger

socket.setdefaulttimeout(5)


class ElectrumServer:
    __slots__ = ("url", "port", "protocol", "result", "blockheight", "last_connection")

    def __init__(self, url, port, protocol):
        self.url = url
        self.port = port
        self.protocol = protocol
        self.result = None
        self.blockheight = -1
        self.last_connection = -1

    def normalize_params(self, params):
        return [params] if params and not isinstance(params, list) else params

    def build_payload(self, method, params=None):
        payload = {"id": 0, "method": method}
        if params:
            payload.update({"params": params})
        return payload

    def common_handshake(self, sock):
        payload = self.build_payload("server.version", ["kmd_notary_stats_repo", ["1.4", "1.6"]])
        sock.send(json.dumps(payload).encode() + b'\n')
        time.sleep(1)
        return sock.recv(999999)[:-1].decode()

    def send_request(self, sock, method, params):
        payload = self.build_payload(method, params)
        sock.send(json.dumps(payload).encode() + b'\n')
        time.sleep(1)
        resp = sock.recv(999999)[:-1].decode().splitlines()
        return resp[-1] if resp else None

    def tcp(self, method, params=None):
        params = self.normalize_params(params)
        try:
            with socket.create_connection((self.url, self.port), timeout=10) as sock:
                # Handshake
                self.common_handshake(sock)
                # Request
                return self.send_request(sock, method, params)
        except Exception as e:
            logger.error(f"TCP error for {self.url}:{self.port} - {e}")
            return str(e)

    def ssl(self, method, params=None):
        params = self.normalize_params(params)
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        try:
            with socket.create_connection((self.url, self.port), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname=self.url) as ssock:
                    # Handshake
                    self.common_handshake(ssock)
                    # Request
                    return self.send_request(ssock, method, params)
        except Exception as e:
            logger.error(f"SSL error for {self.url}:{self.port} - {e}")
            return str(e)

    async def async_wss_request(self, websocket, method, params):
        payload = self.build_payload("server.version", ["kmd_coins_repo", ["1.4", "1.6"]])
        await websocket.send(json.dumps(payload))
        await asyncio.sleep(1)
        await websocket.recv()
        payload = self.build_payload(method, params)
        await websocket.send(json.dumps(payload))
        await asyncio.sleep(1)
        resp = await websocket.recv()
        resp = resp.splitlines()
        return resp[-1] if resp else None

    def wss(self, method, params=None):
        params = self.normalize_params(params)
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        try:
            async def connect_and_query():
                async with websockets.connect(f"wss://{self.url}:{self.port}", ssl=ssl_context, timeout=10) as websocket:
                    return await self.async_wss_request(websocket, method, params)

            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            return loop.run_until_complete(connect_and_query())
        except Exception as e:
            logger.error(f"WSS error for {self.url}:{self.port} - {e}")
            return str(e)


def get_from_electrum(url, port, method, params=None):
    e = ElectrumServer(url, port, "TCP")
    return json.loads(e.tcp(method, params))


def get_from_electrum_ssl(url, port, method, params=None):
    e = ElectrumServer(url, port, "SSL")
    return json.loads(e.ssl(method, params))


def get_from_electrum_wss(url, port, method, params=None):
    e = ElectrumServer(url, port, "WSS")
    return json.loads(e.wss(method, params))


def combine_balance_responses(p2pk_resp, p2pkh_resp):
    p2pk_confirmed_balance = p2pk_resp['result']['confirmed']
    p2pkh_confirmed_balance = p2pkh_resp['result']['confirmed']
    p2pk_unconfirmed_balance = p2pk_resp['result']['unconfirmed']
    p2pkh_unconfirmed_balance = p2pkh_resp['result']['unconfirmed']
    total_confirmed = p2pk_confirmed_balance + p2pkh_confirmed_balance
    total_unconfirmed = p2pk_unconfirmed_balance + p2pkh_unconfirmed_balance
    total = total_confirmed + total_unconfirmed
    return total/100000000


def get_full_electrum_balance(pubkey, coin):
    p2pk_scripthash = get_p2pk_scripthash_from_pubkey(pubkey)
    p2pkh_scripthash = get_p2pkh_scripthash_from_pubkey(pubkey)
    if coin in ELECTRUMS_WSS:
        for electrum in ELECTRUMS_WSS[coin]:
            try:
                url, port = get_electrum_url_port(electrum)
                e = ElectrumServer(url, port, "WSS")
                p2pk_resp = json.loads(e.wss('blockchain.scripthash.get_balance', p2pk_scripthash))
                p2pkh_resp = json.loads(e.wss('blockchain.scripthash.get_balance', p2pkh_scripthash))
                return combine_balance_responses(p2pk_resp, p2pkh_resp)
            except Exception as e:
                logger.warning(f"Error in [get_full_electrum_balance] with ELECTRUMS_WSS for {coin}: {e}")
    
    if coin in ELECTRUMS_SSL:
        for electrum in ELECTRUMS_SSL[coin]:
            try:
                url, port = get_electrum_url_port(electrum)
                e = ElectrumServer(url, port, "SSL")
                p2pk_resp = json.loads(e.ssl('blockchain.scripthash.get_balance', p2pk_scripthash))
                # logger.warning(p2pk_resp)
                p2pkh_resp = json.loads(e.ssl('blockchain.scripthash.get_balance', p2pkh_scripthash))
                # logger.warning(p2pkh_resp)
                return combine_balance_responses(p2pk_resp, p2pkh_resp)
            except Exception as e:
                logger.warning(f"Error in [get_full_electrum_balance] with ELECTRUMS_SSL for {coin}: {e}")

    if coin in ELECTRUMS:
        for electrum in ELECTRUMS[coin]:
            try:
                url, port = get_electrum_url_port(electrum)
                e = ElectrumServer(url, port, "TCP")
                p2pk_resp = json.loads(e.tcp('blockchain.scripthash.get_balance', p2pk_scripthash))
                p2pkh_resp = json.loads(e.tcp('blockchain.scripthash.get_balance', p2pkh_scripthash))
                return combine_balance_responses(p2pk_resp, p2pkh_resp)
            except Exception as e:
                logger.warning(f"Error in [get_full_electrum_balance] with ELECTRUMS for {coin}: {e}")
    return -1


def get_notary_utxo_count(coin, pubkey):
    if coin in ELECTRUMS_SSL:
        for electrum in ELECTRUMS_SSL[coin]:
            url, port = get_electrum_url_port(electrum)
            p2pk_scripthash = get_p2pk_scripthash_from_pubkey(pubkey)
            p2pk_resp = get_from_electrum_ssl(url, port, 'blockchain.scripthash.listunspent', p2pk_scripthash)
            if not isinstance(p2pk_resp['result'], int):
                num_unspent = 0
                for item in p2pk_resp['result']:
                    if item['value'] == 10000:
                        num_unspent +=1
                return num_unspent
            else:
                logger.warning(f"ELECTRUM returning 'int' response for {coin}")


    elif coin in ELECTRUMS:
        for electrum in ELECTRUMS[coin]:
            url, port = get_electrum_url_port(electrum)
            p2pk_scripthash = get_p2pk_scripthash_from_pubkey(pubkey)
            p2pk_resp = get_from_electrum(url, port, 'blockchain.scripthash.listunspent', p2pk_scripthash)
            if not isinstance(p2pk_resp['result'], int):
                num_unspent = 0
                for item in p2pk_resp['result']:
                    if item['value'] == 10000:
                        num_unspent +=1
                return num_unspent
            else:
                logger.warning(f"ELECTRUM returning 'int' response for {coin}")
    else:
        logger.info(f"{coin} not in electrums or electrums_ssl")


def get_version(coin):
    if coin in ELECTRUMS_SSL:
        for electrum in ELECTRUMS_SSL[coin]:
            split = electrum.split(":")
            url = split[0]
            port = split[1]
            return get_from_electrum_ssl(url, port, "server.version")

    if coin in ELECTRUMS:
        for electrum in ELECTRUMS[coin]:
            split = electrum.split(":")
            url = split[0]
            port = split[1]
            return get_from_electrum(url, port, "server.version")