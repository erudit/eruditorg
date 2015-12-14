# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('erudit', '0010_auto_20151130_2043'),
    ]

    operations = [
        migrations.CreateModel(
            name='MandragoreProfile',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('synced_with_mandragore', models.BooleanField(default=False, verbose_name='Synchronisé avec Mandragore')),
                ('mandragore_id', models.CharField(verbose_name='Identifiant Mandragore', blank=True, max_length=7, null=True)),
                ('sync_date', models.DateField(blank=True, null=True)),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
