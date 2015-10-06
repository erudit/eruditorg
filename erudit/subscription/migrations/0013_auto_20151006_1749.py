# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('subscription', '0012_auto_20151006_1727'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='amount',
            field=models.DecimalField(max_digits=7, default=0.0, decimal_places=2, verbose_name='Montant 2016'),
        ),
        migrations.AlterField(
            model_name='renewalnotice',
            name='amount_total',
            field=models.DecimalField(help_text='Montant des articles demandés (sous-total avant Rabais)', default=0.0, decimal_places=2, verbose_name='Montant total', max_digits=7),
        ),
        migrations.AlterField(
            model_name='renewalnotice',
            name='federal_tax',
            field=models.DecimalField(max_digits=7, default=0.0, decimal_places=2, verbose_name='Taxe fédérale'),
        ),
        migrations.AlterField(
            model_name='renewalnotice',
            name='harmonized_tax',
            field=models.DecimalField(max_digits=7, default=0.0, decimal_places=2, verbose_name='Taxe harmonisée'),
        ),
        migrations.AlterField(
            model_name='renewalnotice',
            name='net_amount',
            field=models.DecimalField(help_text='Montant brut + Taxes (total facturable, taxes incl.)', default=0.0, decimal_places=2, verbose_name='Montant net', max_digits=7),
        ),
        migrations.AlterField(
            model_name='renewalnotice',
            name='provincial_tax',
            field=models.DecimalField(max_digits=7, default=0.0, decimal_places=2, verbose_name='Taxe provinciale'),
        ),
        migrations.AlterField(
            model_name='renewalnotice',
            name='raw_amount',
            field=models.DecimalField(help_text='Montant total - Rabais (sous-total après Rabais)', default=0.0, decimal_places=2, verbose_name='Montant brut', max_digits=7),
        ),
        migrations.AlterField(
            model_name='renewalnotice',
            name='rebate',
            field=models.DecimalField(help_text='Applicable avant taxes, sur Montant total', default=0.0, decimal_places=2, verbose_name='Rabais', max_digits=7),
        ),
    ]
