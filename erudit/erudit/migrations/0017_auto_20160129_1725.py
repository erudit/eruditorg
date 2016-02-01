# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('erudit', '0016_auto_20160126_2028'),
    ]

    operations = [
        migrations.AlterField(
            model_name='journal',
            name='code',
            field=models.SlugField(verbose_name='Code', max_length=255, unique=True, help_text='Identifiant unique (utilisé dans URL Érudit)'),
        ),
        migrations.AlterField(
            model_name='journal',
            name='members',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL, related_name='journals', verbose_name='Membres'),
        ),
    ]
