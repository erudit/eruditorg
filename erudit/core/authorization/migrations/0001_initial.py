# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
        ('contenttypes', '0002_remove_content_type_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Authorization',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('date_creation', models.DateTimeField(verbose_name='Date de création', null=True, editable=False, default=django.utils.timezone.now)),
                ('date_modification', models.DateTimeField(verbose_name='Date de modification', null=True, editable=False, default=django.utils.timezone.now)),
                ('object_id', models.PositiveIntegerField(blank=True, null=True)),
                ('authorization_codename', models.CharField(max_length=100, choices=[('subscriptions:can_manage_account', 'Peut gérer les abonnements individuels'), ('authorization:can_manage_authorizations', 'Peut gérer les autorisation'), ('subscriptions:can_manage_issuesubmission', 'Peut gérer les numéros'), ('subscriptions:can_review_issuesubmission', 'Peut valider les numéros')])),
                ('content_type', models.ForeignKey(verbose_name='Type', blank=True, to='contenttypes.ContentType', null=True)),
                ('group', models.ForeignKey(blank=True, to='auth.Group', null=True)),
                ('user', models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'verbose_name': 'Autorisation',
            },
        ),
    ]
