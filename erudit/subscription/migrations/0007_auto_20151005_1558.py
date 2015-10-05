# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('subscription', '0006_merge'),
    ]

    operations = [
        migrations.AlterField(
            model_name='client',
            name='city',
            field=models.CharField(max_length=100, blank=True, null=True, verbose_name='Ville'),
        ),
        migrations.AlterField(
            model_name='client',
            name='civic',
            field=models.TextField(blank=True, null=True, verbose_name='Numéro civique'),
        ),
        migrations.AlterField(
            model_name='client',
            name='country',
            field=models.CharField(max_length=100, blank=True, null=True, verbose_name='Pays'),
        ),
        migrations.AlterField(
            model_name='client',
            name='firstname',
            field=models.CharField(max_length=50, blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='client',
            name='street',
            field=models.TextField(blank=True, null=True, verbose_name='Rue'),
        ),
    ]
