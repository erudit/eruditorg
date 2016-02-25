# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('subscription', '0002_institutionalaccount_institutionipaddressrange'),
    ]

    operations = [
        migrations.AddField(
            model_name='institutionalaccount',
            name='badge',
            field=models.ImageField(verbose_name='Badge', upload_to='', null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='individualaccount',
            name='policy',
            field=models.ForeignKey(help_text="Laisser vide si la politique d'accès aux produits est définie plus bas", to='subscription.Policy', blank=True, verbose_name='Accès', related_name='accounts', null=True),
        ),
    ]
