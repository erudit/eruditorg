# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('journal', '0002_auto_20160209_1529'),
    ]

    operations = [
        migrations.RenameField(
            model_name='journalinformation',
            old_name='about_fr_ca',
            new_name='about_fr',
        ),
        migrations.RenameField(
            model_name='journalinformation',
            old_name='contact_fr_ca',
            new_name='contact_fr',
        ),
        migrations.RenameField(
            model_name='journalinformation',
            old_name='editorial_policy_fr_ca',
            new_name='editorial_policy_fr',
        ),
        migrations.RenameField(
            model_name='journalinformation',
            old_name='partners_fr_ca',
            new_name='partners_fr',
        ),
        migrations.RenameField(
            model_name='journalinformation',
            old_name='subscriptions_fr_ca',
            new_name='subscriptions_fr',
        ),
        migrations.RenameField(
            model_name='journalinformation',
            old_name='team_fr_ca',
            new_name='team_fr',
        ),
    ]
