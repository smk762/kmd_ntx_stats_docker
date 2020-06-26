from django.db import models
from django.contrib.postgres.fields import ArrayField, JSONField

# NOTARISATION

class notarised(models.Model):
    txid = models.CharField(max_length=64)
    chain = models.CharField(max_length=32)
    block_hash = models.CharField(max_length=64)
    block_time = models.PositiveIntegerField()
    block_datetime = models.DateTimeField()
    block_height = models.PositiveIntegerField()
    notaries = ArrayField(models.CharField(max_length=34),size=13)
    ac_ntx_blockhash = models.CharField(max_length=64)
    ac_ntx_height = models.PositiveIntegerField()
    opret = models.CharField(max_length=2048)
    season = models.CharField(max_length=32)
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
    btc_block_ht = models.PositiveIntegerField()
    btc_block_time = models.PositiveIntegerField()
    addresses = ArrayField(models.CharField(max_length=34),size=13)
    notaries = ArrayField(models.CharField(max_length=34),size=13)
    kmd_txid = models.CharField(max_length=64)
    kmd_block_hash = models.CharField(max_length=64)
    kmd_block_ht = models.PositiveIntegerField()
    kmd_block_time = models.PositiveIntegerField()
    opret = models.CharField(max_length=2048)
    season = models.CharField(max_length=32)

    class Meta:
        db_table = 'notarised_btc'
        constraints = [
            models.UniqueConstraint(fields=['btc_txid'],
                                 name='unique_btc_txid')
        ]

class last_notarised(models.Model):
    notary = models.CharField(max_length=64)
    chain = models.CharField(max_length=32)
    txid = models.CharField(max_length=64)
    block_height = models.PositiveIntegerField()
    block_time = models.PositiveIntegerField()
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

class notarised_tenure(models.Model):
    chain = models.CharField(max_length=64)
    first_ntx_block = models.PositiveIntegerField()
    last_ntx_block = models.PositiveIntegerField()
    first_ntx_block_time = models.PositiveIntegerField()
    last_ntx_block_time = models.PositiveIntegerField()
    ntx_count = models.PositiveIntegerField()
    season = models.CharField(max_length=32)

    class Meta:
        db_table = 'notarised_tenure'
        constraints = [
            models.UniqueConstraint(
                fields=['chain','season'],
                name='unique_chain_season_tenure'
            )
        ]

class last_btc_notarised(models.Model):
    notary = models.CharField(max_length=64)
    txid = models.CharField(max_length=64)
    block_height = models.PositiveIntegerField()
    block_time = models.PositiveIntegerField()
    season = models.CharField(max_length=32)

    class Meta:
        db_table = 'last_btc_notarised'
        constraints = [
            models.UniqueConstraint(
                fields=['notary'],
                name='unique_notary_btc_ntx'
            )
        ]

class notarised_count_season(models.Model):
    notary = models.CharField(max_length=64)
    btc_count = models.PositiveIntegerField()
    antara_count = models.PositiveIntegerField()
    third_party_count = models.PositiveIntegerField()
    other_count = models.PositiveIntegerField()
    total_ntx_count = models.PositiveIntegerField()
    chain_ntx_counts = JSONField()
    chain_ntx_pct = JSONField()
    time_stamp = models.PositiveIntegerField()
    season = models.CharField(max_length=34)

    class Meta:
        db_table = 'notarised_count_season'
        constraints = [
            models.UniqueConstraint(
                fields=['notary', "season"],
                name='unique_notary_season'
            )
        ]

class notarised_count_daily(models.Model):
    notarised_date = models.DateField()
    notary = models.CharField(max_length=64)
    btc_count = models.PositiveIntegerField()
    antara_count = models.PositiveIntegerField()
    third_party_count = models.PositiveIntegerField()
    other_count = models.PositiveIntegerField()
    total_ntx_count = models.PositiveIntegerField()
    chain_ntx_counts = JSONField()
    chain_ntx_pct = JSONField()
    time_stamp = models.PositiveIntegerField()
    season = models.CharField(max_length=34)

    class Meta:
        db_table = 'notarised_count_daily'
        constraints = [
            models.UniqueConstraint(
                fields=['notary', "notarised_date"],
                name='unique_notary_date'
            )
        ]

class notarised_chain_season(models.Model):
    chain = models.CharField(max_length=64)
    ntx_count = models.PositiveIntegerField()
    block_height = models.PositiveIntegerField()
    kmd_ntx_blockhash = models.CharField(max_length=64)
    kmd_ntx_txid = models.CharField(max_length=64)
    kmd_ntx_blocktime = models.PositiveIntegerField()
    opret = models.CharField(max_length=2048)
    ac_ntx_blockhash = models.CharField(max_length=64)
    ac_ntx_height = models.PositiveIntegerField()
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

class notarised_chain_daily(models.Model):
    notarised_date = models.DateField()
    chain = models.CharField(max_length=64)
    ntx_count = models.PositiveIntegerField()

    class Meta:
        db_table = 'notarised_chain_daily'
        constraints = [
            models.UniqueConstraint(
                fields=['chain', 'notarised_date'],
                name='unique_notarised_chain_date'
            )
        ]

# MINING

class mined(models.Model):
    block_height = models.PositiveIntegerField()
    block_time = models.PositiveIntegerField()
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

class chain_sync(models.Model):
    chain = models.CharField(max_length=64)
    block_height = models.PositiveIntegerField()
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

class mined_count_season(models.Model):
    notary = models.CharField(max_length=64)
    blocks_mined = models.PositiveIntegerField()
    sum_value_mined = models.DecimalField(max_digits=18, decimal_places=8)
    max_value_mined = models.DecimalField(max_digits=18, decimal_places=8)
    last_mined_block = models.PositiveIntegerField()
    last_mined_blocktime = models.PositiveIntegerField()
    time_stamp = models.PositiveIntegerField()
    season = models.CharField(max_length=34)

    class Meta:
        db_table = 'mined_count_season'
        constraints = [
            models.UniqueConstraint(
                fields=['notary', 'season'],
                name='unique_notary_season_mined'
            )
        ]

class mined_count_daily(models.Model):
    mined_date = models.DateField()
    notary = models.CharField(max_length=64)
    blocks_mined = models.PositiveIntegerField()
    sum_value_mined = models.DecimalField(max_digits=18, decimal_places=8)
    time_stamp = models.PositiveIntegerField()

    class Meta:
        db_table = 'mined_count_daily'
        constraints = [
            models.UniqueConstraint(
                fields=['notary', 'mined_date'],
                name='unique_notary_daily_mined'
            )
        ]

# WALLET

class balances(models.Model):
    notary = models.CharField(max_length=34)
    chain = models.CharField(max_length=34)
    balance = models.DecimalField(max_digits=18, decimal_places=8)
    address = models.CharField(max_length=34)
    season = models.CharField(max_length=34)
    node = models.CharField(max_length=34)
    update_time = models.PositiveIntegerField()

    class Meta:
        db_table = 'balances'
        constraints = [
            models.UniqueConstraint(
                fields=['chain', 'address', 'season'],
                name='unique_chain_address_season_balance'
            )
        ]

class rewards(models.Model):
    address = models.CharField(max_length=34)
    notary = models.CharField(max_length=34)
    utxo_count = models.PositiveIntegerField()
    eligible_utxo_count = models.PositiveIntegerField()
    oldest_utxo_block = models.PositiveIntegerField()
    balance = models.DecimalField(max_digits=18, decimal_places=8)
    rewards = models.DecimalField(max_digits=18, decimal_places=8)
    update_time = models.PositiveIntegerField()

    class Meta:
        db_table = 'rewards'
        constraints = [
            models.UniqueConstraint(
                fields=['address'],
                name='unique_reward_address'
            )
        ]

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

# INFO

class coins(models.Model):
    chain = models.CharField(max_length=34)
    coins_info = JSONField()
    electrums = JSONField()
    electrums_ssl = JSONField()
    explorers = JSONField()
    dpow = JSONField()
    dpow_active = models.PositiveIntegerField()
    mm2_compatible = models.PositiveIntegerField()

    class Meta:
        db_table = 'coins'
        constraints = [
            models.UniqueConstraint(
                fields=['chain'],
                name='unique_chain_coin'
            )
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

class funding_transactions(models.Model):
    chain = models.CharField(max_length=128)
    txid = models.CharField(max_length=128)
    vout = models.PositiveIntegerField()
    amount = models.DecimalField(max_digits=18, decimal_places=8)

    address = models.CharField(max_length=128)
    notary = models.CharField(max_length=128)
    block_hash = models.CharField(max_length=128)
    block_height = models.PositiveIntegerField()
    block_time = models.PositiveIntegerField()

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
# to make migrations, use "docker-compose run web python3 manage.py makemigrations"
# to apply migrations, use "docker-compose run web python3 manage.py migrate"