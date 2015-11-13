# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Issue',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('year', models.IntegerField(choices=[(1900, 1900), (1901, 1901), (1902, 1902), (1903, 1903), (1904, 1904), (1905, 1905), (1906, 1906), (1907, 1907), (1908, 1908), (1909, 1909), (1910, 1910), (1911, 1911), (1912, 1912), (1913, 1913), (1914, 1914), (1915, 1915), (1916, 1916), (1917, 1917), (1918, 1918), (1919, 1919), (1920, 1920), (1921, 1921), (1922, 1922), (1923, 1923), (1924, 1924), (1925, 1925), (1926, 1926), (1927, 1927), (1928, 1928), (1929, 1929), (1930, 1930), (1931, 1931), (1932, 1932), (1933, 1933), (1934, 1934), (1935, 1935), (1936, 1936), (1937, 1937), (1938, 1938), (1939, 1939), (1940, 1940), (1941, 1941), (1942, 1942), (1943, 1943), (1944, 1944), (1945, 1945), (1946, 1946), (1947, 1947), (1948, 1948), (1949, 1949), (1950, 1950), (1951, 1951), (1952, 1952), (1953, 1953), (1954, 1954), (1955, 1955), (1956, 1956), (1957, 1957), (1958, 1958), (1959, 1959), (1960, 1960), (1961, 1961), (1962, 1962), (1963, 1963), (1964, 1964), (1965, 1965), (1966, 1966), (1967, 1967), (1968, 1968), (1969, 1969), (1970, 1970), (1971, 1971), (1972, 1972), (1973, 1973), (1974, 1974), (1975, 1975), (1976, 1976), (1977, 1977), (1978, 1978), (1979, 1979), (1980, 1980), (1981, 1981), (1982, 1982), (1983, 1983), (1984, 1984), (1985, 1985), (1986, 1986), (1987, 1987), (1988, 1988), (1989, 1989), (1990, 1990), (1991, 1991), (1992, 1992), (1993, 1993), (1994, 1994), (1995, 1995), (1996, 1996), (1997, 1997), (1998, 1998), (1999, 1999), (2000, 2000), (2001, 2001), (2002, 2002), (2003, 2003), (2004, 2004), (2005, 2005), (2006, 2006), (2007, 2007), (2008, 2008), (2009, 2009), (2010, 2010), (2011, 2011), (2012, 2012), (2013, 2013), (2014, 2014), (2015, 2015), (2016, 2016), (2017, 2017), (2018, 2018), (2019, 2019), (2020, 2020)])),
                ('volume', models.CharField(max_length=255)),
                ('number', models.CharField(max_length=255)),
                ('special_issue', models.BooleanField()),
                ('date_produced', models.DateField()),
                ('date_published', models.DateField()),
                ('open_access', models.BooleanField()),
            ],
        ),
        migrations.CreateModel(
            name='Journal',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('date_created', models.DateField(auto_now_add=True, verbose_name='Créé le')),
                ('date_modified', models.DateField(verbose_name='Modifié le', auto_now=True)),
                ('name', models.CharField(help_text='Nom officiel', verbose_name='Nom', max_length=255)),
                ('display_name', models.CharField(help_text='Nom à utiliser dans tout affichage', blank=True, null=True, verbose_name="Nom d'affichage", max_length=255)),
                ('code', models.CharField(help_text='Identifiant unique (utilisé dans URL Érudit)', max_length=255)),
                ('issn_print', models.CharField(blank=True, null=True, verbose_name='ISSN imprimé', max_length=255)),
                ('issn_web', models.CharField(blank=True, null=True, verbose_name='ISSN web', max_length=255)),
                ('paper', models.BooleanField(default=False, verbose_name='Papier', help_text='Est publiée également en version papier?')),
                ('open_access', models.BooleanField(default=True, verbose_name='Open access')),
                ('issues_per_year', models.IntegerField(blank=True, verbose_name='Numéros par année', null=True)),
                ('url', models.URLField(blank=True, null=True, verbose_name='URL')),
                ('address', models.TextField(blank=True, verbose_name='Adresse', null=True)),
                ('active', models.BooleanField(default=True, verbose_name='Actif', help_text="Une revue inactive n'édite plus de numéros")),
                ('formerly', models.ForeignKey(to='erudit.Journal', blank=True, null=True, help_text="Choisir l'ancien nom de la revue", verbose_name='Anciennement')),
            ],
            options={
                'verbose_name_plural': 'Revues',
                'verbose_name': 'Revue',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='JournalComment',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('comment', models.TextField(verbose_name='Commentaire')),
                ('date', models.DateTimeField(verbose_name='Soumis le', auto_now=True)),
                ('author', models.ForeignKey(to=settings.AUTH_USER_MODEL, related_name='+', verbose_name='Soumis par')),
                ('journal', models.ForeignKey(to='erudit.Journal', related_name='comments')),
            ],
            options={
                'verbose_name_plural': 'Commentaires',
                'verbose_name': 'Commentaire',
                'abstract': False,
                'ordering': ['date'],
            },
        ),
        migrations.CreateModel(
            name='JournalSubmission',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('volume', models.CharField(max_length=100)),
                ('date_created', models.DateField(auto_now=True)),
                ('comment', models.TextField()),
                ('submission_file', models.FileField(upload_to='submissions')),
                ('contact', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
                ('journal', models.ForeignKey(to='erudit.Journal')),
            ],
        ),
        migrations.CreateModel(
            name='JournalType',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Library',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Organisation',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(verbose_name='Nom', max_length=120)),
                ('street', models.CharField(verbose_name='Adresse', max_length=200)),
                ('postal_code', models.CharField(verbose_name='Code postal', max_length=50)),
                ('city', models.CharField(verbose_name='Ville', max_length=50)),
                ('province', models.CharField(verbose_name='Province', max_length=50)),
                ('country', models.CharField(verbose_name='Pays', max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Person',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('lastname', models.CharField(verbose_name='Nom', max_length=50)),
                ('firstname', models.CharField(verbose_name='Prénom', max_length=50)),
                ('email', models.EmailField(verbose_name='Courriel', max_length=254)),
                ('organisation', models.ForeignKey(to='erudit.Organisation')),
            ],
        ),
        migrations.CreateModel(
            name='Publisher',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('members', models.ManyToManyField(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='journal',
            name='publisher',
            field=models.ForeignKey(to='erudit.Publisher', blank=True, related_name='journals', verbose_name='Éditeur', null=True),
        ),
        migrations.AddField(
            model_name='journal',
            name='type',
            field=models.ForeignKey(to='erudit.JournalType', blank=True, verbose_name='Type', null=True),
        ),
        migrations.AddField(
            model_name='journal',
            name='user_created',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, related_name='+', verbose_name='Créé par'),
        ),
        migrations.AddField(
            model_name='journal',
            name='user_modified',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, related_name='+', verbose_name='Modifié par'),
        ),
        migrations.AddField(
            model_name='issue',
            name='journal',
            field=models.ForeignKey(to='erudit.Journal', related_name='issues'),
        ),
    ]
