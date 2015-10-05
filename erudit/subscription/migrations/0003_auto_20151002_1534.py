# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('subscription', '0002_auto_20150928_1505'),
    ]

    operations = [
        migrations.RenameField(
            model_name='client',
            old_name='address',
            new_name='civic',
        ),
        migrations.AddField(
            model_name='client',
            name='currency',
            field=models.CharField(default='', max_length=3, verbose_name='Devise'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='client',
            name='exemption_code',
            field=models.CharField(default='', max_length=1, verbose_name="Code d'exemption"),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='client',
            name='pobox',
            field=models.CharField(default='', max_length=50, verbose_name='Casier postal'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='client',
            name='street',
            field=models.TextField(null=True, verbose_name='Numéro civique', blank=True),
        ),
        migrations.AddField(
            model_name='product',
            name='code',
            field=models.CharField(default='', max_length=30),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='renewalnotice',
            name='renewal_number',
            field=models.CharField(default='', max_length=10, verbose_name="Numéro d'avis"),
            preserve_default=False,
        ),
    ]
