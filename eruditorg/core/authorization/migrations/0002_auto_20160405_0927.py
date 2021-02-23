# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("authorization", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="authorization",
            name="authorization_codename",
            field=models.CharField(
                max_length=100,
                choices=[
                    ("authorization:can_manage_authorizations", "Autorisations"),
                    ("subscriptions:can_manage_individual_subscription", "Abonnements"),
                    ("editor:can_manage_issuesubmission", "Dépôt de fichiers"),
                ],
            ),
        ),
    ]
