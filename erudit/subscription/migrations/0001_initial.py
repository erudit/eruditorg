# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('erudit', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='Client',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('lastname', models.CharField(max_length=50, verbose_name='Nom')),
                ('firstname', models.CharField(max_length=50, verbose_name='Prénom')),
                ('organisation', models.CharField(max_length=200)),
                ('email', models.EmailField(max_length=254)),
                ('address', models.TextField(blank=True, null=True, verbose_name='Adresse')),
                ('city', models.CharField(max_length=50, verbose_name='Ville')),
                ('province', models.CharField(max_length=50, verbose_name='Province')),
                ('country', models.CharField(max_length=50, verbose_name='Pays')),
                ('postal_code', models.CharField(max_length=50, verbose_name='Code postal')),
            ],
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('title', models.CharField(max_length=200)),
                ('description', models.CharField(max_length=200)),
                ('amount', models.DecimalField(max_digits=7, decimal_places=2)),
                ('titles', models.ManyToManyField(to='subscription.Product')),
            ],
        ),
        migrations.CreateModel(
            name='RenewalNotice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('po_number', models.CharField(max_length=30)),
                ('amount_total', models.DecimalField(max_digits=7, decimal_places=2)),
                ('rebate', models.DecimalField(max_digits=7, decimal_places=2)),
                ('raw_amount', models.DecimalField(max_digits=7, decimal_places=2)),
                ('federal_tax', models.DecimalField(max_digits=7, decimal_places=2)),
                ('provincial_tax', models.DecimalField(max_digits=7, decimal_places=2)),
                ('harmonized_tax', models.DecimalField(max_digits=7, decimal_places=2)),
                ('net_amount', models.DecimalField(max_digits=7, decimal_places=2)),
                ('currency', models.CharField(max_length=5)),
                ('date_created', models.DateField()),
                ('paying_customer', models.ForeignKey(to='erudit.Person', related_name='paid_renewals')),
                ('products', models.ManyToManyField(to='subscription.Product')),
                ('receiving_customer', models.ForeignKey(to='erudit.Person', related_name='received_renewals')),
            ],
        ),
    ]
