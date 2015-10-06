# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('subscription', '0009_renewalnotice_has_basket'),
    ]

    operations = [
        migrations.AddField(
            model_name='renewalnotice',
            name='has_rebate',
            field=models.BooleanField(default=False, verbose_name='Avec rabais'),
        ),
        migrations.AlterField(
            model_name='renewalnotice',
            name='has_basket',
            field=models.BooleanField(default=False, verbose_name='Avec panier', editable=False),
        ),
        migrations.AlterField(
            model_name='renewalnotice',
            name='status',
            field=models.ForeignKey(to='subscription.RenewalNoticeStatus', blank=True, related_name='renewal_notices', null=True, verbose_name='État'),
        ),
    ]
