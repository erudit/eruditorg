# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


currency_locale = {
    'EUR': 'fr_FR',
    'CAD': 'fr_CA',
    'USD': 'en_US',
}


def create_locales(apps, schema_editor):
    # We can't import the Person model directly as it may be a newer
    # version than this migration expects. We use the historical version.
    Country = apps.get_model("subscription", "country")
    for country in Country.objects.all():
        country.locale = currency_locale.get(country.currency.code)
        country.save()


class Migration(migrations.Migration):

    dependencies = [
        ('subscription', '0016_country_locale'),
    ]

    operations = [
        migrations.RunPython(create_locales),
    ]
