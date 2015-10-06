# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('subscription', '0010_auto_20151006_1531'),
    ]

    operations = [
        migrations.AlterField(
            model_name='renewalnotice',
            name='status',
            field=models.CharField(choices=[('DONT', 'Ne pas envoyer'), ('TODO', 'À envoyer'), ('SENT', 'Envoyé'), ('REDO', 'À ré-envoyer')], default='DONT', verbose_name='État', max_length=4),
        ),
    ]
