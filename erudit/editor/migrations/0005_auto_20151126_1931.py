# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('editor', '0004_auto_20151120_2000'),
    ]

    operations = [
        migrations.AlterField(
            model_name='issuesubmission',
            name='date_created',
            field=models.DateField(auto_now_add=True, verbose_name="Date de l'envoi"),
        ),
    ]
