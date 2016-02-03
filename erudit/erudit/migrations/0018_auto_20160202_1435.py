# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('erudit', '0017_auto_20160129_1725'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='journal',
            name='publisher',
        ),
        migrations.AddField(
            model_name='journal',
            name='publishers',
            field=models.ManyToManyField(to='erudit.Publisher', related_name='journals', verbose_name='Éditeur'),
        ),
    ]
