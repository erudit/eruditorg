# Generated by Django 2.0.13 on 2019-10-16 20:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('subscription', '0018_auto_20191016_1329'),
    ]

    operations = [
        migrations.AlterField(
            model_name='institutionipaddressrange',
            name='ip_end_int',
            field=models.BigIntegerField(verbose_name='Adresse IP de fin'),
        ),
        migrations.AlterField(
            model_name='institutionipaddressrange',
            name='ip_start_int',
            field=models.BigIntegerField(verbose_name='Adresse IP de début'),
        ),
    ]