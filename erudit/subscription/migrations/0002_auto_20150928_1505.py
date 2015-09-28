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
            options={'verbose_name_plural': 'Clients', 'verbose_name': 'Client'},
        ),
        migrations.AlterModelOptions(
            name='product',
            options={'verbose_name_plural': 'Produits', 'verbose_name': 'Produit'},
        ),
        migrations.AlterModelOptions(
            name='renewalnotice',
            options={'verbose_name_plural': 'Avis de renouvellement', 'verbose_name': 'Avis de renouvellement'},
        ),
        migrations.AlterField(
            model_name='renewalnotice',
            name='paying_customer',
            field=models.ForeignKey(related_name='paid_renewals', to='subscription.Client'),
        ),
        migrations.AlterField(
            model_name='renewalnotice',
            name='receiving_customer',
            field=models.ForeignKey(related_name='received_renewals', to='subscription.Client'),
        ),
    ]
