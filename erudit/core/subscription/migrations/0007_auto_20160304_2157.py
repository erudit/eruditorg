# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('subscription', '0006_auto_20160303_2205'),
    ]

    operations = [
        migrations.CreateModel(
            name='IndividualAccountProfile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, primary_key=True, auto_created=True)),
                ('policy', models.ForeignKey(verbose_name='Accès', related_name='accounts', null=True, blank=True, help_text="Laisser vide si la politique d'accès aux produits est définie plus bas", to='subscription.Policy')),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Compte personnel',
                'verbose_name_plural': 'Comptes personnels',
            },
        ),
        migrations.RemoveField(
            model_name='individualaccount',
            name='policy',
        ),
        migrations.RemoveField(
            model_name='individualaccount',
            name='user_ptr',
        ),
        migrations.DeleteModel(
            name='IndividualAccount',
        ),
    ]
