# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('subscription', '0003_auto_20151002_2112'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='client',
            options={'verbose_name': 'Client', 'verbose_name_plural': 'Clients', 'ordering': ['organisation']},
        ),
        migrations.AlterModelOptions(
            name='product',
            options={'verbose_name': 'Produit', 'verbose_name_plural': 'Produits', 'ordering': ['title']},
        ),
        migrations.AlterModelOptions(
            name='renewalnotice',
            options={'verbose_name': 'Avis de renouvellement', 'verbose_name_plural': 'Avis de renouvellement', 'ordering': ['paying_customer']},
        ),
        migrations.AlterModelOptions(
            name='renewalnoticestatus',
            options={'verbose_name': "État d'Avis de renouvellement", 'verbose_name_plural': "États d'Avis de renouvellement", 'ordering': ['name']},
        ),
        migrations.AlterField(
            model_name='client',
            name='city',
            field=models.CharField(null=True, verbose_name='Ville', max_length=50, blank=True),
        ),
        migrations.AlterField(
            model_name='client',
            name='country',
            field=models.CharField(null=True, verbose_name='Pays', max_length=50, blank=True),
        ),
        migrations.AlterField(
            model_name='client',
            name='email',
            field=models.EmailField(null=True, verbose_name='Courriel', max_length=254, help_text="L'avis de renouvellement sera envoyé à cette adresse", blank=True),
        ),
        migrations.AlterField(
            model_name='client',
            name='firstname',
            field=models.CharField(null=True, verbose_name='Prénom', max_length=50, blank=True),
        ),
        migrations.AlterField(
            model_name='client',
            name='lastname',
            field=models.CharField(null=True, verbose_name='Nom', max_length=50, blank=True),
        ),
        migrations.AlterField(
            model_name='client',
            name='organisation',
            field=models.CharField(null=True, max_length=200, blank=True),
        ),
        migrations.AlterField(
            model_name='client',
            name='postal_code',
            field=models.CharField(null=True, verbose_name='Code postal', max_length=50, blank=True),
        ),
        migrations.AlterField(
            model_name='client',
            name='province',
            field=models.CharField(null=True, verbose_name='Province', max_length=50, blank=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='amount',
            field=models.DecimalField(null=True, verbose_name='Montant 2016', decimal_places=2, max_digits=7, blank=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='description',
            field=models.CharField(null=True, max_length=200, blank=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='title',
            field=models.CharField(null=True, verbose_name='Titre', max_length=200, blank=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='titles',
            field=models.ManyToManyField(verbose_name='Titres', to='subscription.Product', blank=True),
        ),
        migrations.AlterField(
            model_name='renewalnotice',
            name='amount_total',
            field=models.DecimalField(verbose_name='Montant total', help_text='Montant des articles demandés (sous-total avant Rabais)', max_digits=7, null=True, decimal_places=2, blank=True),
        ),
        migrations.AlterField(
            model_name='renewalnotice',
            name='currency',
            field=models.CharField(null=True, verbose_name='Devise', max_length=5, blank=True),
        ),
        migrations.AlterField(
            model_name='renewalnotice',
            name='date_created',
            field=models.DateField(null=True, verbose_name='Date de création', blank=True),
        ),
        migrations.AlterField(
            model_name='renewalnotice',
            name='federal_tax',
            field=models.DecimalField(null=True, verbose_name='Taxe fédérale', decimal_places=2, max_digits=7, blank=True),
        ),
        migrations.AlterField(
            model_name='renewalnotice',
            name='harmonized_tax',
            field=models.DecimalField(null=True, verbose_name='Taxe harmonisée', decimal_places=2, max_digits=7, blank=True),
        ),
        migrations.AlterField(
            model_name='renewalnotice',
            name='net_amount',
            field=models.DecimalField(verbose_name='Montant net', help_text='Montant brut + Taxes (total facturable, taxes incl.)', max_digits=7, null=True, decimal_places=2, blank=True),
        ),
        migrations.AlterField(
            model_name='renewalnotice',
            name='paying_customer',
            field=models.ForeignKey(verbose_name='Client payeur', to='subscription.Client', null=True, related_name='paid_renewals', blank=True),
        ),
        migrations.AlterField(
            model_name='renewalnotice',
            name='po_number',
            field=models.CharField(null=True, verbose_name='Bon de commande', max_length=30, help_text='Numéro de bon de commande', blank=True),
        ),
        migrations.AlterField(
            model_name='renewalnotice',
            name='products',
            field=models.ManyToManyField(verbose_name='Produits', to='subscription.Product', blank=True),
        ),
        migrations.AlterField(
            model_name='renewalnotice',
            name='provincial_tax',
            field=models.DecimalField(null=True, verbose_name='Taxe provinciale', decimal_places=2, max_digits=7, blank=True),
        ),
        migrations.AlterField(
            model_name='renewalnotice',
            name='raw_amount',
            field=models.DecimalField(verbose_name='Montant brut', help_text='Montant total - Rabais (sous-total après Rabais)', max_digits=7, null=True, decimal_places=2, blank=True),
        ),
        migrations.AlterField(
            model_name='renewalnotice',
            name='rebate',
            field=models.DecimalField(verbose_name='Rabais', help_text='Applicable avant taxes, sur Montant total', max_digits=7, null=True, decimal_places=2, blank=True),
        ),
        migrations.AlterField(
            model_name='renewalnotice',
            name='receiving_customer',
            field=models.ForeignKey(verbose_name='Client receveur', to='subscription.Client', null=True, related_name='received_renewals', blank=True),
        ),
        migrations.AlterField(
            model_name='renewalnotice',
            name='status',
            field=models.ForeignKey(verbose_name='État', to='subscription.RenewalNoticeStatus', help_text="Choisir ou ajouter une option à volonté (tagger l'Avis pour suivi)", null=True, related_name='renewal_notices', blank=True),
        ),
    ]
