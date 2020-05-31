# Generated by Django 2.2 on 2020-05-31 16:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kmd_ntx_api', '0063_auto_20200526_0435'),
    ]

    operations = [
        migrations.CreateModel(
            name='coin_social',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('chain', models.CharField(max_length=128)),
                ('twitter', models.CharField(max_length=128)),
                ('youtube', models.CharField(max_length=128)),
                ('discord', models.CharField(max_length=128)),
                ('telegram', models.CharField(max_length=128)),
                ('github', models.CharField(max_length=128)),
                ('website', models.CharField(max_length=128)),
                ('explorer', models.CharField(max_length=128)),
                ('icon', models.CharField(max_length=128)),
                ('season', models.CharField(max_length=128)),
            ],
            options={
                'db_table': 'coin_social',
            },
        ),
        migrations.AddConstraint(
            model_name='coin_social',
            constraint=models.UniqueConstraint(fields=('chain', 'season'), name='unique_chain_season_social'),
        ),
    ]
