# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('individual_subscription', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='organizationpolicy',
            name='access_basket',
            field=models.ManyToManyField(to='subscription.Basket', verbose_name='Paniers'),
        ),
        migrations.AlterField(
            model_name='organizationpolicy',
            name='comment',
            field=models.TextField(blank=True, verbose_name='Commentaire'),
        ),
    ]
