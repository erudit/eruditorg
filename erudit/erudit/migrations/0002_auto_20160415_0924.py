# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('erudit', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='issue',
            field=models.ForeignKey(to='erudit.Issue', related_name='articles', verbose_name='Numéro'),
        ),
    ]
