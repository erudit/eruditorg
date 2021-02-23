# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    def create_journaltypes(apps, schema_editor):
        JournalType = apps.get_model("erudit", "JournalType")
        JournalType(code="C", name="Culturel").save()
        JournalType(code="S", name="Savant").save()

    dependencies = [
        ("erudit", "0001_initial"),
    ]

    operations = [migrations.RunPython(create_journaltypes)]
