# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings
import erudit.fedora.modelmixins


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Article',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('surtitle', models.CharField(max_length=500, null=True, blank=True)),
                ('title', models.CharField(max_length=500, null=True, blank=True)),
                ('localidentifier', models.CharField(max_length=50, null=True, blank=True, verbose_name='Identifiant Fedora')),
                ('processing', models.CharField(max_length=1, choices=[('C', 'Complet'), ('M', 'Minimal')])),
            ],
            bases=(models.Model, erudit.fedora.modelmixins.FedoraMixin),
        ),
        migrations.CreateModel(
            name='Collection',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('synced_with_edinum', models.BooleanField(default=False, verbose_name='Synchronisé avec Edinum')),
                ('edinum_id', models.CharField(max_length=7, null=True, blank=True, verbose_name='Identifiant Edinum')),
                ('sync_date', models.DateField(null=True, blank=True)),
                ('name', models.CharField(max_length=200)),
                ('code', models.CharField(max_length=10, null=True, blank=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Contract',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_start', models.DateField(help_text='Date de début du contrat, format aaaa-mm-jj', verbose_name='Début')),
                ('date_end', models.DateField(help_text='Date de fin du contrat, format aaaa-mm-jj', verbose_name='Fin')),
                ('date_signature', models.DateField(help_text='Date de signature du contrat, format aaaa-mm-jj', null=True, blank=True, verbose_name='Signé le')),
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
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Nom')),
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
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=255, help_text='Court identifiant utilisé dans le nom automatique des contrats', verbose_name='Code')),
                ('name', models.CharField(max_length=255, verbose_name='Nom')),
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
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, verbose_name='Montant')),
                ('date_start', models.DateField(null=True, blank=True, verbose_name='Date de début')),
                ('date_end', models.DateField(null=True, blank=True, verbose_name='Date de fin')),
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
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=255, help_text='Acronyme', verbose_name='Code')),
                ('name', models.CharField(max_length=255, verbose_name='Nom')),
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
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
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
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Nom')),
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
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('id_sage', models.IntegerField(help_text='Identifiant de la facture dans SAGE.', null=True, blank=True, verbose_name='Id facture SAGE')),
                ('id_subcontractor', models.IntegerField(help_text='Identifiant de la facture du sous-contractant qui couvre cette facture (ex.: CEN-R).', null=True, blank=True, verbose_name='Id facture sous-contractant')),
                ('date', models.DateField(null=True, blank=True)),
                ('total_invoice_subcontractor', models.DecimalField(null=True, blank=True, verbose_name='Total facture sous-contractant', decimal_places=2, help_text='Total de la facture du sous-contractant (ex.: CEN-R)', max_digits=15)),
                ('total', models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, verbose_name='Total')),
                ('status', models.CharField(max_length=255, choices=[('D', 'Draft'), ('V', 'Valid'), ('S', 'Sent'), ('P', 'Paid')], verbose_name='Statut')),
            ],
            options={
                'verbose_name_plural': 'Factures',
                'verbose_name': 'Facture',
                'ordering': ['journal'],
            },
        ),
        migrations.CreateModel(
            name='Issue',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255, null=True, blank=True)),
                ('year', models.IntegerField(null=True, choices=[(1900, 1900), (1901, 1901), (1902, 1902), (1903, 1903), (1904, 1904), (1905, 1905), (1906, 1906), (1907, 1907), (1908, 1908), (1909, 1909), (1910, 1910), (1911, 1911), (1912, 1912), (1913, 1913), (1914, 1914), (1915, 1915), (1916, 1916), (1917, 1917), (1918, 1918), (1919, 1919), (1920, 1920), (1921, 1921), (1922, 1922), (1923, 1923), (1924, 1924), (1925, 1925), (1926, 1926), (1927, 1927), (1928, 1928), (1929, 1929), (1930, 1930), (1931, 1931), (1932, 1932), (1933, 1933), (1934, 1934), (1935, 1935), (1936, 1936), (1937, 1937), (1938, 1938), (1939, 1939), (1940, 1940), (1941, 1941), (1942, 1942), (1943, 1943), (1944, 1944), (1945, 1945), (1946, 1946), (1947, 1947), (1948, 1948), (1949, 1949), (1950, 1950), (1951, 1951), (1952, 1952), (1953, 1953), (1954, 1954), (1955, 1955), (1956, 1956), (1957, 1957), (1958, 1958), (1959, 1959), (1960, 1960), (1961, 1961), (1962, 1962), (1963, 1963), (1964, 1964), (1965, 1965), (1966, 1966), (1967, 1967), (1968, 1968), (1969, 1969), (1970, 1970), (1971, 1971), (1972, 1972), (1973, 1973), (1974, 1974), (1975, 1975), (1976, 1976), (1977, 1977), (1978, 1978), (1979, 1979), (1980, 1980), (1981, 1981), (1982, 1982), (1983, 1983), (1984, 1984), (1985, 1985), (1986, 1986), (1987, 1987), (1988, 1988), (1989, 1989), (1990, 1990), (1991, 1991), (1992, 1992), (1993, 1993), (1994, 1994), (1995, 1995), (1996, 1996), (1997, 1997), (1998, 1998), (1999, 1999), (2000, 2000), (2001, 2001), (2002, 2002), (2003, 2003), (2004, 2004), (2005, 2005), (2006, 2006), (2007, 2007), (2008, 2008), (2009, 2009), (2010, 2010), (2011, 2011), (2012, 2012), (2013, 2013), (2014, 2014), (2015, 2015), (2016, 2016), (2017, 2017), (2018, 2018), (2019, 2019), (2020, 2020), (2021, 2021)], blank=True, verbose_name='Année')),
                ('volume', models.CharField(max_length=255, null=True, blank=True, verbose_name='Volume')),
                ('number', models.CharField(max_length=255, null=True, blank=True, verbose_name='Numéro')),
                ('special_issue', models.BooleanField(default=False, help_text="Cocher s'il s'agit d'un numéro spécial.", verbose_name='Numéro spécial')),
                ('date_produced', models.DateField(null=True, blank=True, verbose_name='Date de production')),
                ('date_published', models.DateField(null=True, blank=True, verbose_name='Date de publication')),
                ('open_access', models.NullBooleanField(default=None, help_text='Cocher si ce numéro est en accès libre', verbose_name='Accès libre')),
                ('localidentifier', models.CharField(max_length=50, null=True, blank=True, verbose_name='Identifiant Fedora')),
            ],
            options={
                'verbose_name_plural': 'Numéros',
                'verbose_name': 'Numéro',
                'ordering': ['journal', 'year', 'volume', 'number'],
            },
            bases=(erudit.fedora.modelmixins.FedoraMixin, models.Model),
        ),
        migrations.CreateModel(
            name='Journal',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('synced_with_edinum', models.BooleanField(default=False, verbose_name='Synchronisé avec Edinum')),
                ('edinum_id', models.CharField(max_length=7, null=True, blank=True, verbose_name='Identifiant Edinum')),
                ('sync_date', models.DateField(null=True, blank=True)),
                ('name', models.CharField(max_length=255, help_text='Nom officiel', verbose_name='Nom')),
                ('display_name', models.CharField(max_length=255, help_text='Nom à utiliser dans tout affichage', null=True, blank=True, verbose_name="Nom d'affichage")),
                ('code', models.SlugField(unique=True, help_text='Identifiant unique (utilisé dans URL Érudit)', verbose_name='Code', max_length=255)),
                ('issn_print', models.CharField(max_length=255, null=True, blank=True, verbose_name='ISSN imprimé')),
                ('issn_web', models.CharField(max_length=255, null=True, blank=True, verbose_name='ISSN web')),
                ('subtitle', models.CharField(max_length=255, null=True, blank=True)),
                ('localidentifier', models.CharField(max_length=50, null=True, blank=True, verbose_name='Identifiant Fedora')),
                ('paper', models.NullBooleanField(default=None, help_text='Est publiée également en version papier?', verbose_name='Papier')),
                ('open_access', models.NullBooleanField(default=None, help_text='Cette revue est en accès libre?', verbose_name='Libre accès')),
                ('issues_per_year', models.IntegerField(null=True, blank=True, verbose_name='Numéros par année')),
                ('url', models.URLField(null=True, blank=True, verbose_name='URL')),
                ('address', models.TextField(null=True, blank=True, verbose_name='Adresse')),
                ('active', models.BooleanField(default=True, help_text="Une revue inactive n'édite plus de numéros", verbose_name='Actif')),
                ('collection', models.ForeignKey(null=True, blank=True, to='erudit.Collection')),
                ('formerly', models.ForeignKey(null=True, blank=True, verbose_name='Anciennement', help_text="Choisir l'ancien nom de la revue", to='erudit.Journal')),
                ('members', models.ManyToManyField(related_name='journals', to=settings.AUTH_USER_MODEL, verbose_name='Membres')),
            ],
            options={
                'verbose_name_plural': 'Revues',
                'verbose_name': 'Revue',
                'ordering': ['name'],
            },
            bases=(erudit.fedora.modelmixins.FedoraMixin, models.Model),
        ),
        migrations.CreateModel(
            name='JournalInformation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('about', models.TextField(null=True, blank=True, verbose_name='Revue')),
                ('about_fr', models.TextField(null=True, blank=True, verbose_name='Revue')),
                ('about_en', models.TextField(null=True, blank=True, verbose_name='Revue')),
                ('editorial_policy', models.TextField(null=True, blank=True, verbose_name='Politique éditoriale')),
                ('editorial_policy_fr', models.TextField(null=True, blank=True, verbose_name='Politique éditoriale')),
                ('editorial_policy_en', models.TextField(null=True, blank=True, verbose_name='Politique éditoriale')),
                ('subscriptions', models.TextField(null=True, blank=True, verbose_name='Abonnements')),
                ('subscriptions_fr', models.TextField(null=True, blank=True, verbose_name='Abonnements')),
                ('subscriptions_en', models.TextField(null=True, blank=True, verbose_name='Abonnements')),
                ('team', models.TextField(null=True, blank=True, verbose_name='Équipe')),
                ('team_fr', models.TextField(null=True, blank=True, verbose_name='Équipe')),
                ('team_en', models.TextField(null=True, blank=True, verbose_name='Équipe')),
                ('contact', models.TextField(null=True, blank=True, verbose_name='Contact')),
                ('contact_fr', models.TextField(null=True, blank=True, verbose_name='Contact')),
                ('contact_en', models.TextField(null=True, blank=True, verbose_name='Contact')),
                ('partners', models.TextField(null=True, blank=True, verbose_name='Partenaires')),
                ('partners_fr', models.TextField(null=True, blank=True, verbose_name='Partenaires')),
                ('partners_en', models.TextField(null=True, blank=True, verbose_name='Partenaires')),
                ('journal', models.OneToOneField(verbose_name='Journal', related_name='information', to='erudit.Journal')),
            ],
            options={
                'verbose_name_plural': 'Informations de revue',
                'verbose_name': 'Information de revue',
            },
        ),
        migrations.CreateModel(
            name='JournalProduction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('journal', models.ForeignKey(verbose_name='Revue', related_name='production', to='erudit.Journal')),
            ],
            options={
                'verbose_name_plural': 'Productions de revue',
                'verbose_name': 'Production de revue',
                'ordering': ['journal'],
            },
        ),
        migrations.CreateModel(
            name='JournalType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, null=True, blank=True, verbose_name='Nom')),
                ('code', models.SlugField(unique=True, choices=[('C', 'Culturel'), ('S', 'Savant')], verbose_name='Code', max_length=2)),
            ],
            options={
                'verbose_name_plural': 'Types de revue',
                'verbose_name': 'Type de revue',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Library',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Nom')),
            ],
            options={
                'verbose_name_plural': 'Bibliothèques',
                'verbose_name': 'Bibliothèque',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='MandragoreProfile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('synced_with_mandragore', models.BooleanField(default=False, verbose_name='Synchronisé avec Mandragore')),
                ('mandragore_id', models.CharField(max_length=7, null=True, blank=True, verbose_name='Identifiant Mandragore')),
                ('sync_date', models.DateField(null=True, blank=True)),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Organisation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=120, verbose_name='Nom')),
                ('street', models.CharField(max_length=200, null=True, blank=True, verbose_name='Adresse')),
                ('postal_code', models.CharField(max_length=50, null=True, blank=True, verbose_name='Code postal')),
                ('city', models.CharField(max_length=50, null=True, blank=True, verbose_name='Ville')),
                ('province', models.CharField(max_length=50, null=True, blank=True, verbose_name='Province')),
                ('country', models.CharField(max_length=50, null=True, blank=True, verbose_name='Pays')),
            ],
            options={
                'verbose_name_plural': 'Organisations',
                'verbose_name': 'Organisation',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Person',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('lastname', models.CharField(max_length=50, verbose_name='Nom')),
                ('firstname', models.CharField(max_length=50, null=True, blank=True, verbose_name='Prénom')),
                ('email', models.EmailField(max_length=254, null=True, blank=True, verbose_name='Courriel')),
                ('organisation', models.ForeignKey(null=True, blank=True, verbose_name='Organisation', to='erudit.Organisation')),
            ],
            options={
                'verbose_name_plural': 'Personnes',
                'verbose_name': 'Personne',
                'ordering': ['lastname'],
            },
        ),
        migrations.CreateModel(
            name='ProductionCenter',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=255, verbose_name='Code')),
                ('name', models.CharField(max_length=255, verbose_name='Nom')),
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
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=255, verbose_name='Code')),
                ('name', models.CharField(max_length=255, verbose_name='Nom')),
            ],
            options={
                'verbose_name_plural': 'Types de production',
                'verbose_name': 'Type de production',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Publisher',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('synced_with_edinum', models.BooleanField(default=False, verbose_name='Synchronisé avec Edinum')),
                ('edinum_id', models.CharField(max_length=7, null=True, blank=True, verbose_name='Identifiant Edinum')),
                ('sync_date', models.DateField(null=True, blank=True)),
                ('name', models.CharField(max_length=255, verbose_name='Nom')),
            ],
            options={
                'verbose_name_plural': 'Éditeurs',
                'verbose_name': 'Éditeur',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Quotation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.TextField(null=True, blank=True)),
                ('date_start', models.DateField(null=True, blank=True)),
                ('date_end', models.DateField(null=True, blank=True)),
                ('journal', models.ForeignKey(null=True, blank=True, to='erudit.Journal')),
            ],
        ),
        migrations.CreateModel(
            name='QuotationItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('total', models.DecimalField(decimal_places=2, null=True, blank=True, max_digits=15)),
                ('quotation', models.ForeignKey(to='erudit.Quotation')),
            ],
        ),
        migrations.AddField(
            model_name='journalproduction',
            name='production_center',
            field=models.ForeignKey(null=True, blank=True, verbose_name='Centre de production', help_text='Centre de production responsable\n            de la production de la revue.', to='erudit.ProductionCenter'),
        ),
        migrations.AddField(
            model_name='journalproduction',
            name='production_type',
            field=models.ForeignKey(null=True, blank=True, verbose_name='Type de production', to='erudit.ProductionType'),
        ),
        migrations.AddField(
            model_name='journal',
            name='publishers',
            field=models.ManyToManyField(related_name='journals', to='erudit.Publisher', verbose_name='Éditeur'),
        ),
        migrations.AddField(
            model_name='journal',
            name='type',
            field=models.ForeignKey(null=True, blank=True, verbose_name='Type', to='erudit.JournalType'),
        ),
        migrations.AddField(
            model_name='issue',
            name='journal',
            field=models.ForeignKey(verbose_name='Revue', related_name='issues', to='erudit.Journal'),
        ),
        migrations.AddField(
            model_name='invoice',
            name='journal',
            field=models.ForeignKey(null=True, blank=True, verbose_name='Revue', help_text='Revue facturée', to='erudit.Journal'),
        ),
        migrations.AddField(
            model_name='indexation',
            name='indexer',
            field=models.ForeignKey(to='erudit.Indexer', verbose_name='Indexeur'),
        ),
        migrations.AddField(
            model_name='indexation',
            name='journal',
            field=models.ForeignKey(to='erudit.Journal', verbose_name='Revue'),
        ),
        migrations.AddField(
            model_name='grant',
            name='granting_agency',
            field=models.ForeignKey(to='erudit.GrantingAgency', verbose_name='Organisme subventionnaire'),
        ),
        migrations.AddField(
            model_name='grant',
            name='journal',
            field=models.ForeignKey(verbose_name='Revue', related_name='grants', help_text='Revue ayant obtenu cette subvention', to='erudit.Journal'),
        ),
        migrations.AddField(
            model_name='contract',
            name='journal',
            field=models.ForeignKey(verbose_name='Revue', related_name='contracts', to='erudit.Journal'),
        ),
        migrations.AddField(
            model_name='contract',
            name='status',
            field=models.ForeignKey(null=True, blank=True, verbose_name='État', related_name='contracts', to='erudit.ContractStatus'),
        ),
        migrations.AddField(
            model_name='contract',
            name='type',
            field=models.ForeignKey(verbose_name='Type', related_name='contracts', to='erudit.ContractType'),
        ),
        migrations.AddField(
            model_name='article',
            name='issue',
            field=models.ForeignKey(verbose_name='Numéro', related_name='issues', to='erudit.Issue'),
        ),
    ]
