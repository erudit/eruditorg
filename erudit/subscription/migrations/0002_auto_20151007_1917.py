# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('subscription', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='renewalnotice',
            name='no_error',
        ),
        migrations.AddField(
            model_name='renewalnotice',
            name='is_correct',
            field=models.BooleanField(help_text='Renseigné automatiquement par système.', default=True, verbose_name='Est correct?', editable=False),
        ),
        migrations.AlterField(
            model_name='client',
            name='currency',
            field=models.CharField(null=True, blank=True, verbose_name='Devise', max_length=3),
        ),
        migrations.AlterField(
            model_name='client',
            name='exemption_code',
            field=models.CharField(null=True, blank=True, verbose_name="Code d'exemption", max_length=1),
        ),
        migrations.AlterField(
            model_name='client',
            name='pobox',
            field=models.CharField(null=True, blank=True, verbose_name='Casier postal', max_length=100),
        ),
        migrations.AlterField(
            model_name='client',
            name='province',
            field=models.CharField(null=True, blank=True, verbose_name='Province', max_length=100),
        ),
    ]
