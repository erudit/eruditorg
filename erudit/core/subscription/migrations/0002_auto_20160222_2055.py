# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('subscription', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='individualaccount',
            name='policy',
            field=models.ForeignKey(verbose_name='Accès', help_text="Laisser vide si la politique d'accès est définie plus bas", to='subscription.Policy', blank=True, related_name='accounts', null=True),
        ),
    ]
