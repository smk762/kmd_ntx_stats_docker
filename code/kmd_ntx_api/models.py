from django.db import models
from django.db.models import JSONField
from django.contrib.postgres.fields import ArrayField

# TODO: When updating on conflict, make sure all potentially variable fields are included.


class addresses(models.Model):
    season = models.CharField(max_length=34)
    server = models.CharField(max_length=34)
    notary = models.CharField(max_length=34)
    notary_id = models.CharField(max_length=34)
    address = models.CharField(max_length=34)
    pubkey = models.CharField(max_length=66)
    coin = models.CharField(max_length=34)

    class Meta:
        db_table = 'addresses'
        indexes = [
            models.Index(fields=['notary']),
            models.Index(fields=['coin']),
            models.Index(fields=['season', 'server'])
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['address', "season", "coin"],
                name='unique_season_coin_address'
            )
        ]


class balances(models.Model):
    season = models.CharField(max_length=34)
    server = models.CharField(max_length=34)
    notary = models.CharField(max_length=34)
    address = models.CharField(max_length=34)
    coin = models.CharField(max_length=34)
    balance = models.DecimalField(max_digits=18, decimal_places=8)
    update_time = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'balances'
        indexes = [
            models.Index(fields=['notary']),
            models.Index(fields=['coin']),
            models.Index(fields=['season', 'server'])
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['coin', 'address', 'season'],
                name='unique_coin_address_season_balance'
            )
        ]


class coins(models.Model):
    coin = models.CharField(max_length=34)
    coins_info = JSONField(default=dict)
    electrums = JSONField(default=dict)
    electrums_ssl = JSONField(default=dict)
    electrums_wss = JSONField(default=dict)
    lightwallets = JSONField(default=dict)
    explorers = JSONField(default=dict)
    dpow = JSONField(default=dict)
    dpow_tenure = JSONField(default=dict)
    dpow_active = models.PositiveIntegerField(default=0)
    mm2_compatible = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'coins'
        indexes = [
            models.Index(fields=['coin']),
            models.Index(fields=['dpow_active']),
            models.Index(fields=['mm2_compatible'])
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['coin'],
                name='unique_coin_coin'
            )
        ]


class coin_social(models.Model):
    coin = models.CharField(max_length=128, default="")
    twitter = models.CharField(max_length=128, default="")
    reddit = models.CharField(max_length=128, default="")
    email = models.CharField(max_length=128, default="")
    linkedin = models.CharField(max_length=128, default="")
    mining_pools = ArrayField(models.CharField(max_length=64), default=list)
    youtube = models.CharField(max_length=128, default="")
    discord = models.CharField(max_length=128, default="")
    telegram = models.CharField(max_length=128, default="")
    github = models.CharField(max_length=128, default="")
    website = models.CharField(max_length=128, default="")
    explorers = ArrayField(models.CharField(max_length=64), default=list)
    icon = models.CharField(max_length=128, default="")
    season = models.CharField(max_length=128, default="")

    class Meta:
        db_table = 'coin_social'
        constraints = [
            models.UniqueConstraint(
                fields=['coin', 'season'],
                name='unique_coin_season_social'
            )
        ]


class coin_last_ntx(models.Model):
    season = models.CharField(max_length=34)
    server = models.CharField(max_length=34, default='')
    coin = models.CharField(max_length=64)
    notaries = ArrayField(models.CharField(max_length=34),size=13)
    opret = models.CharField(max_length=2048)
    kmd_ntx_blockheight = models.PositiveIntegerField(default=0)
    kmd_ntx_blockhash = models.CharField(max_length=64)
    kmd_ntx_txid = models.CharField(max_length=64)
    kmd_ntx_blocktime = models.PositiveIntegerField(default=0)
    ac_ntx_blockhash = models.CharField(max_length=64)
    ac_ntx_height = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'coin_last_ntx'
        indexes = [
            models.Index(fields=['coin']),
            models.Index(fields=['season'])
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['coin', 'season'],
                name='unique_coin_last_ntx_season'
            )
        ]


class coin_ntx_season(models.Model):
    season = models.CharField(max_length=34)
    coin = models.CharField(max_length=64)
    coin_data = JSONField(default=dict)
    timestamp = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'coin_ntx_season'
        indexes = [
            models.Index(fields=['coin']),
            models.Index(fields=['season'])
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['coin', "season"],
                name='unique_coin_season'
            )
        ]


class mined(models.Model):
    block_height = models.PositiveIntegerField(default=0)
    block_time = models.PositiveIntegerField(default=0)
    block_datetime = models.DateTimeField()
    value = models.DecimalField(max_digits=18, decimal_places=8)
    address = models.CharField(max_length=34)
    name = models.CharField(max_length=34)
    txid = models.CharField(max_length=64)
    diff = models.FloatField(default=0)
    season = models.CharField(max_length=34)
    usd_price = models.DecimalField(max_digits=18, decimal_places=8, default=0)
    btc_price = models.DecimalField(max_digits=18, decimal_places=8, default=0)
    category = models.CharField(max_length=34 ,default="")

    class Meta:
        db_table = 'mined'
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['category']),
            models.Index(fields=['season']),
            models.Index(fields=['-block_height']),
            models.Index(fields=['-block_time'])
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['block_height'], 
                name='unique_block'
            )
        ]


class mined_archive(models.Model):
    block_height = models.PositiveIntegerField(default=0)
    block_time = models.PositiveIntegerField(default=0)
    block_datetime = models.DateTimeField()
    value = models.DecimalField(max_digits=18, decimal_places=8)
    address = models.CharField(max_length=34)
    name = models.CharField(max_length=34)
    txid = models.CharField(max_length=64)
    diff = models.FloatField(default=0)
    season = models.CharField(max_length=34)
    usd_price = models.DecimalField(max_digits=18, decimal_places=8, default=0)
    btc_price = models.DecimalField(max_digits=18, decimal_places=8, default=0)
    category = models.CharField(max_length=34 ,default="")

    class Meta:
        db_table = 'mined_archive'
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['category']),
            models.Index(fields=['season']),
            models.Index(fields=['-block_height']),
            models.Index(fields=['-block_time'])
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['block_height'], 
                name='unique_block_archive'
            )
        ]


class mined_count_daily(models.Model):
    mined_date = models.DateField()
    notary = models.CharField(max_length=64)
    blocks_mined = models.PositiveIntegerField(default=0)
    sum_value_mined = models.DecimalField(max_digits=18, decimal_places=8)
    timestamp = models.PositiveIntegerField(default=0)
    usd_price = models.DecimalField(max_digits=18, decimal_places=8, default=0)
    btc_price = models.DecimalField(max_digits=18, decimal_places=8, default=0)

    class Meta:
        db_table = 'mined_count_daily'
        indexes = [
            models.Index(fields=['-mined_date']),
            models.Index(fields=['notary'])
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['notary', 'mined_date'],
                name='unique_notary_daily_mined'
            )
        ]


class mined_count_season(models.Model):
    name = models.CharField(max_length=64)
    address = models.CharField(max_length=64, default='')
    blocks_mined = models.PositiveIntegerField(default=0)
    sum_value_mined = models.DecimalField(max_digits=18, decimal_places=8)
    max_value_mined = models.DecimalField(max_digits=18, decimal_places=8)
    max_value_txid = models.CharField(max_length=64, default='')
    last_mined_block = models.PositiveIntegerField(default=0)
    last_mined_blocktime = models.PositiveIntegerField(default=0)
    timestamp = models.PositiveIntegerField(default=0)
    season = models.CharField(max_length=34)

    class Meta:
        db_table = 'mined_count_season'
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['season'])
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['address', 'season'],
                name='unique_name_season_mined'
            )
        ]

# TODO: Archive data and deprecate
class nn_btc_tx(models.Model):
    txid = models.CharField(max_length=64)
    block_hash = models.CharField(max_length=64)
    block_height = models.PositiveIntegerField(default=0)
    block_time = models.PositiveIntegerField(default=0)
    block_datetime = models.DateTimeField()

    address = models.CharField(max_length=42)
    notary = models.CharField(max_length=42, default="non-NN")
    season = models.CharField(max_length=32)
    category = models.CharField(max_length=32)

    input_index = models.IntegerField(default=-1)
    input_sats = models.BigIntegerField(default=-1)
    output_index = models.IntegerField(default=-1)
    output_sats = models.BigIntegerField(default=-1)
    num_inputs = models.PositiveIntegerField(default=0)
    num_outputs = models.PositiveIntegerField(default=0)
    fees = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'nn_btc_tx'
        indexes = [
            models.Index(fields=['txid', '-block_time'])
        ]
        constraints = [
            models.UniqueConstraint(fields=['txid', 'address', 'input_index', 'output_index'],
                                 name='unique_btc_nn_txid')
        ]


class nn_ltc_tx(models.Model):
    txid = models.CharField(max_length=64)
    block_hash = models.CharField(max_length=64)
    block_height = models.PositiveIntegerField(default=0)
    block_time = models.PositiveIntegerField(default=0)
    block_datetime = models.DateTimeField()

    address = models.CharField(max_length=64)
    notary = models.CharField(max_length=42, default="non-NN")
    season = models.CharField(max_length=32)
    category = models.CharField(max_length=32)

    input_index = models.IntegerField(default=-1)
    input_sats = models.BigIntegerField(default=-1)
    output_index = models.IntegerField(default=-1)
    output_sats = models.BigIntegerField(default=-1)
    num_inputs = models.PositiveIntegerField(default=0)
    num_outputs = models.PositiveIntegerField(default=0)
    fees = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'nn_ltc_tx'
        indexes = [
            models.Index(fields=['txid']),
            models.Index(fields=['-block_time'])
        ]
        constraints = [
            models.UniqueConstraint(fields=['txid', 'address', 'input_index', 'output_index'],
                                 name='unique_ltc_nn_txid')
        ]


class nn_social(models.Model):
    notary = models.CharField(max_length=128)
    twitter = models.CharField(max_length=128)
    youtube = models.CharField(max_length=128)
    discord = models.CharField(max_length=128)
    email = models.CharField(max_length=128)
    telegram = models.CharField(max_length=128)
    github = models.CharField(max_length=128)
    keybase = models.CharField(max_length=128)
    website = models.CharField(max_length=128)
    icon = models.CharField(max_length=128)
    season = models.CharField(max_length=128)

    class Meta:
        db_table = 'nn_social'
        constraints = [
            models.UniqueConstraint(
                fields=['notary', 'season'],
                name='unique_notary_season_social'
            )
        ]


class notarised(models.Model):
    txid = models.CharField(max_length=64)
    coin = models.CharField(max_length=32)
    block_hash = models.CharField(max_length=64)
    block_time = models.PositiveIntegerField(default=0)
    block_datetime = models.DateTimeField()
    block_height = models.PositiveIntegerField(default=0)
    notaries = ArrayField(models.CharField(max_length=34),size=13)
    notary_addresses = ArrayField(models.CharField(max_length=34),size=13, default=list)
    ac_ntx_blockhash = models.CharField(max_length=64)
    ac_ntx_height = models.PositiveIntegerField(default=0)
    opret = models.CharField(max_length=2048)
    season = models.CharField(max_length=32)
    server = models.CharField(max_length=32, default='')
    epoch = models.CharField(max_length=32, default='')
    scored = models.BooleanField(default=True)
    score_value = models.DecimalField(max_digits=18, decimal_places=8, default=0)

    class Meta:
        db_table = 'notarised'
        indexes = [
            models.Index(fields=['txid']),
            models.Index(fields=['-block_time']),
            models.Index(fields=['-block_height']),
            models.Index(fields=['season']),
            models.Index(fields=['server']),
            models.Index(fields=['epoch']),
            models.Index(fields=['coin']),
            models.Index(fields=['coin', '-block_height']),
            models.Index(fields=['season', 'server']),
            models.Index(fields=['season', 'server', 'coin']),
            models.Index(fields=['season', 'server', 'epoch']),
            models.Index(fields=['season', 'server', 'epoch', 'coin']),
        ]
        constraints = [
            models.UniqueConstraint(fields=['txid'],
                                 name='unique_txid')
        ]


class notarised_archive(models.Model):
    txid = models.CharField(max_length=64)
    coin = models.CharField(max_length=32)
    block_hash = models.CharField(max_length=64)
    block_time = models.PositiveIntegerField(default=0)
    block_datetime = models.DateTimeField()
    block_height = models.PositiveIntegerField(default=0)
    notaries = ArrayField(models.CharField(max_length=34),size=13)
    notary_addresses = ArrayField(models.CharField(max_length=34),size=13, default=list)
    ac_ntx_blockhash = models.CharField(max_length=64)
    ac_ntx_height = models.PositiveIntegerField(default=0)
    opret = models.CharField(max_length=2048)
    season = models.CharField(max_length=32)
    server = models.CharField(max_length=32, default='')
    epoch = models.CharField(max_length=32, default='')
    scored = models.BooleanField(default=True)
    score_value = models.DecimalField(max_digits=18, decimal_places=8, default=0)

    class Meta:
        db_table = 'notarised_archive'
        indexes = [
            models.Index(fields=['txid']),
            models.Index(fields=['-block_time']),
            models.Index(fields=['-block_height']),
            models.Index(fields=['season']),
            models.Index(fields=['server']),
            models.Index(fields=['epoch']),
            models.Index(fields=['coin']),
            models.Index(fields=['coin', '-block_height']),
            models.Index(fields=['season', 'server']),
            models.Index(fields=['season', 'server', 'coin']),
            models.Index(fields=['season', 'server', 'epoch']),
            models.Index(fields=['season', 'server', 'epoch', 'coin']),
        ]
        constraints = [
            models.UniqueConstraint(fields=['txid'],
                                 name='unique_txid_archive')
        ]



class notarised_coin_daily(models.Model):
    notarised_date = models.DateField()
    season = models.CharField(max_length=24)
    server = models.CharField(max_length=24)
    coin = models.CharField(max_length=64)
    ntx_count = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'notarised_coin_daily'
        indexes = [
            models.Index(fields=['-notarised_date']),
            models.Index(fields=['season']),
            models.Index(fields=['server']),
            models.Index(fields=['coin'])
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['coin', 'notarised_date', 'season', 'server'],
                name='unique_notarised_coin_daily'
            )
        ]

# Todo: create subtables for json data
class notarised_count_daily(models.Model):
    season = models.CharField(max_length=34)
    notarised_date = models.DateField()
    notary = models.CharField(max_length=64)
    master_server_count = models.PositiveIntegerField(default=0)
    main_server_count = models.PositiveIntegerField(default=0)
    third_party_server_count = models.PositiveIntegerField(default=0)
    other_server_count = models.PositiveIntegerField(default=0)
    total_ntx_count = models.PositiveIntegerField(default=0)
    coin_ntx_counts = JSONField(default=dict)
    coin_ntx_pct = JSONField(default=dict)
    timestamp = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'notarised_count_daily'
        indexes = [
            models.Index(fields=['-notarised_date']),
            models.Index(fields=['notary'])
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['notary', "notarised_date"],
                name='unique_notary_date'
            )
        ]


class notary_last_ntx(models.Model):
    season = models.CharField(max_length=32)
    server = models.CharField(max_length=32, default='')
    coin = models.CharField(max_length=32)
    notary = models.CharField(max_length=64)
    notaries = ArrayField(models.CharField(max_length=34),size=13)
    opret = models.CharField(max_length=2048)
    kmd_ntx_blockheight = models.PositiveIntegerField(default=0)
    kmd_ntx_blockhash = models.CharField(max_length=64)
    kmd_ntx_txid = models.CharField(max_length=64)
    kmd_ntx_blocktime = models.PositiveIntegerField(default=0)
    ac_ntx_blockhash = models.CharField(max_length=64)
    ac_ntx_height = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'notary_last_ntx'
        indexes = [
            models.Index(fields=['notary']),
            models.Index(fields=['coin']),
            models.Index(fields=['season'])
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['notary','season', 'coin'],
                name='unique_notary_last_ntx_notary_season_coin'
            )
        ]


class notary_ntx_season(models.Model):
    season = models.CharField(max_length=34)
    notary = models.CharField(max_length=64)
    notary_data = JSONField(default=dict)
    timestamp = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'notary_ntx_season'
        indexes = [
            models.Index(fields=['notary']),
            models.Index(fields=['season'])
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['notary', "season"],
                name='unique_notary_season'
            )
        ]


class notarised_tenure(models.Model):
    server = models.CharField(max_length=32, default="Unofficial")
    season = models.CharField(max_length=32, default="Unofficial")
    coin = models.CharField(max_length=64)
    official_start_block_time = models.PositiveIntegerField(default=0)
    official_end_block_time = models.PositiveIntegerField(default=0)
    first_ntx_block = models.PositiveIntegerField(default=0)
    last_ntx_block = models.PositiveIntegerField(default=0)
    first_ntx_block_time = models.PositiveIntegerField(default=0)
    last_ntx_block_time = models.PositiveIntegerField(default=0)
    unscored_ntx_count = models.PositiveIntegerField(default=0)
    scored_ntx_count = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'notarised_tenure'
        indexes = [
            models.Index(fields=['coin', 'season', 'server'])
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['coin','season', 'server'],
                name='unique_coin_season_server_tenure'
            )
        ]


class notary_vote(models.Model):
    txid = models.CharField(max_length=64)
    block_hash = models.CharField(max_length=64)
    block_height = models.PositiveIntegerField()
    block_time = models.PositiveIntegerField()
    mined_by = models.CharField(max_length=42, default="")
    lock_time = models.PositiveIntegerField()
    votes = models.DecimalField(max_digits=18, decimal_places=8)
    difficulty = models.DecimalField(max_digits=18, decimal_places=8, default=0)
    candidate = models.CharField(max_length=64)
    candidate_address = models.CharField(max_length=42)
    notes = models.CharField(max_length=512)
    year = models.CharField(max_length=16, default='VOTE202x')
    valid = models.BooleanField(default=True)

    class Meta:
        db_table = 'notary_vote'
        constraints = [
            models.UniqueConstraint(fields=['txid', 'candidate'],
                                 name='unique_vote_txid_candidate')
        ]


class notary_candidates(models.Model):
    name = models.CharField(max_length=64, default="")
    year = models.CharField(max_length=12, default="")
    season = models.CharField(max_length=12, default="")
    proposal_url = models.CharField(max_length=256, default="")

    class Meta:
        db_table = 'notary_candidates'
        constraints = [
            models.UniqueConstraint(fields=['name', 'year'],
                                 name='unique_name_year_candidate')
        ]


# todo: add address lookup tool
class rewards_tx(models.Model):
    txid = models.CharField(max_length=64)
    block_hash = models.CharField(max_length=64)
    block_height = models.PositiveIntegerField(default=0)
    block_time = models.PositiveIntegerField(default=0)
    block_datetime = models.DateTimeField()
    sum_of_inputs = models.PositiveIntegerField(default=0)
    address = models.CharField(max_length=128, default='')
    sum_of_outputs = models.PositiveIntegerField(default=0)
    rewards_value =  models.FloatField(default=0)
    usd_price = models.DecimalField(max_digits=18, decimal_places=8, default=0)
    btc_price = models.DecimalField(max_digits=18, decimal_places=8, default=0)

    class Meta:
        db_table = 'rewards_tx'
        indexes = [
            models.Index(fields=['address']),
            models.Index(fields=['txid']),
            models.Index(fields=['block_hash']),
            models.Index(fields=['block_time']),
        ]
        constraints = [
            models.UniqueConstraint(fields=['txid', 'address'],
                                 name='unique_rewards_nn_txid')
        ]

class kmd_supply(models.Model):
    block_height = models.PositiveIntegerField(default=0)
    block_time = models.PositiveIntegerField(default=0)
    total_supply = models.PositiveIntegerField(default=0)
    delta = models.IntegerField(default=0)

    class Meta:
        db_table = 'kmd_supply'
        indexes = [
            models.Index(fields=['block_height']),
        ]
        constraints = [
            models.UniqueConstraint(fields=['block_height'],
                                 name='unique_blockheight_supply')
        ]


class scoring_epochs(models.Model):
    season = models.CharField(max_length=128)
    server = models.CharField(max_length=128)
    epoch = models.CharField(max_length=128)
    epoch_start = models.PositiveIntegerField(default=0)
    epoch_end = models.PositiveIntegerField(default=0)
    start_event = models.CharField(max_length=128)
    end_event = models.CharField(max_length=128)
    epoch_coins = ArrayField(models.CharField(max_length=34), default=list)
    score_per_ntx = models.DecimalField(max_digits=18, decimal_places=8)

    class Meta:
        db_table = 'scoring_epochs'
        indexes = [
            models.Index(fields=['season', 'server', 'epoch'])
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['season', 'server', 'epoch'],
                name='unique_scoring_epoch'
            )
        ]


class seednode_version_stats(models.Model):
    name = models.CharField(max_length=128)
    season = models.CharField(max_length=128, default='')
    version = models.CharField(max_length=128)
    timestamp = models.PositiveIntegerField(default=0)
    error = models.CharField(max_length=256)
    score = models.FloatField(default=0)

    class Meta:
        db_table = 'seednode_version_stats'
        indexes = [
            models.Index(fields=['timestamp'])
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'timestamp'],
                name='unique_mm2_version_stat'
            )
        ]


class server_ntx_season(models.Model):
    season = models.CharField(max_length=34)
    server = models.CharField(max_length=64)
    server_data = JSONField(default=dict)
    timestamp = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'server_ntx_season'
        indexes = [
            models.Index(fields=['server']),
            models.Index(fields=['season'])
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['server', "season"],
                name='unique_server_season'
            )
        ]


class swaps(models.Model):
    uuid = models.CharField(primary_key=True, max_length=36)
    started_at = models.DateTimeField()
    timestamp = models.PositiveIntegerField(default=0)
    taker_coin = models.CharField(max_length=12)
    taker_amount = models.FloatField()
    taker_gui = models.CharField(max_length=64, blank=True, null=True)
    taker_version = models.CharField(max_length=64, blank=True, null=True)
    taker_pubkey = models.CharField(max_length=66, blank=True, null=True)
    maker_coin = models.CharField(max_length=12)
    maker_amount = models.FloatField()
    maker_gui = models.CharField(max_length=64, blank=True, null=True)
    maker_version = models.CharField(max_length=64, blank=True, null=True)
    maker_pubkey = models.CharField(max_length=66, blank=True, null=True)

    class Meta:
        db_table = 'swaps'
        indexes = [
            models.Index(fields=['taker_coin']),
            models.Index(fields=['maker_coin']),
            models.Index(fields=['taker_gui']),
            models.Index(fields=['maker_gui']),
            models.Index(fields=['taker_pubkey']),
            models.Index(fields=['maker_pubkey']),
            models.Index(fields=['taker_version']),
            models.Index(fields=['maker_version'])
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['uuid'],
                name='unique_swap'
            )
        ]


class swaps_failed(models.Model):
    uuid = models.CharField(primary_key=True, max_length=36)
    started_at = models.DateTimeField()
    timestamp = models.PositiveIntegerField(default=0)
    taker_coin = models.CharField(max_length=12)
    taker_amount = models.FloatField()
    taker_error_type = models.CharField(max_length=32, blank=True, null=True)
    taker_error_msg = models.TextField(blank=True, null=True)
    taker_gui = models.CharField(max_length=64, blank=True, null=True)
    taker_version = models.CharField(max_length=64, blank=True, null=True)
    taker_pubkey = models.CharField(max_length=66, blank=True, null=True)
    maker_coin = models.CharField(max_length=12)
    maker_amount = models.FloatField()
    maker_error_type = models.CharField(max_length=32, blank=True, null=True)
    maker_error_msg = models.TextField(blank=True, null=True)
    maker_gui = models.CharField(max_length=64, blank=True, null=True)
    maker_version = models.CharField(max_length=64, blank=True, null=True)
    maker_pubkey = models.CharField(max_length=66, blank=True, null=True)
    # raw_data = JSONField(default=dict)

    class Meta:
        db_table = 'swaps_failed'
        indexes = [
            models.Index(fields=['taker_coin']),
            models.Index(fields=['maker_coin']),
            models.Index(fields=['taker_gui']),
            models.Index(fields=['maker_gui']),
            models.Index(fields=['taker_pubkey']),
            models.Index(fields=['maker_pubkey']),
            models.Index(fields=['taker_version']),
            models.Index(fields=['maker_version']),
            models.Index(fields=['taker_error_type']),
            models.Index(fields=['maker_error_type'])
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['uuid'],
                name='unique_swaps_failed'
            )
        ]
