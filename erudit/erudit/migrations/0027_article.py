# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import erudit.fedora.modelmixins


class Migration(migrations.Migration):

    dependencies = [
        ('erudit', '0026_issue_title'),
    ]

    operations = [
        migrations.CreateModel(
            name='Article',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('synced_with_edinum', models.BooleanField(default=False, verbose_name='Synchronisé avec Edinum')),
                ('edinum_id', models.CharField(blank=True, max_length=7, null=True, verbose_name='Identifiant Edinum')),
                ('sync_date', models.DateField(blank=True, null=True)),
                ('title', models.CharField(blank=True, max_length=500, null=True)),
                ('localidentifier', models.CharField(blank=True, max_length=50, null=True, verbose_name='Identifiant Fedora')),
                ('processing', models.CharField(choices=[('C', 'Complet'), ('M', 'Minimal')], max_length=1)),
                ('issue', models.ForeignKey(related_name='issues', verbose_name='Numéro', to='erudit.Issue')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model, erudit.fedora.modelmixins.FedoraMixin),
        ),
    ]
