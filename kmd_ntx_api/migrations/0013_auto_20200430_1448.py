# Generated by Django 2.2 on 2020-04-30 14:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kmd_ntx_api', '0012_notarised_opret'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notarised',
            name='opret',
            field=models.CharField(max_length=512),
        ),
    ]