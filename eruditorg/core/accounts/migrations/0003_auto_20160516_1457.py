# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0002_restrictionprofile"),
    ]

    operations = [
        migrations.AlterField(
            model_name="restrictionprofile",
            name="password",
            field=models.CharField(
                null=True, max_length=50, blank=True, verbose_name="Mot de passe"
            ),
        ),
    ]
