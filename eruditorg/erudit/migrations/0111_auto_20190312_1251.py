# Generated by Django 2.0.10 on 2019-03-12 17:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("erudit", "0110_auto_20181123_1558"),
    ]

    operations = [
        migrations.AlterField(
            model_name="issue",
            name="is_published",
            field=models.BooleanField(default=False, verbose_name="Est publié"),
        ),
    ]
