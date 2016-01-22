# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('erudit', '0014_auto_20160106_1527'),
        ('individual_subscription', '0014_auto_20160112_0134'),
    ]

    operations = [
        migrations.CreateModel(
            name='Journal',
            fields=[
            ],
            options={
                'proxy': True,
                'verbose_name': 'Revue',
            },
            bases=('erudit.journal',),
        ),
        migrations.CreateModel(
            name='Organisation',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('erudit.organisation',),
        ),
        migrations.AddField(
            model_name='individualaccount',
            name='active',
            field=models.BooleanField(verbose_name='Actif', default=True),
        ),
        migrations.AlterField(
            model_name='policy',
            name='content_type',
            field=models.ForeignKey(verbose_name='Type', to='contenttypes.ContentType'),
        ),
    ]
