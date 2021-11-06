from django.contrib.auth.models import User, Group
from kmd_ntx_api.models import *
from rest_framework import serializers


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['url', 'username', 'email', 'groups']


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ['url', 'name']


class addressesSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = addresses
        fields = ['notary_id', 'notary', 'address', 'chain',
                  'pubkey', 'season', 'server']


class balancesSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = balances
        fields = ['notary', 'chain', 'balance', 'address',
                  'update_time', 'season', 'server']


class coinsSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = coins
        fields = ['chain', 'coins_info', 'electrums', 'electrums_ssl',
                  'explorers', 'dpow', 'dpow_tenure', 'dpow_active',
                  'mm2_compatible']


class coinSocialSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = coin_social
        fields = ['chain', 'discord', 'email', 'explorers', 'github',
                  'icon', 'linkedin',  'mining_pools', 'reddit',
                  'telegram', 'twitter', 'youtube',  'website', 'season']


class lastNotarisedSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = last_notarised
        fields = ['season', 'server', 'notary', 'chain', 'txid',
                  'block_height', 'block_time']


class minedSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = mined
        fields = ['block_height', 'block_time', 'block_datetime',
                  'value', 'address', 'name', 'txid', 'season']


class minedCountDailySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = mined_count_daily
        fields = ['mined_date', 'notary', 'blocks_mined', 'sum_value_mined',
                  'time_stamp', 'time_stamp']


class minedCountSeasonSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = mined_count_season
        fields = ['name', 'address', 'blocks_mined', 'sum_value_mined',
                  'max_value_mined', 'max_value_txid', 'last_mined_block',
                  'last_mined_blocktime', 'time_stamp',
                  'season']


class nnBtcTxSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = nn_btc_tx
        fields = ['txid', 'block_hash', 'block_height', 'block_time',
                  'block_datetime', 'address', 'notary', 'season',
                  'category', 'input_index', 'input_sats', 'output_index',
                  'output_sats', 'num_inputs', 'num_outputs', 'fees']


class nnLtcTxSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = nn_ltc_tx
        fields = ['txid', 'block_hash', 'block_height', 'block_time',
                  'block_datetime', 'address', 'notary', 'season',
                  'category', 'input_index', 'input_sats', 'output_index',
                  'output_sats', 'num_inputs', 'num_outputs', 'fees']


class nnSocialSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = nn_social
        fields = ['notary', 'twitter', 'youtube', 'discord', 'telegram',
                  'email', 'github', 'keybase', 'website', 'icon', 'season']


class notarisedSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = notarised
        fields = ['txid', 'chain', 'block_height', 'block_time',
                  'block_datetime', 'block_hash', 'ac_ntx_blockhash',
                  'ac_ntx_height', 'opret', 'notaries', 'notary_addresses',
                  'season', 'server', 'epoch', 'scored', 'score_value']


class notary_ntxSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = notarised
        fields = ['txid', 'chain', 'block_height', 'block_time',
                  'ac_ntx_height', 'score_value']


class notarisedChainDailySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = notarised_chain_daily
        fields = ['notarised_date', 'chain', 'ntx_count']


class notarisedChainSeasonSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = notarised_chain_season
        fields = ['chain', 'ntx_count', 'block_height', 'kmd_ntx_blockhash',
                  'kmd_ntx_txid', 'kmd_ntx_blocktime', 'opret',
                  'ac_ntx_blockhash', 'ac_ntx_height', 'ac_block_height',
                  'ntx_lag', 'season', 'server']


class notarisedCountDailySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = notarised_count_daily
        fields = ['notarised_date', 'notary', 'btc_count', 'antara_count',
                  'third_party_count', 'other_count', 'total_ntx_count',
                  'chain_ntx_counts', 'chain_ntx_pct', 'time_stamp',
                  'season', 'notarised_date']


class notarisedCountSeasonSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = notarised_count_season
        fields = ['season', 'notary', 'btc_count', 'antara_count',
                  'third_party_count', 'other_count', 'total_ntx_count',
                  'chain_ntx_counts', 'chain_ntx_pct', 'time_stamp']


class notarisedTenureSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = notarised_tenure
        fields = ['season', 'server', 'chain', 'first_ntx_block',
                  'last_ntx_block', 'first_ntx_block_time',
                  'last_ntx_block_time', 'official_start_block_time',
                  'official_end_block_time', 'scored_ntx_count',
                  'unscored_ntx_count']


class scoringEpochsSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = scoring_epochs
        fields = ['season', 'server', 'epoch', 'epoch_start',
                  'epoch_end', 'start_event', 'end_event',
                  'epoch_chains', 'score_per_ntx']


class vote2021Serializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = vote2021
        fields = ["txid", "block_hash", "block_time", "lock_time",
                  "block_height", "votes", "candidate",
                  "candidate_address", "mined_by", "difficulty",
                  "notes"]


class swapsSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = swaps
        fields = ["uuid", "started_at", "taker_coin", "taker_amount",
                  "taker_gui", "taker_version", "taker_pubkey",
                  "maker_coin", "maker_amount", "maker_gui",
                  "maker_version", "maker_pubkey", "time_stamp"]


class swapsFailedSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = swaps_failed
        fields = ["uuid", "started_at", "taker_coin", "taker_amount",
                  "taker_error_type", "taker_error_msg", "taker_gui",
                  "taker_version", "taker_pubkey", "maker_coin",
                  "maker_amount", "maker_error_type", "maker_error_msg",
                  "maker_gui", "maker_version", "maker_pubkey"]


class swapsSerializerPub(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = swaps
        fields = ["uuid", "started_at", "time_stamp", "taker_coin",
                  "taker_amount", "taker_gui", "taker_version",
                  "maker_coin", "maker_amount", "maker_gui",
                  "maker_version"]


class swapsFailedSerializerPub(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = swaps_failed
        fields = ["uuid", "started_at", "time_stamp", "taker_coin",
                  "taker_amount", "taker_error_type", "taker_error_msg",
                  "taker_gui", "taker_version", "maker_coin",
                  "maker_amount", "maker_error_type", "maker_error_msg",
                  "maker_gui", "maker_version"]


# Non-Model serializers
class addrFromBase58Serializer(serializers.Serializer):
    class Meta:
        fields = ["pubkey", "pubtype", "wiftype", "p2shtype"]
