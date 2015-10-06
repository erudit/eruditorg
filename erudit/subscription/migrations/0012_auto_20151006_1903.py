# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('subscription', '0011_auto_20151006_1857'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='hide_in_renewal_items',
            field=models.BooleanField(default=False, verbose_name="Ne pas afficher dans la liste d'items des avis"),
        ),
    ]
