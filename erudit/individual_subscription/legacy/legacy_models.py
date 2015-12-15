# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
#
# Also note: You'll have to insert the output of 'django-admin sqlcustom [app_label]'
# into your database.
from __future__ import unicode_literals

from django.db import models


class Abonne(models.Model):
    abonneid = models.AutoField(db_column='AbonneID', primary_key=True)  # Field name made lowercase.
    categorieid = models.ForeignKey('Categorie', db_column='CategorieID')  # Field name made lowercase.
    abonne = models.CharField(db_column='Abonne', max_length=200, blank=True, null=True)  # Field name made lowercase.
    bibliotheque = models.CharField(db_column='Bibliotheque', max_length=200)  # Field name made lowercase.
    consortiumid = models.IntegerField(db_column='ConsortiumID')  # Field name made lowercase.
    activer = models.IntegerField(db_column='Activer')  # Field name made lowercase.
    service = models.CharField(db_column='Service', max_length=75)  # Field name made lowercase.
    exclure = models.IntegerField(db_column='Exclure')  # Field name made lowercase.
    abonnefact = models.CharField(db_column='AbonneFact', max_length=200)  # Field name made lowercase.
    bibliothequefact = models.CharField(db_column='BibliothequeFact', max_length=200)  # Field name made lowercase.
    servicefact = models.CharField(db_column='ServiceFact', max_length=75)  # Field name made lowercase.
    maj = models.DateTimeField(db_column='MAJ')  # Field name made lowercase.
    agence = models.IntegerField(db_column='Agence')  # Field name made lowercase.
    icone = models.CharField(max_length=75)
    requesterid = models.CharField(db_column='requesterID', max_length=45, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'abonne'

    def __str__(self):
        return '{} [type: {}] {}'.format(self.abonneid, self.categorieid, self.abonne)


class Abonneaccess(models.Model):
    abonneaccessid = models.AutoField(db_column='AbonneAccessID', primary_key=True)  # Field name made lowercase.
    ip = models.CharField(max_length=50, blank=True, null=True)
    mot_de_passe = models.CharField(max_length=50, blank=True, null=True)
    abonneid = models.IntegerField(db_column='AbonneID', blank=True, null=True)  # Field name made lowercase.
    exclure = models.IntegerField(db_column='Exclure')  # Field name made lowercase.
    maj = models.DateTimeField(db_column='MAJ')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'abonneaccess'


class Abonneindividus(models.Model):
    abonneindividusid = models.AutoField(db_column='abonneIndividusID', primary_key=True)  # Field name made lowercase.
    password = models.CharField(max_length=50)
    nom = models.CharField(max_length=30)
    prenom = models.CharField(max_length=30)
    courriel = models.CharField(max_length=120, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'abonneindividus'


class Abonnement(models.Model):
    abonnementid = models.AutoField(db_column='AbonnementID', primary_key=True)  # Field name made lowercase.
    abonneid = models.IntegerField(db_column='AbonneID', blank=True, null=True)  # Field name made lowercase.
    prixtotalabonnement = models.DecimalField(db_column='PrixTotalAbonnement', max_digits=20, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    typeabonnementid = models.IntegerField(db_column='TypeAbonnementID', blank=True, null=True)  # Field name made lowercase.
    categorieid = models.IntegerField(db_column='CategorieID', blank=True, null=True)  # Field name made lowercase.
    typedocumentid = models.IntegerField(db_column='TypeDocumentID', blank=True, null=True)  # Field name made lowercase.
    modeaccessid = models.IntegerField(db_column='ModeAccessID', blank=True, null=True)  # Field name made lowercase.
    individuid = models.IntegerField(db_column='IndividuID', blank=True, null=True)  # Field name made lowercase.
    consortiumid = models.IntegerField(db_column='ConsortiumID', blank=True, null=True)  # Field name made lowercase.
    debutabonnement = models.DateTimeField(db_column='DebutAbonnement', blank=True, null=True)  # Field name made lowercase.
    finabonnement = models.DateTimeField(db_column='FinAbonnement', blank=True, null=True)  # Field name made lowercase.
    papier = models.IntegerField(db_column='Papier', blank=True, null=True)  # Field name made lowercase.
    commentaires = models.TextField(db_column='Commentaires', blank=True, null=True)  # Field name made lowercase.
    gratuit = models.IntegerField(blank=True, null=True)
    maj = models.DateTimeField(db_column='MAJ')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'abonnement'


class Abonnepanier(models.Model):
    abonnepanierid = models.AutoField(db_column='AbonnePanierID', primary_key=True)  # Field name made lowercase.
    abonneid = models.IntegerField(db_column='AbonneID')  # Field name made lowercase.
    panierid = models.IntegerField(db_column='PanierID')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'abonnepanier'


class Adresse(models.Model):
    adresseid = models.AutoField(db_column='AdresseID', primary_key=True)  # Field name made lowercase.
    typeadresseid = models.IntegerField(db_column='TypeAdresseID', blank=True, null=True)  # Field name made lowercase.
    adresse1 = models.CharField(db_column='Adresse1', max_length=70, blank=True, null=True)  # Field name made lowercase.
    contactid = models.IntegerField(db_column='ContactID', blank=True, null=True)  # Field name made lowercase.
    abonneid = models.IntegerField(db_column='AbonneID')  # Field name made lowercase.
    paysid = models.IntegerField(db_column='PaysID')  # Field name made lowercase.
    provinceetatid = models.IntegerField(db_column='ProvinceEtatID')  # Field name made lowercase.
    codepostal = models.CharField(db_column='CodePostal', max_length=45, blank=True, null=True)  # Field name made lowercase.
    autreprovince = models.CharField(db_column='AutreProvince', max_length=55)  # Field name made lowercase.
    ville = models.CharField(db_column='Ville', max_length=50)  # Field name made lowercase.
    adresse2 = models.CharField(db_column='Adresse2', max_length=70, blank=True, null=True)  # Field name made lowercase.
    maj = models.DateTimeField(db_column='MAJ')  # Field name made lowercase.
    localisationid = models.IntegerField(db_column='LocalisationID')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'adresse'


class Adressesip(models.Model):
    adresseipid = models.BigIntegerField(db_column='adresseIPID', primary_key=True)  # Field name made lowercase.
    abonneid = models.IntegerField(db_column='AbonneID', blank=True, null=True)  # Field name made lowercase.
    ip = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'adressesip'


class Categorie(models.Model):
    categorieid = models.AutoField(db_column='CategorieID', primary_key=True)  # Field name made lowercase.
    categorie = models.CharField(db_column='Categorie', max_length=100, blank=True, null=True)  # Field name made lowercase.
    categorieanglais = models.CharField(db_column='CategorieAnglais', max_length=100, blank=True, null=True)  # Field name made lowercase.
    pourcentage = models.CharField(db_column='Pourcentage', max_length=50, blank=True, null=True)  # Field name made lowercase.
    langue = models.CharField(max_length=2)
    maj = models.DateTimeField(db_column='MAJ')  # Field name made lowercase.
    idunique = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'categorie'

    def __str__(self):
        return '{} {}'.format(self.categorieid, self.categorie)


class Commande(models.Model):
    commandeid = models.AutoField(primary_key=True)
    nocommande = models.CharField(max_length=45)
    daterecu = models.DateField()
    heurerecu = models.TimeField(blank=True, null=True)
    abonneid = models.IntegerField()
    anneeabonnement = models.TextField(db_column='AnneeAbonnement')  # Field name made lowercase. This field type is a guess.
    noboncommande = models.CharField(db_column='NoBonCommande', max_length=45)  # Field name made lowercase.
    panier = models.IntegerField()
    maj = models.DateTimeField(db_column='MAJ')  # Field name made lowercase.
    prorata = models.IntegerField(db_column='Prorata')  # Field name made lowercase.
    periode = models.CharField(db_column='Periode', max_length=45)  # Field name made lowercase.
    trimestrepayable = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'commande'


class Consortium(models.Model):
    consortiumid = models.AutoField(db_column='ConsortiumID', primary_key=True)  # Field name made lowercase.
    consortium = models.CharField(db_column='Consortium', max_length=100, blank=True, null=True)  # Field name made lowercase.
    maj = models.DateTimeField(db_column='MAJ')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'consortium'


class Contact(models.Model):
    contactid = models.AutoField(db_column='ContactID', primary_key=True)  # Field name made lowercase.
    typecontactid = models.ForeignKey('Typecontact', db_column='TypeContactID', blank=True, null=True)  # Field name made lowercase.
    nomfamille = models.CharField(db_column='NomFamille', max_length=50, blank=True, null=True)  # Field name made lowercase.
    prenom = models.CharField(db_column='Prenom', max_length=50, blank=True, null=True)  # Field name made lowercase.
    courriel = models.CharField(db_column='Courriel', max_length=50, blank=True, null=True)  # Field name made lowercase.
    abonneid = models.IntegerField(db_column='AbonneID', blank=True, null=True)  # Field name made lowercase.
    telephone = models.CharField(db_column='Telephone', max_length=25, blank=True, null=True)  # Field name made lowercase.
    telecopieur = models.CharField(db_column='Telecopieur', max_length=25)  # Field name made lowercase.
    exclure = models.IntegerField(db_column='Exclure')  # Field name made lowercase.
    motdepasse = models.CharField(db_column='MotDePasse', unique=True, max_length=45)  # Field name made lowercase.
    nomfamillefact = models.CharField(db_column='NomFamilleFact', max_length=50)  # Field name made lowercase.
    prenomfact = models.CharField(db_column='PrenomFact', max_length=50)  # Field name made lowercase.
    courrielfact = models.CharField(db_column='CourrielFact', max_length=50)  # Field name made lowercase.
    groupe = models.CharField(max_length=6)
    maj = models.DateTimeField(db_column='MAJ')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'contact'


class Devise(models.Model):
    deviseid = models.AutoField(db_column='DeviseID', primary_key=True)  # Field name made lowercase.
    devise = models.CharField(db_column='Devise', max_length=5, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'devise'


class Editeur(models.Model):
    editeurid = models.IntegerField(db_column='EditeurID', primary_key=True)  # Field name made lowercase.
    revueid = models.ForeignKey('Revue', db_column='RevueID')  # Field name made lowercase.
    editeur = models.CharField(db_column='Editeur', max_length=200)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'editeur'


class Facture(models.Model):
    factureid = models.AutoField(db_column='FactureID', primary_key=True)  # Field name made lowercase.
    nofacture = models.CharField(max_length=45)
    prixavanttaxe = models.DecimalField(db_column='PrixAvantTaxe', max_digits=19, decimal_places=2)  # Field name made lowercase.
    prixaprestaxe = models.DecimalField(db_column='PrixAprestaxe', max_digits=19, decimal_places=2)  # Field name made lowercase.
    abonneid = models.IntegerField(db_column='AbonneID')  # Field name made lowercase.
    commandeid = models.IntegerField()
    datefacturation = models.DateField(db_column='DateFacturation')  # Field name made lowercase.
    sommerecue = models.DecimalField(db_column='SommeRecue', max_digits=19, decimal_places=2)  # Field name made lowercase.
    solde = models.DecimalField(db_column='Solde', max_digits=19, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    nocheque = models.CharField(db_column='NoCheque', max_length=45, blank=True, null=True)  # Field name made lowercase.
    regle = models.IntegerField(db_column='Regle')  # Field name made lowercase.
    datemaj = models.DateTimeField(db_column='DateMAJ')  # Field name made lowercase.
    notes = models.CharField(db_column='Notes', max_length=120, blank=True, null=True)  # Field name made lowercase.
    maj = models.DateTimeField(db_column='MAJ')  # Field name made lowercase.
    deviseid = models.IntegerField(db_column='DeviseID')  # Field name made lowercase.
    prorate = models.IntegerField(db_column='Prorate')  # Field name made lowercase.
    gratuit = models.IntegerField(db_column='Gratuit')  # Field name made lowercase.
    tpsexclure = models.IntegerField(db_column='TPSExclure')  # Field name made lowercase.
    tvqexclure = models.IntegerField(db_column='TVQExclure')  # Field name made lowercase.
    tauxtaxeid = models.IntegerField(db_column='TauxTaxeID', blank=True, null=True)  # Field name made lowercase.
    datedepot = models.DateField(db_column='DateDepot', blank=True, null=True)  # Field name made lowercase.
    tps = models.FloatField(db_column='TPS', blank=True, null=True)  # Field name made lowercase.
    tvq = models.FloatField(db_column='TVQ', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'facture'


class Historique(models.Model):
    historiqueid = models.AutoField(db_column='HistoriqueID', primary_key=True)  # Field name made lowercase.
    historiquedescription = models.CharField(db_column='HistoriqueDescription', max_length=100)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'historique'


class Historiquerevue(models.Model):
    historiqueid = models.ForeignKey(Historique, db_column='HistoriqueID')  # Field name made lowercase.
    revueid = models.ForeignKey('Revue', db_column='RevueID')  # Field name made lowercase.
    ordre = models.SmallIntegerField(db_column='Ordre')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'historiquerevue'
        unique_together = (('historiqueid', 'revueid'),)


class Individu(models.Model):
    individuid = models.AutoField(db_column='IndividuID', primary_key=True)  # Field name made lowercase.
    nomfamille = models.CharField(db_column='NomFamille', max_length=75, blank=True, null=True)  # Field name made lowercase.
    prenom = models.CharField(db_column='Prenom', max_length=50, blank=True, null=True)  # Field name made lowercase.
    maj = models.DateTimeField(db_column='MAJ')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'individu'


class Intip(models.Model):
    intipid = models.AutoField(db_column='intipID', primary_key=True)  # Field name made lowercase.
    debutint = models.CharField(max_length=15)
    finint = models.CharField(max_length=15)
    abonneid = models.IntegerField(db_column='AbonneID')  # Field name made lowercase.
    maj = models.DateTimeField(db_column='MAJ')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'intip'


class Ls(models.Model):
    ls_revueabonneid = models.AutoField(db_column='LS_RevueAbonneID', primary_key=True)  # Field name made lowercase.
    ls_revueid = models.IntegerField(db_column='LS_RevueID', blank=True, null=True)  # Field name made lowercase.
    ls_abonneid = models.IntegerField(db_column='LS_AbonneID', blank=True, null=True)  # Field name made lowercase.
    ls_annneeabonnement = models.TextField(db_column='LS_AnnneeAbonnement', blank=True, null=True)  # Field name made lowercase. This field type is a guess.
    ls_commandeid = models.IntegerField(db_column='LS_CommandeID', blank=True, null=True)  # Field name made lowercase.
    maj = models.DateTimeField(db_column='MAJ')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'ls'


class Paiement(models.Model):
    paiementid = models.AutoField(db_column='PaiementID', primary_key=True)  # Field name made lowercase.
    abonneid = models.ForeignKey(Abonne, db_column='AbonneID', blank=True, null=True)  # Field name made lowercase.
    commandeid = models.IntegerField(db_column='CommandeID', blank=True, null=True)  # Field name made lowercase.
    anneeabonnement = models.CharField(db_column='AnneeAbonnement', max_length=4)  # Field name made lowercase.
    daterecue = models.DateField(db_column='DateRecue')  # Field name made lowercase.
    paiementfait = models.IntegerField(db_column='PaiementFait')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'paiement'


class Panier(models.Model):
    panierid = models.AutoField(db_column='PanierID', primary_key=True)  # Field name made lowercase.
    description = models.CharField(db_column='Description', max_length=75)  # Field name made lowercase.
    dateapplication = models.DateTimeField(db_column='DateApplication')  # Field name made lowercase.
    consortium = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'panier'


class Panierrevue(models.Model):
    panierrevueid = models.AutoField(db_column='PanierRevueID', primary_key=True)  # Field name made lowercase.
    panierid = models.IntegerField(db_column='PanierID', blank=True, null=True)  # Field name made lowercase.
    revueid = models.IntegerField(db_column='RevueID')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'panierrevue'


class Pays(models.Model):
    paysid = models.AutoField(db_column='PaysID', primary_key=True)  # Field name made lowercase.
    pays = models.CharField(db_column='Pays', max_length=50, blank=True, null=True)  # Field name made lowercase.
    code = models.CharField(db_column='Code', max_length=50, blank=True, null=True)  # Field name made lowercase.
    langue = models.CharField(db_column='Langue', max_length=2, blank=True, null=True)  # Field name made lowercase.
    devise = models.CharField(db_column='Devise', max_length=6)  # Field name made lowercase.
    maj = models.DateTimeField(db_column='MAJ')  # Field name made lowercase.
    paysanglais = models.CharField(db_column='PaysAnglais', max_length=50, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'pays'


class Prixrevue(models.Model):
    prixpanierid = models.AutoField(db_column='prixpanierID', primary_key=True)  # Field name made lowercase.
    revueid = models.IntegerField()
    prix = models.DecimalField(max_digits=19, decimal_places=2, blank=True, null=True)
    panierid = models.IntegerField()
    reglecalcul = models.IntegerField()
    annee = models.TextField()  # This field type is a guess.
    consortiumid = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'prixrevue'


class Provetetat(models.Model):
    provetatid = models.AutoField(db_column='ProvEtatID', primary_key=True)  # Field name made lowercase.
    provetat = models.CharField(db_column='ProvEtat', max_length=50, blank=True, null=True)  # Field name made lowercase.
    codealpha = models.CharField(db_column='CodeAlpha', max_length=2, blank=True, null=True)  # Field name made lowercase.
    abreviation = models.CharField(db_column='Abreviation', max_length=50, blank=True, null=True)  # Field name made lowercase.
    code = models.IntegerField(db_column='Code', blank=True, null=True)  # Field name made lowercase.
    maj = models.DateTimeField(db_column='MAJ')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'provetetat'


class Rapport2007(models.Model):
    rapport2007id = models.AutoField(db_column='Rapport2007ID', primary_key=True)  # Field name made lowercase.
    abonne = models.CharField(db_column='Abonne', max_length=145)  # Field name made lowercase.
    daterecue = models.DateTimeField(db_column='DateRecue')  # Field name made lowercase.
    typeabonnement = models.CharField(db_column='TypeAbonnement', max_length=15)  # Field name made lowercase.
    prorata = models.IntegerField(db_column='Prorata')  # Field name made lowercase.
    prixitem = models.DecimalField(db_column='PrixItem', max_digits=19, decimal_places=2)  # Field name made lowercase.
    tarifprorata = models.DecimalField(db_column='TarifProrata', max_digits=19, decimal_places=2)  # Field name made lowercase.
    escompte = models.IntegerField(db_column='Escompte')  # Field name made lowercase.
    prixpaye = models.DecimalField(db_column='PrixPaye', max_digits=19, decimal_places=2)  # Field name made lowercase.
    revue = models.CharField(db_column='Revue', max_length=175)  # Field name made lowercase.
    periode = models.CharField(db_column='Periode', max_length=75)  # Field name made lowercase.
    anneeabonnement = models.IntegerField(db_column='AnneeAbonnement')  # Field name made lowercase.
    revueid = models.IntegerField(db_column='RevueID')  # Field name made lowercase.
    abonneid = models.IntegerField(db_column='AbonneID')  # Field name made lowercase.
    commandeid = models.IntegerField(db_column='CommandeID')  # Field name made lowercase.
    deviseid = models.IntegerField(db_column='DeviseID')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'rapport2007'


class Rapport2008(models.Model):
    rapport2008id = models.AutoField(db_column='Rapport2008ID', primary_key=True)  # Field name made lowercase.
    abonne = models.CharField(db_column='Abonne', max_length=145)  # Field name made lowercase.
    daterecue = models.DateTimeField(db_column='DateRecue')  # Field name made lowercase.
    typeabonnement = models.CharField(db_column='TypeAbonnement', max_length=15)  # Field name made lowercase.
    prorata = models.IntegerField(db_column='Prorata')  # Field name made lowercase.
    prixitem = models.DecimalField(db_column='PrixItem', max_digits=19, decimal_places=2)  # Field name made lowercase.
    tarifprorata = models.DecimalField(db_column='TarifProrata', max_digits=19, decimal_places=2)  # Field name made lowercase.
    escompte = models.IntegerField(db_column='Escompte')  # Field name made lowercase.
    prixpaye = models.DecimalField(db_column='PrixPaye', max_digits=19, decimal_places=2)  # Field name made lowercase.
    revue = models.CharField(db_column='Revue', max_length=175)  # Field name made lowercase.
    periode = models.CharField(db_column='Periode', max_length=75)  # Field name made lowercase.
    anneeabonnement = models.IntegerField(db_column='AnneeAbonnement', blank=True, null=True)  # Field name made lowercase.
    revueid = models.IntegerField(db_column='RevueID')  # Field name made lowercase.
    abonneid = models.IntegerField(db_column='AbonneID')  # Field name made lowercase.
    commandeid = models.IntegerField(db_column='CommandeID')  # Field name made lowercase.
    deviseid = models.IntegerField(db_column='DeviseID')  # Field name made lowercase.
    prixcan = models.DecimalField(db_column='PrixCan', max_digits=19, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    tauxchange = models.DecimalField(db_column='TauxChange', max_digits=19, decimal_places=8)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'rapport2008'


class Rapport2009(models.Model):
    rapport2009id = models.AutoField(db_column='Rapport2009ID', primary_key=True)  # Field name made lowercase.
    abonne = models.CharField(db_column='Abonne', max_length=145)  # Field name made lowercase.
    daterecue = models.DateTimeField(db_column='DateRecue')  # Field name made lowercase.
    typeabonnement = models.CharField(db_column='TypeAbonnement', max_length=15)  # Field name made lowercase.
    prorata = models.IntegerField(db_column='Prorata')  # Field name made lowercase.
    prixitem = models.DecimalField(db_column='PrixItem', max_digits=19, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    tarifprorata = models.DecimalField(db_column='TarifProrata', max_digits=19, decimal_places=2)  # Field name made lowercase.
    escompte = models.IntegerField(db_column='Escompte')  # Field name made lowercase.
    prixpaye = models.DecimalField(db_column='PrixPaye', max_digits=19, decimal_places=2)  # Field name made lowercase.
    revue = models.CharField(db_column='Revue', max_length=175)  # Field name made lowercase.
    periode = models.CharField(db_column='Periode', max_length=75)  # Field name made lowercase.
    anneeabonnement = models.IntegerField(db_column='AnneeAbonnement', blank=True, null=True)  # Field name made lowercase.
    revueid = models.IntegerField(db_column='RevueID')  # Field name made lowercase.
    abonneid = models.IntegerField(db_column='AbonneID')  # Field name made lowercase.
    commandeid = models.IntegerField(db_column='CommandeID')  # Field name made lowercase.
    deviseid = models.IntegerField(db_column='DeviseID')  # Field name made lowercase.
    prixcan = models.DecimalField(db_column='PrixCan', max_digits=19, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    tauxchange = models.DecimalField(db_column='TauxChange', max_digits=19, decimal_places=8)  # Field name made lowercase.
    prixpayefacture = models.DecimalField(db_column='PrixPayeFacture', max_digits=19, decimal_places=2)  # Field name made lowercase.
    transfere = models.IntegerField(db_column='Transfere')  # Field name made lowercase.
    paiementfait = models.IntegerField(db_column='PaiementFait', blank=True, null=True)  # Field name made lowercase.
    consortiumid = models.IntegerField(db_column='ConsortiumID')  # Field name made lowercase.
    escompteconsortium = models.IntegerField(db_column='EscompteConsortium')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'rapport2009'


class Rapport2010(models.Model):
    rapport2010id = models.AutoField(db_column='Rapport2010ID', primary_key=True)  # Field name made lowercase.
    abonne = models.CharField(db_column='Abonne', max_length=145)  # Field name made lowercase.
    daterecue = models.DateTimeField(db_column='DateRecue')  # Field name made lowercase.
    typeabonnement = models.CharField(db_column='TypeAbonnement', max_length=15)  # Field name made lowercase.
    prorata = models.IntegerField(db_column='Prorata')  # Field name made lowercase.
    prixitem = models.DecimalField(db_column='PrixItem', max_digits=19, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    tarifprorata = models.DecimalField(db_column='TarifProrata', max_digits=19, decimal_places=2)  # Field name made lowercase.
    escompte = models.IntegerField(db_column='Escompte')  # Field name made lowercase.
    prixpaye = models.DecimalField(db_column='PrixPaye', max_digits=19, decimal_places=2)  # Field name made lowercase.
    revue = models.CharField(db_column='Revue', max_length=175)  # Field name made lowercase.
    periode = models.CharField(db_column='Periode', max_length=75)  # Field name made lowercase.
    anneeabonnement = models.IntegerField(db_column='AnneeAbonnement', blank=True, null=True)  # Field name made lowercase.
    revueid = models.IntegerField(db_column='RevueID')  # Field name made lowercase.
    abonneid = models.IntegerField(db_column='AbonneID')  # Field name made lowercase.
    commandeid = models.IntegerField(db_column='CommandeID')  # Field name made lowercase.
    deviseid = models.IntegerField(db_column='DeviseID')  # Field name made lowercase.
    prixcan = models.DecimalField(db_column='PrixCan', max_digits=19, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    tauxchange = models.DecimalField(db_column='TauxChange', max_digits=19, decimal_places=8)  # Field name made lowercase.
    prixpayefacture = models.DecimalField(db_column='PrixPayeFacture', max_digits=19, decimal_places=2)  # Field name made lowercase.
    transfere = models.IntegerField(db_column='Transfere')  # Field name made lowercase.
    paiementfait = models.IntegerField(db_column='PaiementFait', blank=True, null=True)  # Field name made lowercase.
    consortiumid = models.IntegerField(db_column='ConsortiumID')  # Field name made lowercase.
    escompteconsortium = models.IntegerField(db_column='EscompteConsortium')  # Field name made lowercase.
    quantite = models.IntegerField(db_column='Quantite')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'rapport2010'


class Rapport2011(models.Model):
    rapport2011id = models.AutoField(db_column='Rapport2011ID', primary_key=True)  # Field name made lowercase.
    abonne = models.CharField(db_column='Abonne', max_length=145)  # Field name made lowercase.
    daterecue = models.DateTimeField(db_column='DateRecue')  # Field name made lowercase.
    typeabonnement = models.CharField(db_column='TypeAbonnement', max_length=15)  # Field name made lowercase.
    prorata = models.IntegerField(db_column='Prorata')  # Field name made lowercase.
    prixitem = models.DecimalField(db_column='PrixItem', max_digits=19, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    tarifprorata = models.DecimalField(db_column='TarifProrata', max_digits=19, decimal_places=2)  # Field name made lowercase.
    escompte = models.IntegerField(db_column='Escompte')  # Field name made lowercase.
    prixpaye = models.DecimalField(db_column='PrixPaye', max_digits=19, decimal_places=2)  # Field name made lowercase.
    revue = models.CharField(db_column='Revue', max_length=175)  # Field name made lowercase.
    periode = models.CharField(db_column='Periode', max_length=75)  # Field name made lowercase.
    anneeabonnement = models.IntegerField(db_column='AnneeAbonnement', blank=True, null=True)  # Field name made lowercase.
    revueid = models.IntegerField(db_column='RevueID')  # Field name made lowercase.
    abonneid = models.IntegerField(db_column='AbonneID')  # Field name made lowercase.
    commandeid = models.IntegerField(db_column='CommandeID')  # Field name made lowercase.
    deviseid = models.IntegerField(db_column='DeviseID')  # Field name made lowercase.
    prixcan = models.DecimalField(db_column='PrixCan', max_digits=19, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    tauxchange = models.DecimalField(db_column='TauxChange', max_digits=19, decimal_places=8)  # Field name made lowercase.
    prixpayefacture = models.DecimalField(db_column='PrixPayeFacture', max_digits=19, decimal_places=2)  # Field name made lowercase.
    transfere = models.IntegerField(db_column='Transfere')  # Field name made lowercase.
    paiementfait = models.IntegerField(db_column='PaiementFait', blank=True, null=True)  # Field name made lowercase.
    consortiumid = models.IntegerField(db_column='ConsortiumID')  # Field name made lowercase.
    escompteconsortium = models.IntegerField(db_column='EscompteConsortium')  # Field name made lowercase.
    quantite = models.IntegerField(db_column='Quantite')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'rapport2011'


class Rapportconsolide(models.Model):
    rapportconsolideid = models.AutoField(db_column='RapportConsolideID', primary_key=True)  # Field name made lowercase.
    abonne = models.CharField(max_length=145)
    titrerev = models.CharField(max_length=145)
    daterecue = models.DateTimeField()
    panier = models.IntegerField()
    prorata = models.IntegerField()
    pourcentage = models.IntegerField()
    prixitem = models.DecimalField(max_digits=19, decimal_places=2)
    reglecalcul = models.IntegerField()
    revueid = models.IntegerField()
    clerapport = models.CharField(max_length=45)
    motpasse = models.CharField(max_length=30)
    abonneid = models.IntegerField()
    prixpaye = models.DecimalField(max_digits=19, decimal_places=2)
    anneeabonnement = models.IntegerField()
    regle = models.IntegerField()
    gratuit = models.IntegerField()
    commandeid = models.IntegerField()
    deviseid = models.IntegerField()
    tauxchange = models.DecimalField(max_digits=19, decimal_places=8)

    class Meta:
        managed = False
        db_table = 'rapportconsolide'


class Rapportjuinseptembre2008(models.Model):
    rapportjuinseptembre2008id = models.AutoField(db_column='RapportJuinSeptembre2008ID', primary_key=True)  # Field name made lowercase.
    abonne = models.CharField(db_column='Abonne', max_length=145)  # Field name made lowercase.
    daterecue = models.DateTimeField(db_column='DateRecue')  # Field name made lowercase.
    typeabonnement = models.IntegerField(db_column='TypeAbonnement')  # Field name made lowercase.
    prorata = models.IntegerField(db_column='Prorata')  # Field name made lowercase.
    prix = models.DecimalField(db_column='Prix', max_digits=19, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    prixitem = models.DecimalField(db_column='PrixItem', max_digits=19, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    pourcentage = models.IntegerField(db_column='Pourcentage')  # Field name made lowercase.
    prixpaye = models.DecimalField(db_column='PrixPaye', max_digits=19, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    reglecalcul = models.IntegerField(db_column='RegleCalcul')  # Field name made lowercase.
    titrerev = models.CharField(db_column='Titrerev', max_length=145)  # Field name made lowercase.
    consortiumid = models.IntegerField(db_column='ConsortiumID')  # Field name made lowercase.
    anneeabonnement = models.IntegerField(db_column='AnneeAbonnement')  # Field name made lowercase.
    revueid = models.IntegerField(db_column='RevueID')  # Field name made lowercase.
    commandeid = models.IntegerField(db_column='CommandeID')  # Field name made lowercase.
    tauxchange = models.DecimalField(db_column='TauxChange', max_digits=19, decimal_places=8)  # Field name made lowercase.
    deviseid = models.IntegerField(db_column='DeviseID')  # Field name made lowercase.
    prixprorata = models.DecimalField(db_column='Prixprorata', max_digits=19, decimal_places=2)  # Field name made lowercase.
    notes = models.CharField(db_column='Notes', max_length=45, blank=True, null=True)  # Field name made lowercase.
    escompteconsortium = models.IntegerField(db_column='EscompteConsortium')  # Field name made lowercase.
    region = models.IntegerField(db_column='Region')  # Field name made lowercase.
    clerapport = models.CharField(db_column='CleRapport', max_length=45)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'rapportjuinseptembre2008'


class Revenus(models.Model):
    revueid = models.IntegerField()
    abonneid = models.IntegerField()
    pourcentage = models.IntegerField()
    prorata = models.IntegerField()
    tarifprorata = models.DecimalField(max_digits=19, decimal_places=4)
    prixpaye = models.DecimalField(max_digits=19, decimal_places=2)
    tauxchange = models.DecimalField(max_digits=19, decimal_places=8)
    devise = models.IntegerField()
    commandeid = models.IntegerField()
    revueabonneid = models.IntegerField()
    trimestre = models.IntegerField()
    revenusid = models.AutoField(primary_key=True)
    service = models.DecimalField(max_digits=19, decimal_places=4)
    typeabonnement = models.CharField(max_length=10)
    regle = models.IntegerField()
    dateabonnement = models.DateField()
    mois = models.IntegerField()
    nonregleavant = models.IntegerField()
    anneeabonnement = models.TextField()  # This field type is a guess.
    anneepaiement = models.TextField()  # This field type is a guess.
    consortiumid = models.IntegerField(db_column='ConsortiumID')  # Field name made lowercase.
    complete = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'revenus'


class Revenus2008(models.Model):
    revenus2008id = models.AutoField(db_column='Revenus2008ID', primary_key=True)  # Field name made lowercase.
    abonneid = models.IntegerField(blank=True, null=True)
    commandeid = models.IntegerField()
    revueid = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'revenus2008'


class Revue(models.Model):
    revueid = models.AutoField(db_column='RevueID', primary_key=True)  # Field name made lowercase.
    titrerev = models.CharField(max_length=150, blank=True, null=True)
    periodiciteid = models.IntegerField(db_column='PeriodiciteID', blank=True, null=True)  # Field name made lowercase.
    nombrenoannuel = models.IntegerField(db_column='NombreNoAnnuel', blank=True, null=True)  # Field name made lowercase.
    prix = models.DecimalField(db_column='Prix', max_digits=19, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    debutanneerestricti = models.IntegerField(db_column='DebutAnneeRestricti', blank=True, null=True)  # Field name made lowercase.
    finanneerestriction = models.IntegerField(db_column='FinAnneeRestriction', blank=True, null=True)  # Field name made lowercase.
    titrerevabr = models.CharField(max_length=50, blank=True, null=True)
    gratuit = models.IntegerField(blank=True, null=True)
    maj = models.DateTimeField(db_column='MAJ')  # Field name made lowercase.
    exclure = models.IntegerField(db_column='Exclure')  # Field name made lowercase.
    clerapport = models.CharField(db_column='cleRapport', max_length=45)  # Field name made lowercase.
    prixsuivante = models.DecimalField(db_column='PrixSuivante', max_digits=19, decimal_places=4)  # Field name made lowercase.
    retire = models.IntegerField(db_column='Retire')  # Field name made lowercase.
    aparaitre = models.IntegerField(db_column='Aparaitre')  # Field name made lowercase.
    motpasse = models.CharField(max_length=30)
    lettre = models.CharField(max_length=1)
    logo = models.CharField(max_length=20)

    class Meta:
        managed = False
        db_table = 'revue'

    def __str__(self):
        return '{} {}'.format(self.revueid, self.titrerev)


class Revueabonne(models.Model):
    revueabonneid = models.AutoField(db_column='RevueAbonneID', primary_key=True)  # Field name made lowercase.
    revueid = models.ForeignKey(Revue, db_column='RevueID', blank=True, null=True)  # Field name made lowercase.
    abonneid = models.ForeignKey(Abonne, db_column='AbonneID', blank=True, null=True)  # Field name made lowercase.
    anneeabonnement = models.TextField(db_column='AnneeAbonnement')  # Field name made lowercase. This field type is a guess.
    commandeid = models.IntegerField()
    maj = models.DateTimeField(db_column='MAJ')  # Field name made lowercase.
    exclure = models.IntegerField(db_column='Exclure')  # Field name made lowercase.
    prixitem = models.DecimalField(db_column='PrixItem', max_digits=19, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    reglecalcul = models.IntegerField(db_column='RegleCalcul')  # Field name made lowercase.
    quantite = models.IntegerField(db_column='Quantite')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'revueabonne'


class Revuefiltre(models.Model):
    revuefiltreid = models.AutoField(db_column='revuefiltreID', primary_key=True)  # Field name made lowercase.
    nomabrege = models.CharField(max_length=20)
    volume = models.IntegerField(blank=True, null=True)
    nonumero = models.IntegerField()
    nonumerodouble = models.IntegerField(blank=True, null=True)
    annee = models.TextField()  # This field type is a guess.
    exceptionnonumerodouble = models.CharField(max_length=45)
    filtre = models.IntegerField(db_column='Filtre')  # Field name made lowercase.
    revueid = models.IntegerField()
    maj = models.DateTimeField(db_column='MAJ')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'revuefiltre'


class Revueindividus(models.Model):
    abonneindividusid = models.ForeignKey(Abonneindividus, db_column='abonneIndividusID')  # Field name made lowercase.
    revueid = models.ForeignKey(Revue, db_column='revueID')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'revueindividus'
        unique_together = (('abonneindividusid', 'revueid'),)


class Tauxchange(models.Model):
    tauxchangeid = models.AutoField(primary_key=True)
    taux = models.DecimalField(max_digits=19, decimal_places=8)
    devise = models.IntegerField()
    mois = models.IntegerField()
    annee = models.IntegerField()
    trimestre = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'tauxchange'


class Tauxtaxe(models.Model):
    tauxtaxeid = models.AutoField(db_column='TauxTaxeID', primary_key=True)  # Field name made lowercase.
    tps = models.DecimalField(db_column='TPS', max_digits=10, decimal_places=5)  # Field name made lowercase.
    tvq = models.DecimalField(db_column='TVQ', max_digits=10, decimal_places=5)  # Field name made lowercase.
    description = models.CharField(db_column='Description', max_length=45)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tauxtaxe'


class Tauxtaxeequisoft(models.Model):
    tauxtaxeidequisoft = models.AutoField(db_column='TauxTaxeIDEquisoft', primary_key=True)  # Field name made lowercase.
    description = models.CharField(db_column='Description', max_length=45)  # Field name made lowercase.
    tauxtps = models.FloatField(db_column='TauxTPS')  # Field name made lowercase.
    tauxtvq = models.FloatField(db_column='TauxTVQ')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'tauxtaxeequisoft'


class Telephone(models.Model):
    telephoneid = models.AutoField(db_column='TelephoneID', primary_key=True)  # Field name made lowercase.
    telephone = models.CharField(db_column='Telephone', max_length=50, blank=True, null=True)  # Field name made lowercase.
    typetelephoneid = models.IntegerField(db_column='TypeTelephoneID', blank=True, null=True)  # Field name made lowercase.
    maj = models.DateTimeField(db_column='MAJ')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'telephone'


class Typeabonnement(models.Model):
    typeabonnementid = models.AutoField(db_column='TypeAbonnementID', primary_key=True)  # Field name made lowercase.
    typeabonnement = models.CharField(db_column='TypeAbonnement', max_length=50, blank=True, null=True)  # Field name made lowercase.
    prix = models.DecimalField(db_column='Prix', max_digits=20, decimal_places=4, blank=True, null=True)  # Field name made lowercase.
    maj = models.DateTimeField(db_column='MAJ')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'typeabonnement'


class Typeadresse(models.Model):
    typeadresseid = models.AutoField(db_column='TypeAdresseID', primary_key=True)  # Field name made lowercase.
    typeadresse = models.CharField(db_column='TypeAdresse', max_length=50, blank=True, null=True)  # Field name made lowercase.
    maj = models.DateTimeField(db_column='MAJ')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'typeadresse'


class Typecontact(models.Model):
    typecontactid = models.AutoField(db_column='TypeContactID', primary_key=True)  # Field name made lowercase.
    typecontact = models.CharField(db_column='TypeContact', max_length=50, blank=True, null=True)  # Field name made lowercase.
    maj = models.DateTimeField(db_column='MAJ')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'typecontact'


class Typetelephone(models.Model):
    typetelephoneid = models.AutoField(db_column='TypeTelephoneID', primary_key=True)  # Field name made lowercase.
    typetelephone = models.CharField(db_column='TypeTelephone', max_length=50, blank=True, null=True)  # Field name made lowercase.
    maj = models.DateTimeField(db_column='MAJ')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'typetelephone'


class Urlrapportrevenus(models.Model):
    urlrapportrevenusid = models.AutoField(db_column='urlrapportrevenusID', primary_key=True)  # Field name made lowercase.
    revueid = models.IntegerField()
    clerapport = models.CharField(max_length=45)
    trimestre = models.CharField(max_length=4)
    devise = models.CharField(max_length=5)
    mimetype = models.CharField(max_length=5)
    annee = models.CharField(max_length=4)
    disponible = models.IntegerField()
    trimestretexte = models.CharField(db_column='trimestreTexte', max_length=45)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'urlrapportrevenus'


class Valeurdefaut(models.Model):
    valeurdefautid = models.AutoField(db_column='ValeurDefautID', primary_key=True)  # Field name made lowercase.
    anneeabonnement = models.TextField(db_column='AnneeAbonnement')  # Field name made lowercase. This field type is a guess.
    tps = models.DecimalField(db_column='TPS', max_digits=6, decimal_places=1)  # Field name made lowercase.
    tvq = models.DecimalField(db_column='TVQ', max_digits=6, decimal_places=1)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'valeurdefaut'
