# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('erudit', '0007_auto_20160223_1546'),
    ]

    operations = [
        migrations.AlterField(
            model_name='eruditdocument',
            name='localidentifier',
            field=models.CharField(unique=True, max_length=50, verbose_name='Identifiant Fedora'),
        ),
        migrations.AlterField(
            model_name='issue',
            name='localidentifier',
            field=models.CharField(unique=True, max_length=50, verbose_name='Identifiant Fedora'),
        ),
        migrations.AlterField(
            model_name='journal',
            name='localidentifier',
            field=models.CharField(unique=True, max_length=50, verbose_name='Identifiant Fedora'),
        ),
    ]
