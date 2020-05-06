# Generated by Django 2.2 on 2020-05-04 02:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kmd_ntx_api', '0019_auto_20200503_1459'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='addresses',
            name='unique_season_address',
        ),
        migrations.AddField(
            model_name='addresses',
            name='coin',
            field=models.CharField(default='', max_length=34),
            preserve_default=False,
        ),
        migrations.AddConstraint(
            model_name='addresses',
            constraint=models.UniqueConstraint(fields=('address', 'season', 'coin'), name='unique_season_coin_address'),
        ),
    ]