# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('post_office', '0003_auto_20150922_1846'),
    ]

    operations = [
        migrations.CreateModel(
            name='Client',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('lastname', models.CharField(verbose_name='Nom', max_length=100)),
                ('firstname', models.CharField(verbose_name='Prénom', max_length=100, null=True, blank=True)),
                ('erudit_number', models.CharField(max_length=120)),
                ('email', models.EmailField(help_text="L'avis de renouvellement sera envoyé à cette adresse", verbose_name='Courriel', max_length=254, null=True, blank=True)),
                ('organisation', models.CharField(max_length=200, null=True, blank=True)),
                ('civic', models.TextField(verbose_name='Numéro civique', null=True, blank=True)),
                ('street', models.TextField(verbose_name='Rue', null=True, blank=True)),
                ('city', models.CharField(verbose_name='Ville', max_length=100, null=True, blank=True)),
                ('pobox', models.CharField(verbose_name='Casier postal', max_length=100)),
                ('province', models.CharField(verbose_name='Province', max_length=100)),
                ('country', models.CharField(verbose_name='Pays', max_length=100, null=True, blank=True)),
                ('postal_code', models.CharField(verbose_name='Code postal', max_length=50, null=True, blank=True)),
                ('exemption_code', models.CharField(verbose_name="Code d'exemption", max_length=1)),
                ('currency', models.CharField(verbose_name='Devise', max_length=3)),
            ],
            options={
                'verbose_name': 'Client',
                'ordering': ['organisation'],
                'verbose_name_plural': 'Clients',
            },
        ),
        migrations.CreateModel(
            name='Country',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('code', models.CharField(max_length=255, null=True, blank=True)),
                ('name', models.CharField(verbose_name='Nom', max_length=255)),
            ],
            options={
                'verbose_name': 'Pays',
                'ordering': ['name'],
                'verbose_name_plural': 'Pays',
            },
        ),
        migrations.CreateModel(
            name='Currency',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('code', models.CharField(max_length=255)),
                ('name', models.CharField(verbose_name='Nom', max_length=255)),
            ],
            options={
                'verbose_name': 'Devise',
                'ordering': ['code'],
                'verbose_name_plural': 'Devises',
            },
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('code', models.CharField(max_length=30)),
                ('title', models.CharField(verbose_name='Titre', max_length=200, null=True, blank=True)),
                ('description', models.CharField(max_length=200, null=True, blank=True)),
                ('amount', models.DecimalField(verbose_name='Montant 2016', default=0.0, max_digits=7, decimal_places=2)),
                ('hide_in_renewal_items', models.BooleanField(verbose_name="Ne pas afficher dans la liste d'items des avis", default=False)),
                ('titles', models.ManyToManyField(verbose_name='Titres', blank=True, to='subscription.Product')),
            ],
            options={
                'verbose_name': 'Produit',
                'ordering': ['title'],
                'verbose_name_plural': 'Produits',
            },
        ),
        migrations.CreateModel(
            name='RenewalNotice',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('renewal_number', models.CharField(verbose_name="Numéro d'avis", max_length=20)),
                ('po_number', models.CharField(help_text='Numéro de bon de commande', verbose_name='Bon de commande', max_length=30, null=True, blank=True)),
                ('amount_total', models.DecimalField(help_text='Montant des articles demandés (sous-total avant Rabais)', verbose_name='Montant total', default=0.0, max_digits=7, decimal_places=2)),
                ('rebate', models.DecimalField(help_text='Applicable avant taxes, sur Montant total', verbose_name='Rabais', default=0.0, max_digits=7, decimal_places=2)),
                ('raw_amount', models.DecimalField(help_text='Montant total - Rabais (sous-total après Rabais)', verbose_name='Montant brut', default=0.0, max_digits=7, decimal_places=2)),
                ('federal_tax', models.DecimalField(verbose_name='Taxe fédérale', default=0.0, max_digits=7, decimal_places=2)),
                ('provincial_tax', models.DecimalField(verbose_name='Taxe provinciale', default=0.0, max_digits=7, decimal_places=2)),
                ('harmonized_tax', models.DecimalField(verbose_name='Taxe harmonisée', default=0.0, max_digits=7, decimal_places=2)),
                ('net_amount', models.DecimalField(help_text='Montant brut + Taxes (total facturable, taxes incl.)', verbose_name='Montant net', default=0.0, max_digits=7, decimal_places=2)),
                ('currency', models.CharField(verbose_name='Devise', max_length=5, null=True, blank=True)),
                ('has_basket', models.BooleanField(verbose_name='Avec panier', editable=False, default=False)),
                ('has_rebate', models.BooleanField(verbose_name='Avec rabais', default=False)),
                ('date_created', models.DateField(verbose_name='Date de création', null=True, blank=True)),
                ('no_error', models.BooleanField(help_text='Renseigné automatiquement par système.', verbose_name='Sans erreur', editable=False, default=True)),
                ('error_msg', models.TextField(help_text='Renseigné automatiquement par système si existe erreur(s).', verbose_name="Messages d'erreur", editable=False, default='')),
                ('status', models.CharField(verbose_name='État', default='DONT', max_length=4, choices=[('DONT', 'Ne pas envoyer'), ('TODO', 'À envoyer'), ('SENT', 'Envoyé'), ('REDO', 'À ré-envoyer')])),
                ('comment', models.TextField(help_text="Commentaire libre pour suivi de l'avis", verbose_name='Commentaire', null=True, blank=True)),
                ('paying_customer', models.ForeignKey(verbose_name='Client payeur', null=True, blank=True, to='subscription.Client', related_name='paid_renewals')),
                ('products', models.ManyToManyField(verbose_name='Produits', blank=True, to='subscription.Product')),
                ('receiving_customer', models.ForeignKey(verbose_name='Client receveur', null=True, blank=True, to='subscription.Client', related_name='received_renewals')),
                ('sent_emails', models.ManyToManyField(verbose_name='Courriels envoyés', blank=True, to='post_office.Email')),
            ],
            options={
                'verbose_name': 'Avis de renouvellement',
                'ordering': ['paying_customer'],
                'verbose_name_plural': 'Avis de renouvellement',
            },
        ),
        migrations.AddField(
            model_name='country',
            name='currency',
            field=models.ForeignKey(verbose_name='Devise', null=True, blank=True, to='subscription.Currency', related_name='pays'),
        ),
    ]
