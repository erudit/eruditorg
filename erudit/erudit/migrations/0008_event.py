# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('erudit', '0007_auto_20160223_1546'),
    ]

    operations = [
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, verbose_name='ID', serialize=False)),
                ('type', models.PositiveIntegerField(choices=[(1, 'Création de soumission'), (2, 'Changement de statut de soumission')])),
                ('time', models.DateTimeField(auto_now_add=True, verbose_name='Date/Heure')),
                ('target_object_id', models.PositiveIntegerField()),
                ('comment', models.TextField(verbose_name='Commentaire')),
                ('author', models.ForeignKey(to=settings.AUTH_USER_MODEL, verbose_name='Auteur')),
                ('target_content_type', models.ForeignKey(to='contenttypes.ContentType')),
            ],
        ),
    ]
