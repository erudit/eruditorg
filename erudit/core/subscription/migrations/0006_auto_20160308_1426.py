# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('subscription', '0005_merge'),
    ]

    operations = [
        migrations.CreateModel(
            name='IndividualAccountProfile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, serialize=False, auto_created=True)),
                ('password', models.CharField(verbose_name='Mot de passe', blank=True, max_length=50)),
                ('policy', models.ForeignKey(to='subscription.Policy', help_text="Laisser vide si la politique d'accès aux produits est définie plus bas", verbose_name='Accès', null=True, related_name='accounts', blank=True)),
                ('user', models.OneToOneField(verbose_name='Utilisateur', to=settings.AUTH_USER_MODEL)),
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
        migrations.DeleteModel(
            name='IndividualAccount',
        ),
    ]
