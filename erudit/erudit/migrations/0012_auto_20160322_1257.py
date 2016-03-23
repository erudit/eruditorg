# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('erudit', '0011_organisation_badge'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='mandragoreprofile',
            name='user',
        ),
        migrations.DeleteModel(
            name='MandragoreProfile',
        ),
    ]
