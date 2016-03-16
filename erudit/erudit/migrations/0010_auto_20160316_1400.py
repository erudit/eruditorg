# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('erudit', '0009_merge'),
    ]

    operations = [
        migrations.CreateModel(
            name='Discipline',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(verbose_name='Nom', max_length=255)),
                ('name_fr', models.CharField(verbose_name='Nom', null=True, max_length=255)),
                ('name_en', models.CharField(verbose_name='Nom', null=True, max_length=255)),
                ('code', models.CharField(verbose_name='Code', max_length=255, unique=True)),
            ],
            options={
                'verbose_name': 'Discipline',
                'verbose_name_plural': 'Disciplines',
            },
        ),
        migrations.AlterModelOptions(
            name='event',
            options={'verbose_name': 'Événement', 'verbose_name_plural': 'Événements'},
        ),
        migrations.AddField(
            model_name='journal',
            name='disciplines',
            field=models.ManyToManyField(to='erudit.Discipline', related_name='journals'),
        ),
    ]
