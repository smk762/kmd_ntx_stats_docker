from django.db import models
from django.contrib.postgres.fields import ArrayField, JSONField



class mined(models.Model):
    block = models.PositiveIntegerField()
    block_time = models.PositiveIntegerField()
    value = models.DecimalField(max_digits=14, decimal_places=8)
    address = models.CharField(max_length=34)
    name = models.CharField(max_length=34)

    class Meta:
        db_table = 'mined'
        constraints = [
            models.UniqueConstraint(fields=['block'], name='unique_block')
        ]

class notarised(models.Model):
    txid = models.CharField(max_length=64)
    chain = models.CharField(max_length=12)
    block_hash = models.CharField(max_length=64)
    block_time = models.PositiveIntegerField()
    block_ht = models.PositiveIntegerField()
    notaries = ArrayField(models.CharField(max_length=34),size=13)
    prev_block_hash = models.CharField(max_length=64)
    prev_block_ht = models.PositiveIntegerField()

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
    timestamp = models.PositiveIntegerField()

    class Meta:
        db_table = 'notarised_count'

class mined_count(models.Model):
    notary = models.CharField(max_length=64)
    sum_mined = models.DecimalField(max_digits=18, decimal_places=8)
    max_mined = models.DecimalField(max_digits=18, decimal_places=8)
    timestamp = models.PositiveIntegerField()
    last_mined = models.PositiveIntegerField()

    class Meta:
        db_table = 'mined_count'
