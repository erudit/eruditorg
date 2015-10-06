# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('subscription', '0011_auto_20151006_1630'),
    ]

    operations = [
        migrations.DeleteModel(
            name='RenewalNoticeStatus',
        ),
        migrations.AddField(
            model_name='renewalnotice',
            name='error_msg',
            field=models.TextField(help_text='Renseigné automatiquement par système si existe erreur(s).', editable=False, verbose_name="Messages d'erreur", default=''),
        ),
        migrations.AddField(
            model_name='renewalnotice',
            name='no_error',
            field=models.BooleanField(help_text='Renseigné automatiquement par système.', editable=False, verbose_name='Sans erreur', default=True),
        ),
    ]
