# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('subscription', '0003_auto_20151002_1534'),
    ]

    operations = [
        migrations.AlterField(
            model_name='client',
            name='city',
            field=models.CharField(verbose_name='Ville', max_length=100),
        ),
        migrations.AlterField(
            model_name='client',
            name='country',
            field=models.CharField(verbose_name='Pays', max_length=100),
        ),
        migrations.AlterField(
            model_name='client',
            name='firstname',
            field=models.CharField(verbose_name='Prénom', max_length=100),
        ),
        migrations.AlterField(
            model_name='client',
            name='lastname',
            field=models.CharField(verbose_name='Nom', max_length=100),
        ),
        migrations.AlterField(
            model_name='client',
            name='pobox',
            field=models.CharField(verbose_name='Casier postal', max_length=100),
        ),
        migrations.AlterField(
            model_name='client',
            name='province',
            field=models.CharField(verbose_name='Province', max_length=100),
        ),
        migrations.AlterField(
            model_name='renewalnotice',
            name='renewal_number',
            field=models.CharField(verbose_name="Numéro d'avis", max_length=20),
        ),
    ]
