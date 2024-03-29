# -*- coding: utf-8 -*-
# Generated by Django 1.9.9 on 2016-10-28 15:36
from __future__ import unicode_literals

from django.db import migrations


def convert_title_property_to_articletitle_object(apps, schema_editor):

    Article = apps.get_model("erudit", "Article")
    ArticleTitle = apps.get_model("erudit", "ArticleTitle")

    for article in Article.objects.all():
        if article.title:
            ArticleTitle(article=article, title=article.title, paral=False).save()


class Migration(migrations.Migration):

    dependencies = [
        ("erudit", "0053_auto_20161028_1034"),
    ]

    operations = [migrations.RunPython(convert_title_property_to_articletitle_object)]
