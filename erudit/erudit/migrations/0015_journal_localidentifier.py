# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('erudit', '0014_auto_20160106_1527'),
    ]

    operations = [
        migrations.AddField(
            model_name='journal',
            name='localidentifier',
            field=models.CharField(max_length=50, blank=True, verbose_name='Identifiant Fedora', null=True),
        ),
    ]
