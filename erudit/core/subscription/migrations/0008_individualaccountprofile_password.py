# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('subscription', '0007_auto_20160304_2157'),
    ]

    operations = [
        migrations.AddField(
            model_name='individualaccountprofile',
            name='password',
            field=models.CharField(max_length=50, blank=True, verbose_name='Mot de passe'),
        ),
    ]
