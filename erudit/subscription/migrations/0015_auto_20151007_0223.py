# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os

from django.core import serializers
from django.db import models, migrations


DATA_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CURRENCY_DATA_PATH = DATA_DIR + '/data/currency.json'
COUNTRY_DATA_PATH = DATA_DIR + '/data/country.json'


def import_json_data(data_path):
    data = ""
    with open(data_path) as f:
        for line in f.readlines():
            data = data + line

    for obj in serializers.deserialize('json', data):
        obj.save()


def import_currencies(apps, schema_editor):
    import_json_data(CURRENCY_DATA_PATH)


def import_countries(apps, schema_editor):
    import_json_data(COUNTRY_DATA_PATH)


class Migration(migrations.Migration):

    dependencies = [
        ('subscription', '0014_auto_20151006_2001'),
    ]

    operations = [
        migrations.RunPython(import_currencies),
        migrations.RunPython(import_countries),
    ]
