# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('subscription', '0016_auto_20151007_0334'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='renewalnotice',
            name='no_error',
        ),
        migrations.AddField(
            model_name='renewalnotice',
            name='is_correct',
            field=models.BooleanField(default=True, verbose_name='Est correct?', help_text='Renseigné automatiquement par système.', editable=False),
        ),
    ]
