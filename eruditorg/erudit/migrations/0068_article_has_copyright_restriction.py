# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-04-13 20:03
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('erudit', '0067_auto_20170413_1351'),
    ]

    operations = [
        migrations.AddField(
            model_name='article',
            name='has_copyright_restriction',
            field=models.BooleanField(default=False, help_text="Cocher si le titulaire du droit d'auteur n'autorise pas la diffusion de cet article sur la plateforme.", verbose_name="Diffusion restreinte par le titulaire du droit d'auteur"),
        ),
    ]