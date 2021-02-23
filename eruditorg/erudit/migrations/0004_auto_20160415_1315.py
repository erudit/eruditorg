# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("erudit", "0003_auto_20160415_0924"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="collection",
            name="edinum_id",
        ),
        migrations.RemoveField(
            model_name="collection",
            name="sync_date",
        ),
        migrations.RemoveField(
            model_name="collection",
            name="synced_with_edinum",
        ),
        migrations.RemoveField(
            model_name="journal",
            name="edinum_id",
        ),
        migrations.RemoveField(
            model_name="journal",
            name="sync_date",
        ),
        migrations.RemoveField(
            model_name="journal",
            name="synced_with_edinum",
        ),
        migrations.RemoveField(
            model_name="publisher",
            name="edinum_id",
        ),
        migrations.RemoveField(
            model_name="publisher",
            name="sync_date",
        ),
        migrations.RemoveField(
            model_name="publisher",
            name="synced_with_edinum",
        ),
        migrations.AddField(
            model_name="article",
            name="fedora_created",
            field=models.DateTimeField(
                verbose_name="Date de création sur Fedora", blank=True, null=True
            ),
        ),
        migrations.AddField(
            model_name="article",
            name="fedora_updated",
            field=models.DateTimeField(
                verbose_name="Date de modification sur Fedora", blank=True, null=True
            ),
        ),
        migrations.AddField(
            model_name="collection",
            name="localidentifier",
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
        migrations.AddField(
            model_name="issue",
            name="fedora_created",
            field=models.DateTimeField(
                verbose_name="Date de création sur Fedora", blank=True, null=True
            ),
        ),
        migrations.AddField(
            model_name="issue",
            name="fedora_updated",
            field=models.DateTimeField(
                verbose_name="Date de modification sur Fedora", blank=True, null=True
            ),
        ),
        migrations.AddField(
            model_name="journal",
            name="fedora_created",
            field=models.DateTimeField(
                verbose_name="Date de création sur Fedora", blank=True, null=True
            ),
        ),
        migrations.AddField(
            model_name="journal",
            name="fedora_updated",
            field=models.DateTimeField(
                verbose_name="Date de modification sur Fedora", blank=True, null=True
            ),
        ),
        migrations.AlterField(
            model_name="collection",
            name="code",
            field=models.CharField(unique=True, default="code", max_length=10),
            preserve_default=False,
        ),
    ]
