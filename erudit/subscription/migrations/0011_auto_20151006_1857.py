# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('subscription', '0010_merge'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='hide_in_renewal_items',
            field=models.BooleanField(default=False, verbose_name="Ne pas afficher dans la liste d'items des avis", editable=False),
        ),
        migrations.AlterField(
            model_name='renewalnotice',
            name='has_basket',
            field=models.BooleanField(default=False, verbose_name='Avec panier', editable=False),
        ),
    ]
