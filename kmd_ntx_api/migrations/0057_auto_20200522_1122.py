# Generated by Django 2.2 on 2020-05-22 11:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kmd_ntx_api', '0056_auto_20200520_1126'),
    ]

    operations = [
        migrations.CreateModel(
            name='nn_social',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('notary', models.CharField(max_length=128)),
                ('twitter', models.CharField(max_length=128)),
                ('youtube', models.CharField(max_length=128)),
                ('discord', models.CharField(max_length=128)),
                ('telegram', models.CharField(max_length=128)),
                ('github', models.CharField(max_length=128)),
                ('keybase', models.CharField(max_length=128)),
                ('website', models.CharField(max_length=128)),
            ],
            options={
                'db_table': 'nn_social',
            },
        ),
        migrations.AddConstraint(
            model_name='nn_social',
            constraint=models.UniqueConstraint(fields=('notary',), name='unique_notary_social'),
        ),
    ]
