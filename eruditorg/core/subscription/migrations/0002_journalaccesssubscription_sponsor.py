# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("erudit", "0001_initial"),
        ("subscription", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="journalaccesssubscription",
            name="sponsor",
            field=models.ForeignKey(
                on_delete=models.deletion.CASCADE,
                to="erudit.Organisation",
                null=True,
                verbose_name="Commanditaire",
                related_name="sponsored_subscriptions",
                blank=True,
            ),
        ),
    ]
