from django.db import models
from django.contrib.postgres.fields import ArrayField, JSONField

class addresses(models.Model):
    season = models.CharField(max_length=34)
    notary_name = models.CharField(max_length=34)
    notary_id = models.CharField(max_length=34)
    chain = models.CharField(max_length=34)
    address = models.CharField(max_length=34)
    pubkey = models.CharField(max_length=66)

    class Meta:
        db_table = 'addresses'
        constraints = [
            models.UniqueConstraint(fields=['address', "season", "chain"], name='unique_season_chain_address')
        ]

class notarised(models.Model):
    txid = models.CharField(max_length=64)
    chain = models.CharField(max_length=32)
    block_hash = models.CharField(max_length=64)
    block_time = models.PositiveIntegerField()
    block_ht = models.PositiveIntegerField()
    notaries = ArrayField(models.CharField(max_length=34),size=13)
    prev_block_hash = models.CharField(max_length=64)
    prev_block_ht = models.PositiveIntegerField()
    opret = models.CharField(max_length=2048)

    class Meta:
        db_table = 'notarised'
        constraints = [
            models.UniqueConstraint(fields=['txid'], name='unique_txid')
        ]

class notarised_count(models.Model):
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
        db_table = 'notarised_count'
        constraints = [
            models.UniqueConstraint(fields=['notary', "season"], name='unique_notary_season')
        ]

class notarised_chain(models.Model):
    chain = models.CharField(max_length=64)
    ntx_count = models.PositiveIntegerField()
    kmd_ntx_height = models.PositiveIntegerField()
    kmd_ntx_blockhash = models.CharField(max_length=64)
    kmd_ntx_txid = models.CharField(max_length=64)
    lastnotarization = models.PositiveIntegerField()
    opret = models.CharField(max_length=2048)
    ac_ntx_block_hash = models.CharField(max_length=64)
    ac_ntx_height = models.PositiveIntegerField()
    ac_block_height = models.CharField(max_length=34)
    ntx_lag = models.CharField(max_length=34)

    class Meta:
        db_table = 'notarised_chain'
        constraints = [
            models.UniqueConstraint(fields=['chain'], name='unique_chain')
        ]

class mined(models.Model):
    block = models.PositiveIntegerField()
    block_time = models.PositiveIntegerField()
    value = models.DecimalField(max_digits=18, decimal_places=8)
    address = models.CharField(max_length=34)
    name = models.CharField(max_length=34)
    txid = models.CharField(max_length=64)
    season = models.CharField(max_length=34)

    class Meta:
        db_table = 'mined'
        constraints = [
            models.UniqueConstraint(fields=['block'], name='unique_block')
        ]

class mined_count(models.Model):
    notary = models.CharField(max_length=64)
    blocks_mined = models.PositiveIntegerField()
    sum_value_mined = models.DecimalField(max_digits=18, decimal_places=8)
    max_value_mined = models.DecimalField(max_digits=18, decimal_places=8)
    last_mined_block = models.PositiveIntegerField()
    last_mined_blocktime = models.PositiveIntegerField()
    time_stamp = models.PositiveIntegerField()
    season = models.CharField(max_length=34)

    class Meta:
        db_table = 'mined_count'
        constraints = [
            models.UniqueConstraint(fields=['notary', 'season'], name='unique_notary_season_mined')
        ]

class balances(models.Model):
    notary = models.CharField(max_length=34)
    chain = models.CharField(max_length=34)
    balance = models.DecimalField(max_digits=18, decimal_places=8)
    address = models.CharField(max_length=34)
    update_time = models.PositiveIntegerField()

    class Meta:
        db_table = 'balances'
        constraints = [
            models.UniqueConstraint(fields=['notary', 'chain', 'address'], name='unique_notary_chain_addr_balance')
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
            models.UniqueConstraint(fields=['address'], name='unique_reward_address')
        ]

class coins(models.Model):
    chain = models.CharField(max_length=34)
    coins_info = JSONField()
    electrums = JSONField()
    electrums_ssl = JSONField()
    explorers = JSONField()
    dpow = JSONField()


    class Meta:
        db_table = 'coins'
        constraints = [
            models.UniqueConstraint(fields=['chain'], name='unique_chain_coin')
        ]

# to make migrations, use "docker-compose run web python3 manage.py makemigrations"
# to apply migrations, use "docker-compose run web python3 manage.py migrate"