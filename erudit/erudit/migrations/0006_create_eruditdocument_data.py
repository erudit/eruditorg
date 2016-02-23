# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models

def link_article_to_eruditdocument(apps, schema_editor):
    Article = apps.get_model("erudit", "Article")
    EruditDocument = apps.get_model("erudit", "EruditDocument")

    for article in Article.objects.all():
        erudit_document = EruditDocument(localidentifier=article.localidentifier)
        erudit_document.save()

        article.eruditdocument_ptr = erudit_document.pk
        article.save()

class Migration(migrations.Migration):

    dependencies = [
        ('erudit', '0005_auto_20160223_1528'),
    ]

    operations = [
        migrations.RunPython(link_article_to_eruditdocument),
    ]
