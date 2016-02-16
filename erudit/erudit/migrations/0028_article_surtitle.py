# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('erudit', '0027_article'),
    ]

    operations = [
        migrations.AddField(
            model_name='article',
            name='surtitle',
            field=models.CharField(max_length=500, null=True, blank=True),
        ),
    ]
