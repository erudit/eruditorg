# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('erudit', '0015_journal_localidentifier'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='publisher',
            name='members',
        ),
        migrations.AddField(
            model_name='journal',
            name='members',
            field=models.ManyToManyField(related_name='journals', to=settings.AUTH_USER_MODEL),
        ),
    ]
