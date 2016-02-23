# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('erudit', '0004_eruditdocument'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='article',
            options={'verbose_name_plural': 'Articles', 'verbose_name': 'Article'},
        ),
        migrations.AddField(
            model_name='article',
            name='eruditdocument_ptr',
            field=models.IntegerField(null=True),
        ),
    ]
