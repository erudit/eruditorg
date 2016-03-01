# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('editor', '0011_auto_20160226_1404'),
    ]

    operations = [
        migrations.AlterField(
            model_name='issuesubmission',
            name='date_created',
            field=models.DateTimeField(verbose_name="Date de l'envoi"),
        ),
    ]
