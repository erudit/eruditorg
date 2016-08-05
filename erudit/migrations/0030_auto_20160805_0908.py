# -*- coding: utf-8 -*-
# Generated by Django 1.9.9 on 2016-08-05 14:08
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('erudit', '0029_author_othername'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='basket',
            name='journals',
        ),
        migrations.RemoveField(
            model_name='contract',
            name='journal',
        ),
        migrations.RemoveField(
            model_name='contract',
            name='status',
        ),
        migrations.RemoveField(
            model_name='contract',
            name='type',
        ),
        migrations.RemoveField(
            model_name='grant',
            name='currency',
        ),
        migrations.RemoveField(
            model_name='grant',
            name='granting_agency',
        ),
        migrations.RemoveField(
            model_name='grant',
            name='journal',
        ),
        migrations.RemoveField(
            model_name='indexation',
            name='indexer',
        ),
        migrations.RemoveField(
            model_name='indexation',
            name='journal',
        ),
        migrations.RemoveField(
            model_name='invoice',
            name='currency',
        ),
        migrations.RemoveField(
            model_name='invoice',
            name='journal',
        ),
        migrations.RemoveField(
            model_name='journalproduction',
            name='journal',
        ),
        migrations.RemoveField(
            model_name='journalproduction',
            name='production_center',
        ),
        migrations.RemoveField(
            model_name='journalproduction',
            name='production_type',
        ),
        migrations.DeleteModel(
            name='Library',
        ),
        migrations.RemoveField(
            model_name='quotation',
            name='journal',
        ),
        migrations.RemoveField(
            model_name='quotationitem',
            name='currency',
        ),
        migrations.RemoveField(
            model_name='quotationitem',
            name='quotation',
        ),
        migrations.RemoveField(
            model_name='subscriptionprice',
            name='currency',
        ),
        migrations.RemoveField(
            model_name='subscriptionprice',
            name='journal',
        ),
        migrations.RemoveField(
            model_name='subscriptionprice',
            name='type',
        ),
        migrations.RemoveField(
            model_name='subscriptionprice',
            name='zone',
        ),
        migrations.AlterField(
            model_name='eruditdocument',
            name='localidentifier',
            field=models.CharField(db_index=True, max_length=50, unique=True, verbose_name='Identifiant unique'),
        ),
        migrations.DeleteModel(
            name='Basket',
        ),
        migrations.DeleteModel(
            name='Contract',
        ),
        migrations.DeleteModel(
            name='ContractStatus',
        ),
        migrations.DeleteModel(
            name='ContractType',
        ),
        migrations.DeleteModel(
            name='Currency',
        ),
        migrations.DeleteModel(
            name='Grant',
        ),
        migrations.DeleteModel(
            name='GrantingAgency',
        ),
        migrations.DeleteModel(
            name='Indexation',
        ),
        migrations.DeleteModel(
            name='Indexer',
        ),
        migrations.DeleteModel(
            name='Invoice',
        ),
        migrations.DeleteModel(
            name='JournalProduction',
        ),
        migrations.DeleteModel(
            name='ProductionCenter',
        ),
        migrations.DeleteModel(
            name='ProductionType',
        ),
        migrations.DeleteModel(
            name='Quotation',
        ),
        migrations.DeleteModel(
            name='QuotationItem',
        ),
        migrations.DeleteModel(
            name='SubscriptionPrice',
        ),
        migrations.DeleteModel(
            name='SubscriptionType',
        ),
        migrations.DeleteModel(
            name='SubscriptionZone',
        ),
    ]
