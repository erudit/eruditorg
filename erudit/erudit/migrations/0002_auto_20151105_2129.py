# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('erudit', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='journalsubmission',
            name='date_created',
            field=models.DateField(),
        ),
    ]
