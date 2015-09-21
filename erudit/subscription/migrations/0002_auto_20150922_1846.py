# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('subscription', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='client',
            options={'verbose_name': 'Client', 'verbose_name_plural': 'Clients'},
        ),
        migrations.AlterModelOptions(
            name='product',
            options={'verbose_name': 'Produit', 'verbose_name_plural': 'Produits'},
        ),
        migrations.AlterModelOptions(
            name='renewalnotice',
            options={'verbose_name': 'Avis de renouvellement', 'verbose_name_plural': 'Avis de renouvellement'},
        ),
        migrations.AddField(
            model_name='client',
            name='erudit_number',
            field=models.CharField(max_length=120, default=11),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='renewalnotice',
            name='paying_customer',
            field=models.ForeignKey(to='subscription.Client', related_name='paid_renewals'),
        ),
        migrations.AlterField(
            model_name='renewalnotice',
            name='receiving_customer',
            field=models.ForeignKey(to='subscription.Client', related_name='received_renewals'),
        ),
    ]
