# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('subscription', '0017_auto_20151009_1532'),
    ]

    operations = [
        migrations.AddField(
            model_name='renewalnotice',
            name='has_been_answered',
            field=models.BooleanField(default=False, verbose_name='A répondu'),
        ),
        migrations.AlterField(
            model_name='renewalnotice',
            name='status',
            field=models.CharField(default='DONT', max_length=4, choices=[('DONT', 'Ne pas envoyer'), ('TODO', 'À envoyer'), ('SENT', 'Envoyé'), ('REDO', 'À ré-envoyer'), ('LATE', 'Envoyer plus tard')], verbose_name='État'),
        ),
    ]
