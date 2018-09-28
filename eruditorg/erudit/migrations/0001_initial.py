# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings
import erudit.fedora.modelmixins


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Author',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('lastname', models.CharField(max_length=50, verbose_name='Nom')),
                ('firstname', models.CharField(null=True, max_length=50, blank=True, verbose_name='Prénom')),
                ('email', models.EmailField(null=True, max_length=254, blank=True, verbose_name='Courriel')),
                ('suffix', models.CharField(null=True, max_length=20, blank=True, verbose_name='Suffixe')),
            ],
            options={
                'verbose_name_plural': 'Auteurs',
                'verbose_name': 'Auteur',
            },
        ),
        migrations.CreateModel(
            name='Basket',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('code', models.CharField(max_length=255, verbose_name='Code')),
                ('name', models.CharField(max_length=255, verbose_name='Nom')),
            ],
            options={
                'verbose_name_plural': 'Paniers',
                'ordering': ['name'],
                'verbose_name': 'Panier',
            },
        ),
        migrations.CreateModel(
            name='Collection',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('synced_with_edinum', models.BooleanField(default=False, verbose_name='Synchronisé avec Edinum')),
                ('edinum_id', models.CharField(null=True, max_length=7, blank=True, verbose_name='Identifiant Edinum')),
                ('sync_date', models.DateField(null=True, blank=True)),
                ('name', models.CharField(max_length=200)),
                ('code', models.CharField(null=True, max_length=10, blank=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Contract',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('date_start', models.DateField(help_text='Date de début du contrat, format aaaa-mm-jj', verbose_name='Début')),
                ('date_end', models.DateField(help_text='Date de fin du contrat, format aaaa-mm-jj', verbose_name='Fin')),
                ('date_signature', models.DateField(null=True, help_text='Date de signature du contrat, format aaaa-mm-jj', blank=True, verbose_name='Signé le')),
            ],
            options={
                'verbose_name_plural': 'Contrats',
                'ordering': ['journal'],
                'verbose_name': 'Contrat',
            },
        ),
        migrations.CreateModel(
            name='ContractStatus',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Nom')),
            ],
            options={
                'verbose_name_plural': 'Statuts de contrat',
                'ordering': ['name'],
                'verbose_name': 'Statut de contrat',
            },
        ),
        migrations.CreateModel(
            name='ContractType',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('code', models.CharField(help_text='Court identifiant utilisé dans le nom automatique des contrats', max_length=255, verbose_name='Code')),
                ('name', models.CharField(max_length=255, verbose_name='Nom')),
            ],
            options={
                'verbose_name_plural': 'Types de contrat',
                'ordering': ['name'],
                'verbose_name': 'Type de contrat',
            },
        ),
        migrations.CreateModel(
            name='Currency',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('code', models.CharField(max_length=255)),
                ('name', models.CharField(max_length=255, verbose_name='Nom')),
            ],
            options={
                'verbose_name_plural': 'Devises',
                'ordering': ['code'],
                'verbose_name': 'Devise',
            },
        ),
        migrations.CreateModel(
            name='Discipline',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Nom')),
                ('name_fr', models.CharField(null=True, max_length=255, verbose_name='Nom')),
                ('name_en', models.CharField(null=True, max_length=255, verbose_name='Nom')),
                ('code', models.CharField(max_length=255, unique=True, verbose_name='Code')),
            ],
            options={
                'verbose_name_plural': 'Disciplines',
                'verbose_name': 'Discipline',
            },
        ),
        migrations.CreateModel(
            name='EruditDocument',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('localidentifier', models.CharField(max_length=50, unique=True, verbose_name='Identifiant Fedora')),
            ],
            options={
                'verbose_name_plural': 'Documents Érudit',
                'verbose_name': 'Document Érudit',
            },
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('type', models.PositiveIntegerField(choices=[(1, 'Création de soumission'), (2, 'Changement de statut de soumission')])),
                ('time', models.DateTimeField(auto_now_add=True, verbose_name='Date/Heure')),
                ('target_object_id', models.PositiveIntegerField()),
                ('comment', models.TextField(verbose_name='Commentaire')),
                ('author', models.ForeignKey(on_delete=models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Auteur')),
                ('target_content_type', models.ForeignKey(on_delete=models.deletion.CASCADE, to='contenttypes.ContentType')),
            ],
            options={
                'verbose_name_plural': 'Événements',
                'verbose_name': 'Événement',
            },
        ),
        migrations.CreateModel(
            name='Grant',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('amount', models.DecimalField(null=True, max_digits=15, decimal_places=2, blank=True, verbose_name='Montant')),
                ('date_start', models.DateField(null=True, blank=True, verbose_name='Date de début')),
                ('date_end', models.DateField(null=True, blank=True, verbose_name='Date de fin')),
                ('currency', models.ForeignKey(on_delete=models.deletion.CASCADE, blank=True, null=True, verbose_name='Devise', to='erudit.Currency')),
            ],
            options={
                'verbose_name_plural': 'Subventions',
                'ordering': ['journal'],
                'verbose_name': 'Subvention',
            },
        ),
        migrations.CreateModel(
            name='GrantingAgency',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('code', models.CharField(help_text='Acronyme', max_length=255, verbose_name='Code')),
                ('name', models.CharField(max_length=255, verbose_name='Nom')),
            ],
            options={
                'verbose_name_plural': 'Organismes subventionnaires',
                'ordering': ['name'],
                'verbose_name': 'Organisme subventionnaire',
            },
        ),
        migrations.CreateModel(
            name='Indexation',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
            ],
            options={
                'verbose_name_plural': 'Indexations',
                'ordering': ['journal'],
                'verbose_name': 'Indexation',
            },
        ),
        migrations.CreateModel(
            name='Indexer',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Nom')),
            ],
            options={
                'verbose_name_plural': 'Indexeurs',
                'ordering': ['name'],
                'verbose_name': 'Indexeur',
            },
        ),
        migrations.CreateModel(
            name='Invoice',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('id_sage', models.IntegerField(null=True, help_text='Identifiant de la facture dans SAGE.', blank=True, verbose_name='Id facture SAGE')),
                ('id_subcontractor', models.IntegerField(null=True, help_text='Identifiant de la facture du sous-contractant qui couvre cette facture (ex.: CEN-R).', blank=True, verbose_name='Id facture sous-contractant')),
                ('date', models.DateField(null=True, blank=True)),
                ('total_invoice_subcontractor', models.DecimalField(max_digits=15, help_text='Total de la facture du sous-contractant (ex.: CEN-R)', decimal_places=2, blank=True, null=True, verbose_name='Total facture sous-contractant')),
                ('total', models.DecimalField(null=True, max_digits=15, decimal_places=2, blank=True, verbose_name='Total')),
                ('status', models.CharField(choices=[('D', 'Draft'), ('V', 'Valid'), ('S', 'Sent'), ('P', 'Paid')], max_length=255, verbose_name='Statut')),
                ('currency', models.ForeignKey(on_delete=models.deletion.CASCADE, blank=True, null=True, verbose_name='Devise', to='erudit.Currency')),
            ],
            options={
                'verbose_name_plural': 'Factures',
                'ordering': ['journal'],
                'verbose_name': 'Facture',
            },
        ),
        migrations.CreateModel(
            name='Issue',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('title', models.CharField(null=True, max_length=255, blank=True)),
                ('year', models.IntegerField(null=True, choices=[(1900, 1900), (1901, 1901), (1902, 1902), (1903, 1903), (1904, 1904), (1905, 1905), (1906, 1906), (1907, 1907), (1908, 1908), (1909, 1909), (1910, 1910), (1911, 1911), (1912, 1912), (1913, 1913), (1914, 1914), (1915, 1915), (1916, 1916), (1917, 1917), (1918, 1918), (1919, 1919), (1920, 1920), (1921, 1921), (1922, 1922), (1923, 1923), (1924, 1924), (1925, 1925), (1926, 1926), (1927, 1927), (1928, 1928), (1929, 1929), (1930, 1930), (1931, 1931), (1932, 1932), (1933, 1933), (1934, 1934), (1935, 1935), (1936, 1936), (1937, 1937), (1938, 1938), (1939, 1939), (1940, 1940), (1941, 1941), (1942, 1942), (1943, 1943), (1944, 1944), (1945, 1945), (1946, 1946), (1947, 1947), (1948, 1948), (1949, 1949), (1950, 1950), (1951, 1951), (1952, 1952), (1953, 1953), (1954, 1954), (1955, 1955), (1956, 1956), (1957, 1957), (1958, 1958), (1959, 1959), (1960, 1960), (1961, 1961), (1962, 1962), (1963, 1963), (1964, 1964), (1965, 1965), (1966, 1966), (1967, 1967), (1968, 1968), (1969, 1969), (1970, 1970), (1971, 1971), (1972, 1972), (1973, 1973), (1974, 1974), (1975, 1975), (1976, 1976), (1977, 1977), (1978, 1978), (1979, 1979), (1980, 1980), (1981, 1981), (1982, 1982), (1983, 1983), (1984, 1984), (1985, 1985), (1986, 1986), (1987, 1987), (1988, 1988), (1989, 1989), (1990, 1990), (1991, 1991), (1992, 1992), (1993, 1993), (1994, 1994), (1995, 1995), (1996, 1996), (1997, 1997), (1998, 1998), (1999, 1999), (2000, 2000), (2001, 2001), (2002, 2002), (2003, 2003), (2004, 2004), (2005, 2005), (2006, 2006), (2007, 2007), (2008, 2008), (2009, 2009), (2010, 2010), (2011, 2011), (2012, 2012), (2013, 2013), (2014, 2014), (2015, 2015), (2016, 2016), (2017, 2017), (2018, 2018), (2019, 2019), (2020, 2020), (2021, 2021)], blank=True, verbose_name='Année')),
                ('volume', models.CharField(null=True, max_length=255, blank=True, verbose_name='Volume')),
                ('number', models.CharField(null=True, max_length=255, blank=True, verbose_name='Numéro')),
                ('special_issue', models.BooleanField(help_text="Cocher s'il s'agit d'un numéro spécial.", default=False, verbose_name='Numéro spécial')),
                ('date_produced', models.DateField(null=True, blank=True, verbose_name='Date de production')),
                ('date_published', models.DateField(null=True, blank=True, verbose_name='Date de publication')),
                ('open_access', models.NullBooleanField(help_text='Cocher si ce numéro est en accès libre', default=None, verbose_name='Accès libre')),
                ('localidentifier', models.CharField(max_length=50, unique=True, verbose_name='Identifiant Fedora')),
            ],
            options={
                'verbose_name_plural': 'Numéros',
                'ordering': ['journal', 'year', 'volume', 'number'],
                'verbose_name': 'Numéro',
            },
            bases=(erudit.fedora.modelmixins.FedoraMixin, models.Model),
        ),
        migrations.CreateModel(
            name='Journal',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('synced_with_edinum', models.BooleanField(default=False, verbose_name='Synchronisé avec Edinum')),
                ('edinum_id', models.CharField(null=True, max_length=7, blank=True, verbose_name='Identifiant Edinum')),
                ('sync_date', models.DateField(null=True, blank=True)),
                ('name', models.CharField(help_text='Nom officiel', max_length=255, verbose_name='Nom')),
                ('display_name', models.CharField(blank=True, null=True, help_text='Nom à utiliser dans tout affichage', max_length=255, verbose_name="Nom d'affichage")),
                ('code', models.SlugField(help_text='Identifiant unique (utilisé dans URL Érudit)', unique=True, max_length=255, verbose_name='Code')),
                ('issn_print', models.CharField(null=True, max_length=255, blank=True, verbose_name='ISSN imprimé')),
                ('issn_web', models.CharField(null=True, max_length=255, blank=True, verbose_name='ISSN web')),
                ('subtitle', models.CharField(null=True, max_length=255, blank=True)),
                ('localidentifier', models.CharField(max_length=50, unique=True, verbose_name='Identifiant Fedora')),
                ('paper', models.NullBooleanField(help_text='Est publiée également en version papier?', default=None, verbose_name='Papier')),
                ('open_access', models.NullBooleanField(help_text='Cette revue est en accès libre?', default=None, verbose_name='Libre accès')),
                ('issues_per_year', models.IntegerField(null=True, blank=True, verbose_name='Numéros par année')),
                ('url', models.URLField(null=True, blank=True, verbose_name='URL')),
                ('address', models.TextField(null=True, blank=True, verbose_name='Adresse')),
                ('active', models.BooleanField(help_text="Une revue inactive n'édite plus de numéros", default=True, verbose_name='Actif')),
                ('upcoming', models.BooleanField(default=False, verbose_name='Prochainement disponible')),
                ('collection', models.ForeignKey(on_delete=models.deletion.CASCADE, blank=True, null=True, to='erudit.Collection')),
                ('disciplines', models.ManyToManyField(related_name='journals', to='erudit.Discipline')),
                ('formerly', models.ForeignKey(on_delete=models.deletion.CASCADE, help_text="Choisir l'ancien nom de la revue", blank=True, null=True, verbose_name='Anciennement', to='erudit.Journal')),
                ('members', models.ManyToManyField(related_name='journals', to=settings.AUTH_USER_MODEL, verbose_name='Membres')),
            ],
            options={
                'verbose_name_plural': 'Revues',
                'ordering': ['name'],
                'verbose_name': 'Revue',
            },
            bases=(erudit.fedora.modelmixins.FedoraMixin, models.Model),
        ),
        migrations.CreateModel(
            name='JournalInformation',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
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
                ('journal', models.OneToOneField(on_delete=models.deletion.CASCADE, to='erudit.Journal', related_name='information', verbose_name='Journal')),
            ],
            options={
                'verbose_name_plural': 'Informations de revue',
                'verbose_name': 'Information de revue',
            },
        ),
        migrations.CreateModel(
            name='JournalProduction',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('journal', models.ForeignKey(on_delete=models.deletion.CASCADE, to='erudit.Journal', related_name='production', verbose_name='Revue')),
            ],
            options={
                'verbose_name_plural': 'Productions de revue',
                'ordering': ['journal'],
                'verbose_name': 'Production de revue',
            },
        ),
        migrations.CreateModel(
            name='JournalType',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('name', models.CharField(null=True, max_length=255, blank=True, verbose_name='Nom')),
                ('code', models.SlugField(choices=[('C', 'Culturel'), ('S', 'Savant')], max_length=2, unique=True, verbose_name='Code')),
            ],
            options={
                'verbose_name_plural': 'Types de revue',
                'ordering': ['name'],
                'verbose_name': 'Type de revue',
            },
        ),
        migrations.CreateModel(
            name='Library',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='Nom')),
            ],
            options={
                'verbose_name_plural': 'Bibliothèques',
                'ordering': ['name'],
                'verbose_name': 'Bibliothèque',
            },
        ),
        migrations.CreateModel(
            name='Organisation',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('name', models.CharField(max_length=120, verbose_name='Nom')),
                ('street', models.CharField(null=True, max_length=200, blank=True, verbose_name='Adresse')),
                ('postal_code', models.CharField(null=True, max_length=50, blank=True, verbose_name='Code postal')),
                ('city', models.CharField(null=True, max_length=50, blank=True, verbose_name='Ville')),
                ('province', models.CharField(null=True, max_length=50, blank=True, verbose_name='Province')),
                ('country', models.CharField(null=True, max_length=50, blank=True, verbose_name='Pays')),
                ('badge', models.ImageField(null=True, upload_to='organisation_badges', blank=True, verbose_name='Badge')),
            ],
            options={
                'verbose_name_plural': 'Organisations',
                'ordering': ['name'],
                'verbose_name': 'Organisation',
            },
        ),
        migrations.CreateModel(
            name='ProductionCenter',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('code', models.CharField(max_length=255, verbose_name='Code')),
                ('name', models.CharField(max_length=255, verbose_name='Nom')),
            ],
            options={
                'verbose_name_plural': 'Centres de production',
                'ordering': ['name'],
                'verbose_name': 'Centre de production',
            },
        ),
        migrations.CreateModel(
            name='ProductionType',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('code', models.CharField(max_length=255, verbose_name='Code')),
                ('name', models.CharField(max_length=255, verbose_name='Nom')),
            ],
            options={
                'verbose_name_plural': 'Types de production',
                'ordering': ['name'],
                'verbose_name': 'Type de production',
            },
        ),
        migrations.CreateModel(
            name='Publisher',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('synced_with_edinum', models.BooleanField(default=False, verbose_name='Synchronisé avec Edinum')),
                ('edinum_id', models.CharField(null=True, max_length=7, blank=True, verbose_name='Identifiant Edinum')),
                ('sync_date', models.DateField(null=True, blank=True)),
                ('name', models.CharField(max_length=255, verbose_name='Nom')),
            ],
            options={
                'verbose_name_plural': 'Éditeurs',
                'ordering': ['name'],
                'verbose_name': 'Éditeur',
            },
        ),
        migrations.CreateModel(
            name='Quotation',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('description', models.TextField(null=True, blank=True)),
                ('date_start', models.DateField(null=True, blank=True)),
                ('date_end', models.DateField(null=True, blank=True)),
                ('journal', models.ForeignKey(on_delete=models.deletion.CASCADE, blank=True, null=True, to='erudit.Journal')),
            ],
        ),
        migrations.CreateModel(
            name='QuotationItem',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('total', models.DecimalField(null=True, decimal_places=2, blank=True, max_digits=15)),
                ('currency', models.ForeignKey(on_delete=models.deletion.CASCADE, blank=True, null=True, to='erudit.Currency')),
                ('quotation', models.ForeignKey(on_delete=models.deletion.CASCADE, to='erudit.Quotation')),
            ],
        ),
        migrations.CreateModel(
            name='SubscriptionPrice',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('year', models.CharField(choices=[(1900, 1900), (1901, 1901), (1902, 1902), (1903, 1903), (1904, 1904), (1905, 1905), (1906, 1906), (1907, 1907), (1908, 1908), (1909, 1909), (1910, 1910), (1911, 1911), (1912, 1912), (1913, 1913), (1914, 1914), (1915, 1915), (1916, 1916), (1917, 1917), (1918, 1918), (1919, 1919), (1920, 1920), (1921, 1921), (1922, 1922), (1923, 1923), (1924, 1924), (1925, 1925), (1926, 1926), (1927, 1927), (1928, 1928), (1929, 1929), (1930, 1930), (1931, 1931), (1932, 1932), (1933, 1933), (1934, 1934), (1935, 1935), (1936, 1936), (1937, 1937), (1938, 1938), (1939, 1939), (1940, 1940), (1941, 1941), (1942, 1942), (1943, 1943), (1944, 1944), (1945, 1945), (1946, 1946), (1947, 1947), (1948, 1948), (1949, 1949), (1950, 1950), (1951, 1951), (1952, 1952), (1953, 1953), (1954, 1954), (1955, 1955), (1956, 1956), (1957, 1957), (1958, 1958), (1959, 1959), (1960, 1960), (1961, 1961), (1962, 1962), (1963, 1963), (1964, 1964), (1965, 1965), (1966, 1966), (1967, 1967), (1968, 1968), (1969, 1969), (1970, 1970), (1971, 1971), (1972, 1972), (1973, 1973), (1974, 1974), (1975, 1975), (1976, 1976), (1977, 1977), (1978, 1978), (1979, 1979), (1980, 1980), (1981, 1981), (1982, 1982), (1983, 1983), (1984, 1984), (1985, 1985), (1986, 1986), (1987, 1987), (1988, 1988), (1989, 1989), (1990, 1990), (1991, 1991), (1992, 1992), (1993, 1993), (1994, 1994), (1995, 1995), (1996, 1996), (1997, 1997), (1998, 1998), (1999, 1999), (2000, 2000), (2001, 2001), (2002, 2002), (2003, 2003), (2004, 2004), (2005, 2005), (2006, 2006), (2007, 2007), (2008, 2008), (2009, 2009), (2010, 2010), (2011, 2011), (2012, 2012), (2013, 2013), (2014, 2014), (2015, 2015), (2016, 2016), (2017, 2017), (2018, 2018), (2019, 2019), (2020, 2020), (2021, 2021)], max_length=255, verbose_name='Année')),
                ('price', models.DecimalField(null=True, max_digits=15, decimal_places=2, blank=True, verbose_name='Prix')),
                ('approved', models.BooleanField(default=False, verbose_name='Approuvé')),
                ('date_approved', models.DateField(null=True, blank=True, verbose_name="Date d'approbation")),
                ('currency', models.ForeignKey(on_delete=models.deletion.CASCADE, blank=True, null=True, verbose_name='Devise', to='erudit.Currency')),
                ('journal', models.ForeignKey(on_delete=models.deletion.CASCADE, to='erudit.Journal', verbose_name='Revue')),
            ],
            options={
                'verbose_name_plural': "Tarifs d'abonnement",
                'ordering': ['journal', 'year', 'type', 'zone'],
                'verbose_name': "Tarif d'abonnement",
            },
        ),
        migrations.CreateModel(
            name='SubscriptionType',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('code', models.CharField(max_length=255, verbose_name='Code')),
                ('name', models.CharField(max_length=255, verbose_name='Nom')),
            ],
            options={
                'verbose_name_plural': "Types d'abonnement",
                'ordering': ['name'],
                'verbose_name': "Type d'abonnement",
            },
        ),
        migrations.CreateModel(
            name='SubscriptionZone',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('code', models.CharField(max_length=255, verbose_name='Code')),
                ('name', models.CharField(max_length=255, verbose_name='Nom')),
            ],
            options={
                'verbose_name_plural': "Zones d'abonnement",
                'ordering': ['name'],
                'verbose_name': "Zone d'abonnement",
            },
        ),
        migrations.CreateModel(
            name='Article',
            fields=[
                ('eruditdocument_ptr', models.OneToOneField(on_delete=models.deletion.CASCADE, serialize=False, to='erudit.EruditDocument', primary_key=True, parent_link=True, auto_created=True)),
                ('surtitle', models.CharField(null=True, max_length=500, blank=True)),
                ('title', models.CharField(null=True, max_length=500, blank=True)),
                ('processing', models.CharField(choices=[('C', 'Complet'), ('M', 'Minimal')], max_length=1)),
            ],
            options={
                'verbose_name_plural': 'Articles',
                'verbose_name': 'Article',
            },
            bases=('erudit.eruditdocument', erudit.fedora.modelmixins.FedoraMixin),
        ),
        migrations.AddField(
            model_name='subscriptionprice',
            name='type',
            field=models.ForeignKey(on_delete=models.deletion.CASCADE, to='erudit.SubscriptionType', verbose_name='Type'),
        ),
        migrations.AddField(
            model_name='subscriptionprice',
            name='zone',
            field=models.ForeignKey(on_delete=models.deletion.CASCADE, to='erudit.SubscriptionZone', verbose_name='Zone'),
        ),
        migrations.AddField(
            model_name='journalproduction',
            name='production_center',
            field=models.ForeignKey(on_delete=models.deletion.CASCADE, help_text='Centre de production responsable\n            de la production de la revue.', blank=True, null=True, verbose_name='Centre de production', to='erudit.ProductionCenter'),
        ),
        migrations.AddField(
            model_name='journalproduction',
            name='production_type',
            field=models.ForeignKey(on_delete=models.deletion.CASCADE, blank=True, null=True, verbose_name='Type de production', to='erudit.ProductionType'),
        ),
        migrations.AddField(
            model_name='journal',
            name='publishers',
            field=models.ManyToManyField(related_name='journals', to='erudit.Publisher', verbose_name='Éditeur'),
        ),
        migrations.AddField(
            model_name='journal',
            name='type',
            field=models.ForeignKey(on_delete=models.deletion.CASCADE, blank=True, null=True, verbose_name='Type', to='erudit.JournalType'),
        ),
        migrations.AddField(
            model_name='issue',
            name='journal',
            field=models.ForeignKey(on_delete=models.deletion.CASCADE, to='erudit.Journal', related_name='issues', verbose_name='Revue'),
        ),
        migrations.AddField(
            model_name='invoice',
            name='journal',
            field=models.ForeignKey(on_delete=models.deletion.CASCADE, help_text='Revue facturée', blank=True, null=True, verbose_name='Revue', to='erudit.Journal'),
        ),
        migrations.AddField(
            model_name='indexation',
            name='indexer',
            field=models.ForeignKey(on_delete=models.deletion.CASCADE, to='erudit.Indexer', verbose_name='Indexeur'),
        ),
        migrations.AddField(
            model_name='indexation',
            name='journal',
            field=models.ForeignKey(on_delete=models.deletion.CASCADE, to='erudit.Journal', verbose_name='Revue'),
        ),
        migrations.AddField(
            model_name='grant',
            name='granting_agency',
            field=models.ForeignKey(on_delete=models.deletion.CASCADE, to='erudit.GrantingAgency', verbose_name='Organisme subventionnaire'),
        ),
        migrations.AddField(
            model_name='grant',
            name='journal',
            field=models.ForeignKey(on_delete=models.deletion.CASCADE, help_text='Revue ayant obtenu cette subvention', to='erudit.Journal', related_name='grants', verbose_name='Revue'),
        ),
        migrations.AddField(
            model_name='contract',
            name='journal',
            field=models.ForeignKey(on_delete=models.deletion.CASCADE, to='erudit.Journal', related_name='contracts', verbose_name='Revue'),
        ),
        migrations.AddField(
            model_name='contract',
            name='status',
            field=models.ForeignKey(on_delete=models.deletion.CASCADE, blank=True, related_name='contracts', null=True, verbose_name='État', to='erudit.ContractStatus'),
        ),
        migrations.AddField(
            model_name='contract',
            name='type',
            field=models.ForeignKey(on_delete=models.deletion.CASCADE, to='erudit.ContractType', related_name='contracts', verbose_name='Type'),
        ),
        migrations.AddField(
            model_name='basket',
            name='journals',
            field=models.ManyToManyField(help_text='Choisir les revues composant ce panier.', to='erudit.Journal', verbose_name='Revues'),
        ),
        migrations.AddField(
            model_name='author',
            name='organisation',
            field=models.ForeignKey(on_delete=models.deletion.CASCADE, blank=True, null=True, verbose_name='Organisation', to='erudit.Organisation'),
        ),
        migrations.AddField(
            model_name='article',
            name='authors',
            field=models.ManyToManyField(to='erudit.Author', verbose_name='Auteurs'),
        ),
        migrations.AddField(
            model_name='article',
            name='issue',
            field=models.ForeignKey(on_delete=models.deletion.CASCADE, to='erudit.Issue', related_name='issues', verbose_name='Numéro'),
        ),
    ]
