# Generated by Django 3.0.13 on 2021-03-23 17:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('erudit', '0124_remove_journalinformation_organisation_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='journalinformation',
            name='main_languages',
            field=models.CharField(choices=[('F', 'Français'), ('A', 'Anglais'), ('FA', 'Français / Anglais'), ('AF', 'Anglais / Français')], default='F', max_length=2, verbose_name='Langue(s) principale(s) de publication'),
        ),
        migrations.AddField(
            model_name='journalinformation',
            name='other_languages',
            field=models.ManyToManyField(blank=True, to='erudit.Language', verbose_name='Autre(s) langue(s) de publication'),
        ),
        migrations.AlterField(
            model_name='journalinformation',
            name='languages',
            field=models.ManyToManyField(blank=True, related_name='languages', to='erudit.Language', verbose_name='Langues de publication'),
        ),
    ]