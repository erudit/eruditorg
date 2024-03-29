# Generated by Django 2.0.13 on 2019-09-26 19:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("subscription", "0016_auto_20190925_0931"),
    ]

    operations = [
        migrations.AddField(
            model_name="journalaccesssubscription",
            name="is_valid",
            field=models.BooleanField(default=True, verbose_name="Est valide"),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="institutionipaddressrange",
            name="ip_end",
            field=models.GenericIPAddressField(verbose_name="Adresse IP de fin"),
        ),
        migrations.AlterField(
            model_name="institutionipaddressrange",
            name="ip_start",
            field=models.GenericIPAddressField(verbose_name="Adresse IP de début"),
        ),
    ]
