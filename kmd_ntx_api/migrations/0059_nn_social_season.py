# Generated by Django 2.2 on 2020-05-23 03:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kmd_ntx_api', '0058_nn_social_icon'),
    ]

    operations = [
        migrations.AddField(
            model_name='nn_social',
            name='season',
            field=models.CharField(default='Season_3', max_length=128),
            preserve_default=False,
        ),
    ]
