# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('erudit', '0010_auto_20160506_1142'),
    ]

    operations = [
        migrations.AlterField(
            model_name='journal',
            name='collection',
            field=models.ForeignKey(on_delete=models.deletion.CASCADE, to='erudit.Collection', default=1),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='journal',
            name='formerly',
            field=models.ForeignKey(on_delete=models.deletion.CASCADE, verbose_name='Anciennement', to='erudit.Journal', null=True, help_text="Choisir l'ancienne instance de la revue", blank=True),
        ),
        migrations.AlterField(
            model_name='journal',
            name='publishers',
            field=models.ManyToManyField(verbose_name='Éditeurs', to='erudit.Publisher', related_name='journals'),
        ),
    ]
