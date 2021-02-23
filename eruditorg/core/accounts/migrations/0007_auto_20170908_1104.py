# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-09-08 16:04
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0006_auto_20160713_0913"),
    ]

    operations = [
        migrations.AlterField(
            model_name="legacyaccountprofile",
            name="origin",
            field=models.PositiveSmallIntegerField(
                choices=[
                    (1, "Base de données Abonnements"),
                    (2, "Base de données Restrictions"),
                    (4, "Base de données Drupal"),
                ],
                verbose_name="Origine",
            ),
        ),
    ]
