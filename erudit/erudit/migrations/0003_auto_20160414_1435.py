# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('erudit', '0002_auto_20160414_1412'),
    ]

    operations = [
        migrations.AddField(
            model_name='article',
            name='fedora_created',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Date de création sur Fedora'),
        ),
        migrations.AddField(
            model_name='article',
            name='fedora_updated',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Date de modification sur Fedora'),
        ),
        migrations.AddField(
            model_name='issue',
            name='fedora_created',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Date de création sur Fedora'),
        ),
        migrations.AddField(
            model_name='issue',
            name='fedora_updated',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Date de modification sur Fedora'),
        ),
        migrations.AddField(
            model_name='journal',
            name='fedora_created',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Date de création sur Fedora'),
        ),
        migrations.AddField(
            model_name='journal',
            name='fedora_updated',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Date de modification sur Fedora'),
        ),
    ]
