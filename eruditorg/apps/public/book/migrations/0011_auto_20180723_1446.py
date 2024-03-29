# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2018-07-23 19:46
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("book", "0010_book_copyright"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="book",
            options={"verbose_name": "Livre", "verbose_name_plural": "Livres"},
        ),
        migrations.AlterModelOptions(
            name="bookcollection",
            options={
                "verbose_name": "Collection d’actes ou de livres",
                "verbose_name_plural": "Collections d’actes ou de livres",
            },
        ),
        migrations.RenameField(
            model_name="bookcollection",
            old_name="collection_name",
            new_name="name",
        ),
        migrations.AlterField(
            model_name="book",
            name="digital_isbn",
            field=models.CharField(
                blank=True, max_length=20, null=True, verbose_name="ISBN numérique"
            ),
        ),
        migrations.AlterField(
            model_name="book",
            name="isbn",
            field=models.CharField(blank=True, max_length=20, null=True, verbose_name="ISBN"),
        ),
    ]
