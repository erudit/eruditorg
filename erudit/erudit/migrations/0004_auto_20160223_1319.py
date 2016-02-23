# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('erudit', '0003_auto_20160219_1716'),
    ]

    operations = [
        migrations.CreateModel(
            name='Author',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('lastname', models.CharField(verbose_name='Nom', max_length=50)),
                ('firstname', models.CharField(blank=True, max_length=50, null=True, verbose_name='Prénom')),
                ('email', models.EmailField(blank=True, max_length=254, null=True, verbose_name='Courriel')),
                ('organisation', models.ForeignKey(blank=True, null=True, verbose_name='Organisation', to='erudit.Organisation')),
            ],
            options={
                'verbose_name': 'Auteur',
                'verbose_name_plural': 'Auteurs',
            },
        ),
        migrations.RemoveField(
            model_name='person',
            name='organisation',
        ),
        migrations.DeleteModel(
            name='Person',
        ),
        migrations.AddField(
            model_name='article',
            name='authors',
            field=models.ManyToManyField(verbose_name='Auteurs', to='erudit.Author'),
        ),
    ]
