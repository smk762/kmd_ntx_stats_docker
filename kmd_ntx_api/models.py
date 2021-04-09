from django.db import models
from django.contrib.postgres.fields import ArrayField, JSONField


class addresses(models.Model):
    season = models.CharField(max_length=34)
    notary = models.CharField(max_length=34)
    notary_id = models.CharField(max_length=34)
    chain = models.CharField(max_length=34)
    address = models.CharField(max_length=34)
    pubkey = models.CharField(max_length=66)
    node = models.CharField(max_length=34)

    class Meta:
        db_table = 'addresses'
        constraints = [
            models.UniqueConstraint(
                fields=['address', "season", "chain"],
                name='unique_season_chain_address'
            )
        ]


class balances(models.Model):
    notary = models.CharField(max_length=34)
    chain = models.CharField(max_length=34)
    balance = models.DecimalField(max_digits=18, decimal_places=8)
    address = models.CharField(max_length=34)
    season = models.CharField(max_length=34)
    node = models.CharField(max_length=34)
    update_time = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'balances'
        constraints = [
            models.UniqueConstraint(
                fields=['chain', 'address', 'season'],
                name='unique_chain_address_season_balance'
            )
        ]


# TODO: Awaiting delegation to crons / db table
class chain_sync(models.Model):
    chain = models.CharField(max_length=64)
    block_height = models.PositiveIntegerField(default=0)
    sync_hash = models.CharField(max_length=64)
    explorer_hash = models.CharField(max_length=64)

    class Meta:
        db_table = 'chain_sync'
        constraints = [
            models.UniqueConstraint(
                fields=['chain'],
                name='unique_chain_sync'
            )
        ]


class coins(models.Model):
    chain = models.CharField(max_length=34)
    coins_info = JSONField(default=dict)
    electrums = JSONField(default=dict)
    electrums_ssl = JSONField(default=dict)
    explorers = JSONField(default=dict)
    dpow = JSONField(default=dict)
    dpow_tenure = JSONField(default=dict)
    dpow_active = models.PositiveIntegerField(default=0)
    mm2_compatible = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'coins'
        constraints = [
            models.UniqueConstraint(
                fields=['chain'],
                name='unique_chain_coin'
            )
        ]


class coin_social(models.Model):
    chain = models.CharField(max_length=128)
    twitter = models.CharField(max_length=128)
    youtube = models.CharField(max_length=128)
    discord = models.CharField(max_length=128)
    telegram = models.CharField(max_length=128)
    github = models.CharField(max_length=128)
    website = models.CharField(max_length=128)
    explorer = models.CharField(max_length=128)
    icon = models.CharField(max_length=128)
    season = models.CharField(max_length=128)

    class Meta:
        db_table = 'coin_social'
        constraints = [
            models.UniqueConstraint(
                fields=['chain', 'season'],
                name='unique_chain_season_social'
            )
        ]

# Not in use, will implement S5
class funding_transactions(models.Model):
    chain = models.CharField(max_length=128)
    txid = models.CharField(max_length=128)
    vout = models.PositiveIntegerField(default=0)
    amount = models.DecimalField(max_digits=18, decimal_places=8)

    address = models.CharField(max_length=128)
    notary = models.CharField(max_length=128)
    block_hash = models.CharField(max_length=128)
    block_height = models.PositiveIntegerField(default=0)
    block_time = models.PositiveIntegerField(default=0)

    category = models.CharField(max_length=128)
    fee = models.DecimalField(max_digits=18, decimal_places=8)
    season = models.CharField(max_length=128)

    class Meta:
        db_table = 'funding_transactions'
        constraints = [
            models.UniqueConstraint(
                fields=['txid', 'vout', 'category'],
                name='unique_category_vout_txid_funding'
            )
        ]


class last_btc_notarised(models.Model):
    notary = models.CharField(max_length=64)
    txid = models.CharField(max_length=64)
    block_height = models.PositiveIntegerField(default=0)
    block_time = models.PositiveIntegerField(default=0)
    season = models.CharField(max_length=32)

    class Meta:
        db_table = 'last_btc_notarised'
        constraints = [
            models.UniqueConstraint(
                fields=['notary'],
                name='unique_notary_btc_ntx'
            )
        ]


class last_notarised(models.Model):
    notary = models.CharField(max_length=64)
    chain = models.CharField(max_length=32)
    txid = models.CharField(max_length=64)
    block_height = models.PositiveIntegerField(default=0)
    block_time = models.PositiveIntegerField(default=0)
    season = models.CharField(max_length=32)

    class Meta:
        db_table = 'last_notarised'
        indexes = [
            models.Index(fields=['block_time'])
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['notary','chain'],
                name='unique_notary_chain'
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
    season = models.CharField(max_length=34)

    class Meta:
        db_table = 'mined'
        constraints = [
            models.UniqueConstraint(
                fields=['block_height'], 
                name='unique_block'
            )
        ]


class mined_count_daily(models.Model):
    mined_date = models.DateField()
    notary = models.CharField(max_length=64)
    blocks_mined = models.PositiveIntegerField(default=0)
    sum_value_mined = models.DecimalField(max_digits=18, decimal_places=8)
    time_stamp = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'mined_count_daily'
        constraints = [
            models.UniqueConstraint(
                fields=['notary', 'mined_date'],
                name='unique_notary_daily_mined'
            )
        ]


class mined_count_season(models.Model):
    notary = models.CharField(max_length=64)
    address = models.CharField(max_length=64, default='f')
    blocks_mined = models.PositiveIntegerField(default=0)
    sum_value_mined = models.DecimalField(max_digits=18, decimal_places=8)
    max_value_mined = models.DecimalField(max_digits=18, decimal_places=8)
    last_mined_block = models.PositiveIntegerField(default=0)
    last_mined_blocktime = models.PositiveIntegerField(default=0)
    time_stamp = models.PositiveIntegerField(default=0)
    season = models.CharField(max_length=34)

    class Meta:
        db_table = 'mined_count_season'
        constraints = [
            models.UniqueConstraint(
                fields=['notary', 'season'],
                name='unique_notary_season_mined'
            )
        ]


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
    input_sats = models.IntegerField(default=-1)
    output_index = models.IntegerField(default=-1)
    output_sats = models.IntegerField(default=-1)
    num_inputs = models.PositiveIntegerField(default=0)
    num_outputs = models.PositiveIntegerField(default=0)
    fees = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'nn_btc_tx'
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
    input_sats = models.IntegerField(default=-1)
    output_index = models.IntegerField(default=-1)
    output_sats = models.IntegerField(default=-1)
    num_inputs = models.PositiveIntegerField(default=0)
    num_outputs = models.PositiveIntegerField(default=0)
    fees = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'nn_ltc_tx'
        constraints = [
            models.UniqueConstraint(fields=['txid', 'address', 'input_index', 'output_index'],
                                 name='unique_ltc_nn_txid')
        ]


class nn_social(models.Model):
    notary = models.CharField(max_length=128)
    twitter = models.CharField(max_length=128)
    youtube = models.CharField(max_length=128)
    discord = models.CharField(max_length=128)
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
    chain = models.CharField(max_length=32)
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
    btc_validated = models.CharField(max_length=32, default='')

    class Meta:
        db_table = 'notarised'
        constraints = [
            models.UniqueConstraint(fields=['txid'],
                                 name='unique_txid')
        ]


class notarised_btc(models.Model):
    btc_txid = models.CharField(max_length=64)
    btc_block_hash = models.CharField(max_length=64)
    btc_block_ht = models.PositiveIntegerField(default=0)
    btc_block_time = models.PositiveIntegerField(default=0)
    addresses = ArrayField(models.CharField(max_length=34),size=13)
    notaries = ArrayField(models.CharField(max_length=34),size=13)
    kmd_txid = models.CharField(max_length=64)
    kmd_block_hash = models.CharField(max_length=64)
    kmd_block_ht = models.PositiveIntegerField(default=0)
    kmd_block_time = models.PositiveIntegerField(default=0)
    opret = models.CharField(max_length=2048)
    season = models.CharField(max_length=32)

    class Meta:
        db_table = 'notarised_btc'
        constraints = [
            models.UniqueConstraint(fields=['btc_txid'],
                                 name='unique_btc_txid')
        ]


class notarised_chain_daily(models.Model):
    notarised_date = models.DateField()
    chain = models.CharField(max_length=64)
    ntx_count = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'notarised_chain_daily'
        constraints = [
            models.UniqueConstraint(
                fields=['chain', 'notarised_date'],
                name='unique_notarised_chain_date'
            )
        ]


class notarised_chain_season(models.Model):
    chain = models.CharField(max_length=64)
    ntx_count = models.PositiveIntegerField(default=0)
    block_height = models.PositiveIntegerField(default=0)
    kmd_ntx_blockhash = models.CharField(max_length=64)
    kmd_ntx_txid = models.CharField(max_length=64)
    kmd_ntx_blocktime = models.PositiveIntegerField(default=0)
    opret = models.CharField(max_length=2048)
    ac_ntx_blockhash = models.CharField(max_length=64)
    ac_ntx_height = models.PositiveIntegerField(default=0)
    ac_block_height = models.CharField(max_length=34)
    ntx_lag = models.CharField(max_length=34)
    season = models.CharField(max_length=34)

    class Meta:
        db_table = 'notarised_chain_season'
        constraints = [
            models.UniqueConstraint(
                fields=['chain', 'season'],
                name='unique_notarised_chain_season'
            )
        ]


class notarised_count_daily(models.Model):
    notarised_date = models.DateField()
    notary = models.CharField(max_length=64)
    btc_count = models.PositiveIntegerField(default=0)
    antara_count = models.PositiveIntegerField(default=0)
    third_party_count = models.PositiveIntegerField(default=0)
    other_count = models.PositiveIntegerField(default=0)
    total_ntx_count = models.PositiveIntegerField(default=0)
    chain_ntx_counts = JSONField(default=dict)
    chain_ntx_pct = JSONField(default=dict)
    time_stamp = models.PositiveIntegerField(default=0)
    season = models.CharField(max_length=34)

    class Meta:
        db_table = 'notarised_count_daily'
        constraints = [
            models.UniqueConstraint(
                fields=['notary', "notarised_date"],
                name='unique_notary_date'
            )
        ]


class notarised_count_season(models.Model):
    notary = models.CharField(max_length=64)
    btc_count = models.PositiveIntegerField(default=0)
    antara_count = models.PositiveIntegerField(default=0)
    third_party_count = models.PositiveIntegerField(default=0)
    other_count = models.PositiveIntegerField(default=0)
    total_ntx_count = models.PositiveIntegerField(default=0)
    chain_ntx_counts = JSONField(default=dict)
    chain_ntx_pct = JSONField(default=dict)
    season_score = models.DecimalField(max_digits=18, decimal_places=8, default=0)
    time_stamp = models.PositiveIntegerField(default=0)
    season = models.CharField(max_length=34)

    class Meta:
        db_table = 'notarised_count_season'
        constraints = [
            models.UniqueConstraint(
                fields=['notary', "season"],
                name='unique_notary_season'
            )
        ]


class notarised_tenure(models.Model):
    chain = models.CharField(max_length=64)
    first_ntx_block = models.PositiveIntegerField(default=0)
    last_ntx_block = models.PositiveIntegerField(default=0)
    first_ntx_block_time = models.PositiveIntegerField(default=0)
    last_ntx_block_time = models.PositiveIntegerField(default=0)
    official_start_block_time = models.PositiveIntegerField(default=0)
    official_end_block_time = models.PositiveIntegerField(default=0)
    unscored_ntx_count = models.PositiveIntegerField(default=0)
    scored_ntx_count = models.PositiveIntegerField(default=0)
    server = models.CharField(max_length=32, default="Unofficial")
    season = models.CharField(max_length=32, default="Unofficial")

    class Meta:
        db_table = 'notarised_tenure'
        constraints = [
            models.UniqueConstraint(
                fields=['chain','season', 'server'],
                name='unique_chain_season_server_tenure'
            )
        ]


class rewards(models.Model):
    address = models.CharField(max_length=34)
    notary = models.CharField(max_length=34)
    utxo_count = models.PositiveIntegerField(default=0)
    eligible_utxo_count = models.PositiveIntegerField(default=0)
    oldest_utxo_block = models.PositiveIntegerField(default=0)
    balance = models.DecimalField(max_digits=18, decimal_places=8)
    rewards = models.DecimalField(max_digits=18, decimal_places=8)
    update_time = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'rewards'
        constraints = [
            models.UniqueConstraint(
                fields=['address'],
                name='unique_reward_address'
            )
        ]


class scoring_epochs(models.Model):
    season = models.CharField(max_length=128)
    server = models.CharField(max_length=128)
    epoch = models.CharField(max_length=128)
    epoch_start = models.PositiveIntegerField(default=0)
    epoch_end = models.PositiveIntegerField(default=0)
    start_event = models.CharField(max_length=128)
    end_event = models.CharField(max_length=128)
    epoch_chains = ArrayField(models.CharField(max_length=34), default=list)
    score_per_ntx = models.DecimalField(max_digits=18, decimal_places=8)

    class Meta:
        db_table = 'scoring_epochs'
        constraints = [
            models.UniqueConstraint(
                fields=['season', 'server', 'epoch'],
                name='unique_scoring_epoch'
            )
        ]


# to make migrations, use "docker-compose run web python3 manage.py makemigrations"
# to apply migrations, use "docker-compose run web python3 manage.py migrate"
# to update static files, use "docker-compose run web python3 manage.py collectstatic"
