# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('erudit', '0025_journalinformation'),
    ]

    operations = [
        migrations.AddField(
            model_name='journaltype',
            name='code',
            field=models.SlugField(choices=[('C', 'Culturel'), ('S', 'Savant')], default='S', verbose_name='Code', max_length=2, unique=True),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='journaltype',
            name='name',
            field=models.CharField(verbose_name='Nom', max_length=255, blank=True, null=True),
        ),
    ]
