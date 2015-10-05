# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('post_office', '0003_auto_20151002_2112'),
        ('subscription', '0004_auto_20151005_0226'),
    ]

    operations = [
        migrations.AddField(
            model_name='renewalnotice',
            name='sent_emails',
            field=models.ManyToManyField(blank=True, verbose_name='Courriels envoyés', to='post_office.Email'),
        ),
    ]
