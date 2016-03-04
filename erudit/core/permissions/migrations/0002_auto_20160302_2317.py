# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('auth', '0006_require_contenttypes_0002'),
        ('permissions', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ObjectPermission',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('date_creation', models.DateTimeField(default=django.utils.timezone.now, null=True, verbose_name='Date de création', editable=False)),
                ('date_modification', models.DateTimeField(default=django.utils.timezone.now, null=True, verbose_name='Date de modification', editable=False)),
                ('object_id', models.PositiveIntegerField(null=True, blank=True)),
                ('permission', models.CharField(max_length=100)),
                ('content_type', models.ForeignKey(null=True, verbose_name='Type', to='contenttypes.ContentType', blank=True)),
                ('group', models.ForeignKey(null=True, to='auth.Group', blank=True)),
                ('user', models.ForeignKey(null=True, to=settings.AUTH_USER_MODEL, blank=True)),
            ],
            options={
                'verbose_name': 'Règle',
            },
        ),
        migrations.RemoveField(
            model_name='rule',
            name='content_type',
        ),
        migrations.RemoveField(
            model_name='rule',
            name='group',
        ),
        migrations.RemoveField(
            model_name='rule',
            name='user',
        ),
        migrations.DeleteModel(
            name='Rule',
        ),
    ]
