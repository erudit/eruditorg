# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('subscription', '0007_auto_20151005_1558'),
    ]

    operations = [
        migrations.AddField(
            model_name='renewalnotice',
            name='comment',
            field=models.TextField(help_text="Commentaire libre pour suivi de l'avis", null=True, verbose_name='Commentaire', blank=True),
        ),
        migrations.AlterField(
            model_name='client',
            name='firstname',
            field=models.CharField(null=True, max_length=100, verbose_name='Prénom', blank=True),
        ),
    ]
