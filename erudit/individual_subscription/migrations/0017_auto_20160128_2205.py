# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('individual_subscription', '0016_policyevent'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='policyevent',
            options={'ordering': ('-date_creation',), 'verbose_name_plural': 'Évènements sur les accès', 'verbose_name': 'Évènement sur les accès'},
        ),
        migrations.AddField(
            model_name='policy',
            name='generated_title',
            field=models.CharField(blank=True, verbose_name='Titre', max_length=120, editable=False),
        ),
        migrations.AlterField(
            model_name='policy',
            name='date_activation',
            field=models.DateTimeField(blank=True, help_text="Ce champs se remplit automatiquement.             Il est éditable uniquement pour les données existantes qui n'ont pas cette information", null=True, verbose_name="Date d'activation"),
        ),
    ]
