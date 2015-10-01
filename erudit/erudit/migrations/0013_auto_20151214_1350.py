# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('subscription', '0020_auto_20151028_1743'),
        ('erudit', '0012_merge'),
    ]

    operations = [
        migrations.CreateModel(
            name='Contract',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('date_start', models.DateField(verbose_name='Début', help_text='Date de début du contrat, format aaaa-mm-jj')),
                ('date_end', models.DateField(verbose_name='Fin', help_text='Date de fin du contrat, format aaaa-mm-jj')),
                ('date_signature', models.DateField(null=True, verbose_name='Signé le', help_text='Date de signature du contrat, format aaaa-mm-jj', blank=True)),
            ],
            options={
                'verbose_name_plural': 'Contrats',
                'verbose_name': 'Contrat',
                'ordering': ['journal'],
            },
        ),
        migrations.CreateModel(
            name='ContractStatus',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('name', models.CharField(verbose_name='Nom', max_length=255)),
            ],
            options={
                'verbose_name_plural': 'Statuts de contrat',
                'verbose_name': 'Statut de contrat',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='ContractType',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('code', models.CharField(verbose_name='Code', help_text='Court identifiant utilisé dans le nom automatique des contrats', max_length=255)),
                ('name', models.CharField(verbose_name='Nom', max_length=255)),
            ],
            options={
                'verbose_name_plural': 'Types de contrat',
                'verbose_name': 'Type de contrat',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Grant',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('amount', models.DecimalField(null=True, verbose_name='Montant', decimal_places=2, max_digits=15, blank=True)),
                ('date_start', models.DateField(null=True, verbose_name='Date de début', blank=True)),
                ('date_end', models.DateField(null=True, verbose_name='Date de fin', blank=True)),
                ('currency', models.ForeignKey(verbose_name='Devise', blank=True, null=True, to='subscription.Currency')),
            ],
            options={
                'verbose_name_plural': 'Subventions',
                'verbose_name': 'Subvention',
                'ordering': ['journal'],
            },
        ),
        migrations.CreateModel(
            name='GrantingAgency',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('code', models.CharField(verbose_name='Code', help_text='Acronyme', max_length=255)),
                ('name', models.CharField(verbose_name='Nom', max_length=255)),
            ],
            options={
                'verbose_name_plural': 'Organismes subventionnaires',
                'verbose_name': 'Organisme subventionnaire',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Indexation',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
            ],
            options={
                'verbose_name_plural': 'Indexations',
                'verbose_name': 'Indexation',
                'ordering': ['journal'],
            },
        ),
        migrations.CreateModel(
            name='Indexer',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('name', models.CharField(verbose_name='Nom', max_length=255)),
            ],
            options={
                'verbose_name_plural': 'Indexeurs',
                'verbose_name': 'Indexeur',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Invoice',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('id_sage', models.IntegerField(null=True, verbose_name='Id facture SAGE', help_text='Identifiant de la facture dans SAGE.', blank=True)),
                ('id_subcontractor', models.IntegerField(null=True, verbose_name='Id facture sous-contractant', help_text='Identifiant de la facture du sous-contractant qui couvre cette facture (ex.: CEN-R).', blank=True)),
                ('date', models.DateField(null=True, blank=True)),
                ('total_invoice_subcontractor', models.DecimalField(verbose_name='Total facture sous-contractant', decimal_places=2, blank=True, null=True, help_text='Total de la facture du sous-contractant (ex.: CEN-R)', max_digits=15)),
                ('total', models.DecimalField(null=True, verbose_name='Total', decimal_places=2, max_digits=15, blank=True)),
                ('status', models.CharField(verbose_name='Statut', max_length=255, choices=[('D', 'Draft'), ('V', 'Valid'), ('S', 'Sent'), ('P', 'Paid')])),
                ('currency', models.ForeignKey(verbose_name='Devise', blank=True, null=True, to='subscription.Currency')),
            ],
            options={
                'verbose_name_plural': 'Factures',
                'verbose_name': 'Facture',
                'ordering': ['journal'],
            },
        ),
        migrations.CreateModel(
            name='JournalProduction',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
            ],
            options={
                'verbose_name_plural': 'Productions de revue',
                'verbose_name': 'Production de revue',
                'ordering': ['journal'],
            },
        ),
        migrations.CreateModel(
            name='ProductionCenter',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('code', models.CharField(verbose_name='Code', max_length=255)),
                ('name', models.CharField(verbose_name='Nom', max_length=255)),
            ],
            options={
                'verbose_name_plural': 'Centres de production',
                'verbose_name': 'Centre de production',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='ProductionType',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('code', models.CharField(verbose_name='Code', max_length=255)),
                ('name', models.CharField(verbose_name='Nom', max_length=255)),
            ],
            options={
                'verbose_name_plural': 'Types de production',
                'verbose_name': 'Type de production',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Quotation',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('description', models.TextField(null=True, blank=True)),
                ('date_start', models.DateField(null=True, blank=True)),
                ('date_end', models.DateField(null=True, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='QuotationItem',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('total', models.DecimalField(null=True, decimal_places=2, max_digits=15, blank=True)),
                ('currency', models.ForeignKey(blank=True, null=True, to='subscription.Currency')),
                ('quotation', models.ForeignKey(to='erudit.Quotation')),
            ],
        ),
        migrations.RemoveField(
            model_name='journalcomment',
            name='author',
        ),
        migrations.RemoveField(
            model_name='journalcomment',
            name='journal',
        ),
        migrations.AlterModelOptions(
            name='issue',
            options={'verbose_name': 'Numéro', 'ordering': ['journal', 'year', 'volume', 'number'], 'verbose_name_plural': 'Numéros'},
        ),
        migrations.AlterModelOptions(
            name='journaltype',
            options={'verbose_name': 'Type de revue', 'ordering': ['name'], 'verbose_name_plural': 'Types de revue'},
        ),
        migrations.AlterModelOptions(
            name='library',
            options={'verbose_name': 'Bibliothèque', 'ordering': ['name'], 'verbose_name_plural': 'Bibliothèques'},
        ),
        migrations.AlterModelOptions(
            name='organisation',
            options={'verbose_name': 'Organisation', 'ordering': ['name'], 'verbose_name_plural': 'Organisations'},
        ),
        migrations.AlterModelOptions(
            name='person',
            options={'verbose_name': 'Personne', 'ordering': ['lastname'], 'verbose_name_plural': 'Personnes'},
        ),
        migrations.RemoveField(
            model_name='journal',
            name='series_id',
        ),
        migrations.AlterField(
            model_name='issue',
            name='date_produced',
            field=models.DateField(null=True, verbose_name='Date de production', blank=True),
        ),
        migrations.AlterField(
            model_name='issue',
            name='date_published',
            field=models.DateField(null=True, verbose_name='Date de publication', blank=True),
        ),
        migrations.AlterField(
            model_name='issue',
            name='journal',
            field=models.ForeignKey(verbose_name='Revue', related_name='issues', to='erudit.Journal'),
        ),
        migrations.AlterField(
            model_name='issue',
            name='number',
            field=models.CharField(null=True, verbose_name='Numéro', max_length=255, blank=True),
        ),
        migrations.AlterField(
            model_name='issue',
            name='open_access',
            field=models.NullBooleanField(verbose_name='Accès libre', help_text='Cocher si ce numéro est en accès libre', default=None),
        ),
        migrations.AlterField(
            model_name='issue',
            name='special_issue',
            field=models.BooleanField(verbose_name='Numéro spécial', help_text="Cocher s'il s'agit d'un numéro spécial.", default=False),
        ),
        migrations.AlterField(
            model_name='issue',
            name='volume',
            field=models.CharField(null=True, verbose_name='Volume', max_length=255, blank=True),
        ),
        migrations.AlterField(
            model_name='issue',
            name='year',
            field=models.IntegerField(null=True, verbose_name='Année', blank=True, choices=[(1900, 1900), (1901, 1901), (1902, 1902), (1903, 1903), (1904, 1904), (1905, 1905), (1906, 1906), (1907, 1907), (1908, 1908), (1909, 1909), (1910, 1910), (1911, 1911), (1912, 1912), (1913, 1913), (1914, 1914), (1915, 1915), (1916, 1916), (1917, 1917), (1918, 1918), (1919, 1919), (1920, 1920), (1921, 1921), (1922, 1922), (1923, 1923), (1924, 1924), (1925, 1925), (1926, 1926), (1927, 1927), (1928, 1928), (1929, 1929), (1930, 1930), (1931, 1931), (1932, 1932), (1933, 1933), (1934, 1934), (1935, 1935), (1936, 1936), (1937, 1937), (1938, 1938), (1939, 1939), (1940, 1940), (1941, 1941), (1942, 1942), (1943, 1943), (1944, 1944), (1945, 1945), (1946, 1946), (1947, 1947), (1948, 1948), (1949, 1949), (1950, 1950), (1951, 1951), (1952, 1952), (1953, 1953), (1954, 1954), (1955, 1955), (1956, 1956), (1957, 1957), (1958, 1958), (1959, 1959), (1960, 1960), (1961, 1961), (1962, 1962), (1963, 1963), (1964, 1964), (1965, 1965), (1966, 1966), (1967, 1967), (1968, 1968), (1969, 1969), (1970, 1970), (1971, 1971), (1972, 1972), (1973, 1973), (1974, 1974), (1975, 1975), (1976, 1976), (1977, 1977), (1978, 1978), (1979, 1979), (1980, 1980), (1981, 1981), (1982, 1982), (1983, 1983), (1984, 1984), (1985, 1985), (1986, 1986), (1987, 1987), (1988, 1988), (1989, 1989), (1990, 1990), (1991, 1991), (1992, 1992), (1993, 1993), (1994, 1994), (1995, 1995), (1996, 1996), (1997, 1997), (1998, 1998), (1999, 1999), (2000, 2000), (2001, 2001), (2002, 2002), (2003, 2003), (2004, 2004), (2005, 2005), (2006, 2006), (2007, 2007), (2008, 2008), (2009, 2009), (2010, 2010), (2011, 2011), (2012, 2012), (2013, 2013), (2014, 2014), (2015, 2015), (2016, 2016), (2017, 2017), (2018, 2018), (2019, 2019), (2020, 2020)]),
        ),
        migrations.AlterField(
            model_name='journal',
            name='code',
            field=models.CharField(verbose_name='Code', help_text='Identifiant unique (utilisé dans URL Érudit)', max_length=255),
        ),
        migrations.AlterField(
            model_name='journal',
            name='open_access',
            field=models.NullBooleanField(verbose_name='Libre accès', help_text='Cette revue est en accès libre?', default=None),
        ),
        migrations.AlterField(
            model_name='journal',
            name='paper',
            field=models.NullBooleanField(verbose_name='Papier', help_text='Est publiée également en version papier?', default=None),
        ),
        migrations.AlterField(
            model_name='journaltype',
            name='name',
            field=models.CharField(verbose_name='Nom', max_length=255),
        ),
        migrations.AlterField(
            model_name='library',
            name='name',
            field=models.CharField(verbose_name='Nom', max_length=255),
        ),
        migrations.AlterField(
            model_name='organisation',
            name='city',
            field=models.CharField(null=True, verbose_name='Ville', max_length=50, blank=True),
        ),
        migrations.AlterField(
            model_name='organisation',
            name='country',
            field=models.CharField(null=True, verbose_name='Pays', max_length=50, blank=True),
        ),
        migrations.AlterField(
            model_name='organisation',
            name='postal_code',
            field=models.CharField(null=True, verbose_name='Code postal', max_length=50, blank=True),
        ),
        migrations.AlterField(
            model_name='organisation',
            name='province',
            field=models.CharField(null=True, verbose_name='Province', max_length=50, blank=True),
        ),
        migrations.AlterField(
            model_name='organisation',
            name='street',
            field=models.CharField(null=True, verbose_name='Adresse', max_length=200, blank=True),
        ),
        migrations.AlterField(
            model_name='person',
            name='email',
            field=models.EmailField(null=True, verbose_name='Courriel', max_length=254, blank=True),
        ),
        migrations.AlterField(
            model_name='person',
            name='firstname',
            field=models.CharField(null=True, verbose_name='Prénom', max_length=50, blank=True),
        ),
        migrations.AlterField(
            model_name='person',
            name='organisation',
            field=models.ForeignKey(verbose_name='Organisation', blank=True, null=True, to='erudit.Organisation'),
        ),
        migrations.AlterField(
            model_name='publisher',
            name='name',
            field=models.CharField(verbose_name='Nom', max_length=255),
        ),
        migrations.DeleteModel(
            name='JournalComment',
        ),
        migrations.AddField(
            model_name='quotation',
            name='journal',
            field=models.ForeignKey(blank=True, null=True, to='erudit.Journal'),
        ),
        migrations.AddField(
            model_name='journalproduction',
            name='journal',
            field=models.ForeignKey(verbose_name='Revue', related_name='production', to='erudit.Journal'),
        ),
        migrations.AddField(
            model_name='journalproduction',
            name='production_center',
            field=models.ForeignKey(verbose_name='Centre de production', blank=True, null=True, to='erudit.ProductionCenter', help_text='Centre de production responsable\n            de la production de la revue.'),
        ),
        migrations.AddField(
            model_name='journalproduction',
            name='production_type',
            field=models.ForeignKey(verbose_name='Type de production', blank=True, null=True, to='erudit.ProductionType'),
        ),
        migrations.AddField(
            model_name='invoice',
            name='journal',
            field=models.ForeignKey(verbose_name='Revue', blank=True, null=True, to='erudit.Journal', help_text='Revue facturée'),
        ),
        migrations.AddField(
            model_name='indexation',
            name='indexer',
            field=models.ForeignKey(verbose_name='Indexeur', to='erudit.Indexer'),
        ),
        migrations.AddField(
            model_name='indexation',
            name='journal',
            field=models.ForeignKey(verbose_name='Revue', to='erudit.Journal'),
        ),
        migrations.AddField(
            model_name='grant',
            name='granting_agency',
            field=models.ForeignKey(verbose_name='Organisme subventionnaire', to='erudit.GrantingAgency'),
        ),
        migrations.AddField(
            model_name='grant',
            name='journal',
            field=models.ForeignKey(verbose_name='Revue', to='erudit.Journal', related_name='grants', help_text='Revue ayant obtenu cette subvention'),
        ),
        migrations.AddField(
            model_name='contract',
            name='journal',
            field=models.ForeignKey(verbose_name='Revue', related_name='contracts', to='erudit.Journal'),
        ),
        migrations.AddField(
            model_name='contract',
            name='status',
            field=models.ForeignKey(verbose_name='État', blank=True, null=True, related_name='contracts', to='erudit.ContractStatus'),
        ),
        migrations.AddField(
            model_name='contract',
            name='type',
            field=models.ForeignKey(verbose_name='Type', related_name='contracts', to='erudit.ContractType'),
        ),
    ]
