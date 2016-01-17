# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('individual_subscription', '0015_auto_20160114_0136'),
    ]

    operations = [
        migrations.CreateModel(
            name='PolicyEvent',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('date_creation', models.DateTimeField(default=django.utils.timezone.now, null=True, editable=False, verbose_name='Date de création')),
                ('code', models.CharField(max_length=120, choices=[('LIMIT_REACHED', 'Limite atteinte')], verbose_name='Code')),
                ('message', models.TextField(blank=True, verbose_name='Texte')),
                ('policy', models.ForeignKey(to='individual_subscription.Policy', verbose_name='Accès aux produits')),
            ],
        ),
    ]
