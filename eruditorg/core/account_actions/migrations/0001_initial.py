# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='AccountActionToken',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('created', models.DateTimeField(verbose_name='Date de création', auto_now_add=True)),
                ('updated', models.DateTimeField(verbose_name='Date de modification', auto_now=True)),
                ('key', models.CharField(max_length=40, unique=True)),
                ('first_name', models.CharField(max_length=30, null=True, verbose_name='Prénom', blank=True)),
                ('last_name', models.CharField(max_length=30, null=True, verbose_name='Nom', blank=True)),
                ('email', models.EmailField(max_length=254, verbose_name='Adresse e-mail')),
                ('action', models.CharField(max_length=100, verbose_name='Action')),
                ('object_id', models.PositiveIntegerField(null=True, blank=True)),
                ('content_type', models.ForeignKey(verbose_name='Type', blank=True, null=True, to='contenttypes.ContentType')),
                ('user', models.ForeignKey(verbose_name='Utilisateur', blank=True, null=True, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': "Jeton d'action",
                'verbose_name_plural': "Jetons d'actions",
            },
        ),
    ]
