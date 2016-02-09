# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('journal', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='journalinformation',
            name='about',
            field=models.TextField(null=True, verbose_name='Revue', blank=True),
        ),
        migrations.AlterField(
            model_name='journalinformation',
            name='about_en',
            field=models.TextField(null=True, verbose_name='Revue', blank=True),
        ),
        migrations.AlterField(
            model_name='journalinformation',
            name='about_fr_ca',
            field=models.TextField(null=True, verbose_name='Revue', blank=True),
        ),
        migrations.AlterField(
            model_name='journalinformation',
            name='journal',
            field=models.OneToOneField(related_name='information', verbose_name='Journal', to='erudit.Journal'),
        ),
    ]
