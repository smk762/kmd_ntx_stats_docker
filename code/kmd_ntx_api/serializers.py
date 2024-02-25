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
        fields = ['notary_id', 'notary', 'address', 'coin',
                  'pubkey', 'season', 'server']


class balancesSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = balances
        fields = ['notary', 'coin', 'balance', 'address',
                  'update_time', 'season', 'server']


class coinNtxSeasonSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = coin_ntx_season
        fields = ['season', 'coin', 'coin_data', 'timestamp']


class coinsSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = coins
        fields = ['coin', 'coins_info', 'electrums', 'electrums_ssl', 'electrums_wss',
                  'explorers', 'lightwallets', 'dpow', 'dpow_tenure', 'dpow_active',
                  'mm2_compatible']


class coinSocialSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = coin_social
        fields = ['coin', 'discord', 'email', 'explorers', 'github',
                  'icon', 'linkedin',  'mining_pools', 'reddit',
                  'telegram', 'twitter', 'youtube',  'website', 'season']


class coinLastNtxSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = coin_last_ntx
        fields = ['season', 'server', 'coin', 'notaries',
                  'opret', 'kmd_ntx_blockheight', 'kmd_ntx_blockhash',
                  'kmd_ntx_txid', 'kmd_ntx_blocktime', 'ac_ntx_blockhash',
                  'ac_ntx_height']


class minedSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = mined
        fields = ['block_height', 'block_time', 'block_datetime',
                  'value', 'address', 'name', 'txid', 'diff', 'season',
                  'usd_price', 'btc_price', 'category']


class minedCountDailySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = mined_count_daily
        fields = ['mined_date', 'notary', 'blocks_mined', 'sum_value_mined',
                  'usd_price', 'btc_price', 'timestamp']


class minedCountSeasonSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = mined_count_season
        fields = ['name', 'address', 'blocks_mined', 'sum_value_mined',
                  'max_value_mined', 'max_value_txid', 'last_mined_block',
                  'last_mined_blocktime', 'timestamp',
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
        fields = ['txid', 'coin', 'block_height', 'block_time',
                  'block_datetime', 'block_hash', 'ac_ntx_blockhash',
                  'ac_ntx_height', 'opret', 'notaries', 'notary_addresses',
                  'season', 'server', 'epoch', 'scored', 'score_value']


class notarisedSerializerLite(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = notarised
        fields = ['txid', 'coin', 'block_height', 'block_time',
                  'block_datetime', 'ac_ntx_height', 'opret', 'notaries', 
                  'season', 'server', 'epoch', 'score_value']


class notaryLastNtxSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = notary_last_ntx
        fields = ['season', 'server', 'notary', 'coin', 'notaries',
                  'opret', 'kmd_ntx_blockheight', 'kmd_ntx_blockhash',
                  'kmd_ntx_txid', 'kmd_ntx_blocktime', 'ac_ntx_blockhash',
                  'ac_ntx_height']


class notary_ntxSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = notarised
        fields = ['txid', 'coin', 'block_height', 'block_time',
                  'ac_ntx_height', 'score_value']


class notarisedCoinDailySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = notarised_coin_daily
        fields = ['notarised_date', 'coin', 'ntx_count']


class notarisedCountDailySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = notarised_count_daily
        fields = ['season', 'notarised_date', 'notary', 'master_server_count',
                  'main_server_count', 'third_party_server_count', 'other_server_count',
                  'total_ntx_count', 'coin_ntx_counts', 'coin_ntx_pct', 'timestamp',
                  'season']


class notaryNtxSeasonSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = notary_ntx_season
        fields = ['season', 'notary', 'notary_data', 'timestamp']


class notarisedTenureSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = notarised_tenure
        fields = ['season', 'server', 'coin', 'first_ntx_block',
                  'last_ntx_block', 'first_ntx_block_time',
                  'last_ntx_block_time', 'official_start_block_time',
                  'official_end_block_time', 'scored_ntx_count',
                  'unscored_ntx_count']


class scoringEpochsSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = scoring_epochs
        fields = ['season', 'server', 'epoch', 'epoch_start',
                  'epoch_end', 'start_event', 'end_event',
                  'epoch_coins', 'score_per_ntx']



class notaryVoteSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = notary_vote
        fields = ["txid", "block_hash", "block_time", "lock_time",
                  "block_height", "votes", "candidate",
                  "candidate_address", "mined_by", "difficulty",
                  "notes", 'year', 'valid']



class notaryCandidatesSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = notary_candidates
        fields = ["year", "season", "name", "proposal_url"]


class rewardsTxSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = rewards_tx
        fields = ["txid", "block_height", "block_time", "block_datetime",
                  "address", "rewards_value",
                  'usd_price', 'btc_price', "block_hash"]


class seednodeVersionStatsSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = seednode_version_stats
        fields = ['name', 'season', 'version',
                  'timestamp', 'error', 'score']
        headers = ['Notary', 'Season', 'Version',
                  'Timestamp', 'Error', 'Score']


class serverNtxSeasonSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = server_ntx_season
        fields = ['season', 'server', 'server_data', 'timestamp']


class kmdSupplySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = kmd_supply
        fields = ['block_time', 'block_height', 'total_supply']


class swapsSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = swaps
        fields = ["uuid", "started_at", "taker_coin", "taker_amount",
                  "taker_gui", "taker_version", "taker_pubkey",
                  "maker_coin", "maker_amount", "maker_gui",
                  "maker_version", "maker_pubkey", "timestamp"]


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
        fields = ["uuid", "started_at", "timestamp", "taker_coin",
                  "taker_amount", "taker_gui", "taker_version",
                  "maker_coin", "maker_amount", "maker_gui",
                  "maker_version"]


class swapsFailedSerializerPub(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = swaps_failed
        fields = ["uuid", "started_at", "timestamp", "taker_coin",
                  "taker_amount", "taker_error_type", "taker_error_msg",
                  "taker_gui", "taker_version", "maker_coin",
                  "maker_amount", "maker_error_type", "maker_error_msg",
                  "maker_gui", "maker_version"]


# Non-Model serializers
class addrFromBase58Serializer(serializers.Serializer):
    class Meta:
        fields = ["pubkey", "pubtype", "wiftype", "p2shtype"]
        