# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-04-13 18:51
from __future__ import unicode_literals

from django.db import migrations
import taggit.managers


class Migration(migrations.Migration):

    dependencies = [
        ('erudit', '0066_issue_force_free_access'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='article',
            name='html_title',
        ),
        migrations.AlterField(
            model_name='eruditdocument',
            name='keywords',
            field=taggit.managers.TaggableManager(blank=True, help_text='A comma-separated list of tags.', through='erudit.KeywordTaggedWhatever', to='erudit.KeywordTag', verbose_name='Tags'),
        ),
    ]