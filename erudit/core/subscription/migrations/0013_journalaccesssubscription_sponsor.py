# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('erudit', '0012_auto_20160322_1257'),
        ('subscription', '0012_auto_20160322_1536'),
    ]

    operations = [
        migrations.AddField(
            model_name='journalaccesssubscription',
            name='sponsor',
            field=models.ForeignKey(to='erudit.Organisation', null=True, blank=True, verbose_name='Commanditaire', related_name='sponsored_subscriptions'),
        ),
    ]
