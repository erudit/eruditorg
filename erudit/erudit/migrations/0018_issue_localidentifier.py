# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('erudit', '0017_auto_20160129_1725'),
    ]

    operations = [
        migrations.AddField(
            model_name='issue',
            name='localidentifier',
            field=models.CharField(blank=True, null=True, verbose_name='Identifiant Fedora', max_length=50),
        ),
    ]
