# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os
import json

from django.db import migrations

DATA_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CURRENCY_DATA_PATH = DATA_DIR + '/data/currency.json'
COUNTRY_DATA_PATH = DATA_DIR + '/data/country.json'


def import_currencies(apps, schema_editor):
    currencies = json.loads(open(CURRENCY_DATA_PATH).read())
    Currency = apps.get_model('subscription', 'Currency')
    for currency in currencies:
        curr = Currency()
        curr.code = currency['fields']['code']
        curr.name = currency['fields']['name']
        curr.save()


def import_countries(apps, schema_editor):
    countries = json.loads(open(COUNTRY_DATA_PATH).read())
    Country = apps.get_model('subscription', 'Country')
    Currency = apps.get_model('subscription', 'Currency')
    for country in countries:
        Country.objects.create(
            code=country['fields']['code'],
            name=country['fields']['name'],
            currency=Currency.objects.get(pk=country['fields']['currency']),
        )


class Migration(migrations.Migration):

    dependencies = [
        ('subscription', '0002_auto_20151007_1917'),
    ]

    operations = [
        migrations.RunPython(import_currencies),
        migrations.RunPython(import_countries)
    ]
