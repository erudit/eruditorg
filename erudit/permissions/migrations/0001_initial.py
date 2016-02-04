# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contenttypes', '0002_remove_content_type_name'),
        ('auth', '0006_require_contenttypes_0002'),
    ]

    operations = [
        migrations.CreateModel(
            name='Rule',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('date_creation', models.DateTimeField(default=django.utils.timezone.now, null=True, verbose_name='Date de création', editable=False)),
                ('date_modification', models.DateTimeField(default=django.utils.timezone.now, null=True, verbose_name='Date de modification', editable=False)),
                ('object_id', models.PositiveIntegerField(null=True, blank=True)),
                ('permission', models.CharField(max_length=100)),
                ('content_type', models.ForeignKey(verbose_name='Type', blank=True, null=True, to='contenttypes.ContentType')),
                ('group', models.ForeignKey(to='auth.Group', blank=True, null=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, blank=True, null=True)),
            ],
            options={
                'verbose_name': 'Règle',
            },
        ),
    ]
