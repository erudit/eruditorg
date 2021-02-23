# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("erudit", "0012_auto_20160510_1002"),
    ]

    operations = [
        migrations.AddField(
            model_name="organisation",
            name="members",
            field=models.ManyToManyField(
                to=settings.AUTH_USER_MODEL, related_name="organisations", verbose_name="Membres"
            ),
        ),
    ]
