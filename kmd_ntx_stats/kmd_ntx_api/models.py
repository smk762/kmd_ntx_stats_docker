from django.db import models

class mined(models.Model):
    block = models.PositiveIntegerField()
    value = models.DecimalField(max_digits=14, decimal_places=8)
    address = models.CharField(max_length=34)
    name = models.CharField(max_length=34)

class notarised(models.Model):
    txid = models.CharField(max_length=64)
    chain = models.CharField(max_length=12)
    block_hash = models.CharField(max_length=64)
    block_ht = models.PositiveIntegerField()
    notaries = models.ArrayField(models.CharField(max_length=34),size=13)
    prev_block_hash = models.CharField(max_length=64)
    prev_block_ht = models.PositiveIntegerField()

