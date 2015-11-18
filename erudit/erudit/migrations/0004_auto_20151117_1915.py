# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('erudit', '0003_auto_20151111_2042'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='library',
            options={'verbose_name': 'Bibliothèque', 'verbose_name_plural': 'Bibliothèques'},
        ),
    ]
