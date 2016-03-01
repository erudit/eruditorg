# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('editor', '0012_auto_20160226_1414'),
    ]

    operations = [
        migrations.AlterField(
            model_name='issuesubmission',
            name='date_created',
            field=models.DateTimeField(null=True, editable=False, verbose_name="Date de l'envoi"),
        ),
        migrations.AlterField(
            model_name='issuesubmission',
            name='date_modified',
            field=models.DateTimeField(null=True, editable=False, verbose_name='Date de modification'),
        ),
    ]
