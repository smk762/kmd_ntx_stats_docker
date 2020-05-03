from django.db import models
from django.contrib.postgres.fields import ArrayField, JSONField

class addresses(models.Model):
    notary_id = models.PositiveIntegerField()
    notary_name = models.CharField(max_length=34)
    address = models.CharField(max_length=34)
    pubkey = models.CharField(max_length=66)
    season = models.CharField(max_length=34)

    class Meta:
        db_table = 'addresses'
        constraints = [
            models.UniqueConstraint(fields=['address', "season"], name='unique_season_address')
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
    json_count = JSONField()
    time_stamp = models.PositiveIntegerField()
    season = models.CharField(max_length=34)

    class Meta:
        db_table = 'notarised_count'

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


class mined(models.Model):
    block = models.PositiveIntegerField()
    block_time = models.PositiveIntegerField()
    value = models.DecimalField(max_digits=18, decimal_places=8)
    address = models.CharField(max_length=34)
    name = models.CharField(max_length=34)
    txid = models.CharField(max_length=64)

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

# to make migrations, use "docker-compose run web python3 manage.py makemigrations"
# to apply migrations, use "docker-compose run web python3 manage.py migrate"