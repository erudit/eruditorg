# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("editor", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="issuesubmissionstatustrack",
            name="comment",
            field=models.TextField(null=True, verbose_name="Commentaire", blank=True),
        ),
    ]
