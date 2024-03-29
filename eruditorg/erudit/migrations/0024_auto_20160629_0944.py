# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-06-29 14:44
from __future__ import unicode_literals

from django.db import migrations


def forwards_func(apps, schema_editor):
    Article = apps.get_model("erudit", "Article")
    Thesis = apps.get_model("erudit", "Thesis")
    ContentType = apps.get_model("contenttypes", "ContentType")

    article_ct = ContentType.objects.get_for_model(Article)
    Article.objects.filter(polymorphic_ctype__isnull=True).update(polymorphic_ctype=article_ct)
    thesis_ct = ContentType.objects.get_for_model(Thesis)
    Thesis.objects.filter(polymorphic_ctype__isnull=True).update(polymorphic_ctype=thesis_ct)


def backwards_func(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("contenttypes", "0001_initial"),
        ("erudit", "0023_eruditdocument_polymorphic_ctype"),
    ]

    operations = [
        migrations.RunPython(forwards_func, backwards_func),
    ]
