# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('erudit', '0003_auto_20160219_1716'),
    ]

    operations = [
        migrations.CreateModel(
            name='EruditDocument',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('localidentifier', models.CharField(null=True, blank=True, verbose_name='Identifiant Fedora', max_length=50)),
            ],
            options={
                'verbose_name': 'Document Érudit',
                'verbose_name_plural': 'Documents Érudit',
            },
        ),
    ]
