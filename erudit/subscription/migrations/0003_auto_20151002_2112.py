# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('subscription', '0002_auto_20150928_1505'),
    ]

    operations = [
        migrations.CreateModel(
            name='RenewalNoticeStatus',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Nom')),
            ],
            options={
                'ordering': ['name'],
                'verbose_name_plural': "États d'avis de renouvellement",
                'verbose_name': "État d'avis de renouvellement",
            },
        ),
        migrations.AddField(
            model_name='renewalnotice',
            name='status',
            field=models.ForeignKey(verbose_name='État', to='subscription.RenewalNoticeStatus', blank=True, null=True, related_name='renewal_notices'),
        ),
    ]
