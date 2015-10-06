# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('subscription', '0013_auto_20151006_1749'),
    ]

    operations = [
        migrations.CreateModel(
            name='Country',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('code', models.CharField(blank=True, max_length=255, null=True)),
                ('name', models.CharField(max_length=255, verbose_name='Nom')),
            ],
            options={
                'verbose_name_plural': 'Pays',
                'verbose_name': 'Pays',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Currency',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('code', models.CharField(max_length=255)),
                ('name', models.CharField(max_length=255, verbose_name='Nom')),
            ],
            options={
                'verbose_name_plural': 'Devises',
                'verbose_name': 'Devise',
                'ordering': ['code'],
            },
        ),
        migrations.AddField(
            model_name='country',
            name='currency',
            field=models.ForeignKey(to='subscription.Currency', verbose_name='Devise', blank=True, related_name='pays', null=True),
        ),
    ]
