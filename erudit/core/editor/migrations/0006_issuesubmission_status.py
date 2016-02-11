# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('editor', '0005_auto_20151126_1931'),
    ]

    operations = [
        migrations.AddField(
            model_name='issuesubmission',
            name='status',
            field=models.CharField(choices=[('D', 'Brouillon'), ('S', 'Soumis'), ('V', 'Validé')], default='D', max_length=1),
        ),
    ]
