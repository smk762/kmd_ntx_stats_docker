#!/usr/bin/env python3
from lib_const import *
from lib_notary import *
from lib_helper import *
import unittest

'''

season = get_season(int(time.time()))
assert season == "Season_4"

block_range_tables = ['mined','notarised', 'funding_transactions']
test_data = {}

for tbl in block_range_tables:
#collect test data: 500 blocks (1929000 - 1929099)
    sql = "SELECT * FROM "+tbl+" WHERE block_height >= 1929000 AND block_height < 1929100;"
    CURSOR.execute(sql)
    test_data.update({tbl: CURSOR.fetchall()})

try:
    assert len(test_data['mined']) == 100
except Exception as e:
    print("mined len assert failed")
'''
class Test_lil_endian(unittest.TestCase):

    def test_hex(self):
        hex_str = "efbeadde"
        actual = lil_endian(hex_str)
        expected = "deadbeef"
        self.assertEqual(actual, expected)

class Test_get_season(unittest.TestCase):

    def test_timestamp(self):
        py_timestamp = 1593237494
        actual = get_season(py_timestamp)
        expected = "Season_4"
        self.assertEqual(actual, expected)

        js_timestamp = py_timestamp*1000
        actual = get_season(js_timestamp)
        expected = "Season_4"
        self.assertEqual(actual, expected)

        small_timestamp = py_timestamp/10
        actual = get_season(small_timestamp)
        expected = "season_undefined"
        self.assertEqual(actual, expected)

        large_timestamp = py_timestamp*10
        actual = get_season(large_timestamp)
        expected = "season_undefined"
        self.assertEqual(actual, expected)

    def test_block(self):
        block = 1921999
        actual = get_season_from_block(block)
        expected = "Season_3"
        self.assertEqual(actual, expected)

        block = 1922000
        actual = get_season_from_block(block)
        expected = "Season_4"
        self.assertEqual(actual, expected)

        block = 1922000*10
        actual = get_season_from_block(block)
        expected = "season_undefined"
        self.assertEqual(actual, expected)

    def test_addresses(self):
        addresses = ['RKdXYhrQxB3LtwGpysGenKFHFTqSi5g7EF', 'RXiZTJJGbkVH69THmQiZHdz5VE22oXNiF5', 'RLrZLWrFnLkcMf8LQYs9dHFdJkgQrpUFhn',
        'RMadNAGn63C3EsBJzn3UT1XfsWdSnwCDqp', 'RMadEU8A8anN621y84fqfqNQJVyTXs6ZkE', 'RMadARbUdiakCKUR8hxiqCTeTRco8cY3Rv', 
        'RFJeVTuJrsvbcbanrcMRPKU3zjNkkenzuh', 'RQipE6ycbVVb9vCkhqrK8PGZs2p5YmiBtg', 'RMqbQz4NPNbG15QBwy9EFvLn4NX5Fa7w5g',
        'RPknkGAHMwUBvfKQfvw9FyatTZzicSiN4y', 'RFQNjTfcvSAmf8D83og1NrdHj1wH2fc5X4', 'RQrLjTk25WHHo5CcDZXQ4CpZcgmgZa2EZK', 
        'RGcGqDQV6DHHYCVteio5VG2zeH5KyCcYjF' ]

        notaries = ['gcharang_SH', 'greer_NA', 'indenodes_AR', 'indenodes_EU', 'indenodes_NA', 'indenodes_SH',
                     'karasugoi_NA', 'madmax_AR', 'madmax_EU', 'madmax_NA', 'marmarachain_AR', 'mcrypt_SH',
                     'metaphilibert_AR']
                     
        actual = get_season_from_addresses(notaries, addresses, "KMD")
        expected = "Season_4"
        self.assertEqual(actual, expected)

        lt_13_addresses = ['RKdXYhrQxB3LtwGpysGenKFHFTqSi5g7EF', 'RXiZTJJGbkVH69THmQiZHdz5VE22oXNiF5']
        lt_13_notaries = ['mcrypt_SH', 'metaphilibert_AR']         
        actual = get_season_from_addresses(lt_13_notaries, lt_13_addresses, "KMD")
        expected = "season_undefined"
        self.assertEqual(actual, expected)

        season_mix_addresses = ['RKytuA1ubrCD66hNNemcsvyDhDbcR2S1sU', 'RYY4ajQfC4GE6WA8wn5wR7BYdJDbCC7H2x', 'RLrZLWrFnLkcMf8LQYs9dHFdJkgQrpUFhn',
        'RUreYvNjhZYc1vP8cND9Cztpni1pYsigXb', 'RMadEU8A8anN621y84fqfqNQJVyTXs6ZkE', 'RMadARbUdiakCKUR8hxiqCTeTRco8cY3Rv', 
        'RFJeVTuJrsvbcbanrcMRPKU3zjNkkenzuh', 'RQipE6ycbVVb9vCkhqrK8PGZs2p5YmiBtg', 'RMqbQz4NPNbG15QBwy9EFvLn4NX5Fa7w5g',
        'RPknkGAHMwUBvfKQfvw9FyatTZzicSiN4y', 'RFQNjTfcvSAmf8D83og1NrdHj1wH2fc5X4', 'RQrLjTk25WHHo5CcDZXQ4CpZcgmgZa2EZK', 
        'RGcGqDQV6DHHYCVteio5VG2zeH5KyCcYjF' ]

        season_mix_notaries = ['gcharang_SH', 'greer_NA', 'indenodes_AR', 'indenodes_EU', 'indenodes_NA', 'indenodes_SH',
                     'karasugoi_NA', 'madmax_AR', 'madmax_EU', 'madmax_NA', 'farl4web_EU', 'chmex_EU',
                     'mrlynch_AR']
                     
        actual = get_season_from_addresses(season_mix_notaries, season_mix_addresses, "KMD")
        expected = "season_undefined"
        self.assertEqual(actual, expected)

    def test_address(self):
        address = "RGcGqDQV6DHHYCVteio5VG2zeH5KyCcYjF" # gcharang_SH
        actual = get_seasons_from_address(address)
        expected = ["Season_4"]
        self.assertEqual(actual, expected)

        address = "EMgbGBfbKmWSouUWXrGgTeChEQMVRhuxzz" # alien_AR
        actual = get_seasons_from_address(address, "EMC2")
        expected = ["Season_3_Third_Party", "Season_4_Third_Party"]
        self.assertEqual(sorted(actual), sorted(expected))

        address = "1FeexV6bAHb8ybZjqQMjJrcCrHGW9sb6uF" # not CSW
        actual = get_seasons_from_address(address, "BTC")
        expected = []
        self.assertEqual(actual, expected)

class Test_known_address(unittest.TestCase):

    def test_get_notary_from_addr(self):
        address = "1FeexV6bAHb8ybZjqQMjJrcCrHGW9sb6uF" # not CSW
        actual = get_notary_from_address(address)
        expected = 'unknown'
        self.assertEqual(actual, expected)

        address = "RGcGqDQV6DHHYCVteio5VG2zeH5KyCcYjF" # gcharang_SH
        actual = get_notary_from_address(address)
        expected = "gcharang_SH"
        self.assertEqual(actual, expected)

        address = "EMgbGBfbKmWSouUWXrGgTeChEQMVRhuxzz" # alien_AR
        actual = get_notary_from_address(address)
        expected = "alien_AR"
        self.assertEqual(actual, expected)

class Test_opret_decode(unittest.TestCase):

    def test_get_ticker(self):
        scriptPubKeyBinary = binascii.unhexlify("ab7a0202322a2124c0ceadf15ba2a2a6b1f2838587319ac92cfa3111617b0e029e9d0e00484f444c00e1956043b84a6fe3c8db130ab43d75d26d84b1e681de90e4f3a2b57676cf1b510c000000"[70:])
        actual = get_ticker(scriptPubKeyBinary)
        expected = "HODL"
        self.assertEqual(actual, expected)

    def test_get_notarised_data(self):
        result = ('HODL', 1939649, 1593250479, datetime.datetime(2020, 6, 27, 9, 34, 39),
                    '0ddce76cc7c3d63254e81f1f1d76912734537ea0cfe71a125e1766ba73075cfb',
                    ['chmex_AR', 'decker_AR', 'decker_EU', 'etszombi_AR', 'fullmoon_NA', 'madmax_NA',
                    'mihailo_EU', 'mrlynch_AR', 'node9_EU', 'peer2cloud_AR', 'phba2061_EU', 'pirate_NA',
                    'titomane_SH'],
                    '020e7b611131fa2cc99a31878583f2b1a6a2a25bf1adcec024212a3202027aab', 957854,
                    '2e8732b608a37b47307a67abce11922db968435552f2ea6ad0b5b4fda82123d5',
                    'OP_RETURN ab7a0202322a2124c0ceadf15ba2a2a6b1f2838587319ac92cfa3111617b0e029e9d0e00484f444c00e1956043b84a6fe3c8db130ab43d75d26d84b1e681de90e4f3a2b57676cf1b510c000000',
                    'Season_4', 'N/A')

        actual = get_notarised_data("2e8732b608a37b47307a67abce11922db968435552f2ea6ad0b5b4fda82123d5")
        expected = result
        self.assertEqual(actual, expected)

class Test_update_miner(unittest.TestCase):

    def test_update_miner(self):
        block = 1939602
        actual = update_miner(block)
        expected = (1939602, 1593247810, datetime.datetime(2020, 6, 27, 8, 50, 10),
                    Decimal('3.001609999999999889297441768576391041278839111328125'),
                    'RS4S9b9aG1yfeXFoBj2NcPoBE21XKfJDgc', 'decker_EU',
                    '3c9e5ad7062219945a78783c25309d5cbfdd610a1dedd88a41bf1bbd55e03e22',
                    'Season_4')
        self.assertEqual(actual, expected)


if __name__ == '__main__':
        unittest.main(exit=False)