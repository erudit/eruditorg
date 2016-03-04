# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.contrib.auth.models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('subscription', '0005_merge'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='individualaccount',
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.RemoveField(
            model_name='individualaccount',
            name='active',
        ),
        migrations.RemoveField(
            model_name='individualaccount',
            name='email',
        ),
        migrations.RemoveField(
            model_name='individualaccount',
            name='firstname',
        ),
        migrations.RemoveField(
            model_name='individualaccount',
            name='id',
        ),
        migrations.RemoveField(
            model_name='individualaccount',
            name='lastname',
        ),
        migrations.RemoveField(
            model_name='individualaccount',
            name='password',
        ),
        migrations.AddField(
            model_name='individualaccount',
            name='user_ptr',
            field=models.OneToOneField(default=0, primary_key=True, to=settings.AUTH_USER_MODEL, parent_link=True, auto_created=True, serialize=False),
            preserve_default=False,
        ),
    ]
