# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('erudit', '0006_create_eruditdocument_data'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='article',
            name='id',
        ),
        migrations.RemoveField(
            model_name='article',
            name='localidentifier',
        ),
        migrations.AlterField(
            model_name='article',
            name='eruditdocument_ptr',
            field=models.OneToOneField(auto_created=True, primary_key=True, to='erudit.EruditDocument', serialize=False, parent_link=True),
        ),
    ]
