# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table  # noqa
# Feel free to rename the models, but don't rename db_table values or field names.
#
# Also note: You'll have to insert the output of 'django-admin sqlcustom [app_label]'
# into your database.

from django.db import models
from django.conf import settings

# The MANAGED const is set to True when testing so that we have a DB schema to put or test models
# in it.
MANAGED = getattr(settings, "RESTRICTION_MODELS_ARE_MANAGED", False)


class Abonne(models.Model):
    abonneid = models.AutoField(primary_key=True)
    activer = models.CharField(max_length=45, blank=True, null=True)
    abonne = models.CharField(max_length=300, blank=True, null=True)
    icone = models.CharField(max_length=256, blank=True, null=True)
    referer = models.CharField(max_length=256, blank=True, null=True)
    courriel = models.CharField(max_length=256, blank=True, null=True)
    motdepasse = models.CharField(max_length=45, blank=True, null=True)
    requesterid = models.CharField(
        db_column="requesterID", max_length=45, blank=True, null=True
    )  # Field name made lowercase.  # noqa
    privilegeid = models.IntegerField(
        db_column="privilegeId", blank=True, null=True
    )  # Field name made lowercase.  # noqa

    class Meta:
        managed = MANAGED
        db_table = "abonne"
        app_label = "restriction"


class Adressesip(models.Model):
    adresseipid = models.BigIntegerField(
        db_column="adresseIPID", primary_key=True
    )  # Field name made lowercase.  # noqa
    abonneid = models.IntegerField(
        db_column="AbonneID", blank=True, null=True
    )  # Field name made lowercase.  # noqa
    ip = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = MANAGED
        db_table = "adressesip"
        app_label = "restriction"


class Ipabonne(models.Model):
    ip = models.CharField(max_length=20)
    abonneid = models.CharField(max_length=45)

    class Meta:
        managed = MANAGED
        db_table = "ipabonne"
        app_label = "restriction"


class Ipabonneinterval(models.Model):
    debutinterval = models.CharField(max_length=45)
    fininterval = models.CharField(max_length=45)
    abonneid = models.IntegerField()

    class Meta:
        managed = MANAGED
        db_table = "ipabonneinterval"
        app_label = "restriction"


class Privilege(models.Model):
    libelle = models.CharField(max_length=10)

    class Meta:
        managed = MANAGED
        db_table = "privilege"
        app_label = "restriction"


class Ressource(models.Model):
    libelle = models.CharField(max_length=50)
    typeressource = models.CharField(
        db_column="typeRessource", max_length=10, blank=True, null=True
    )  # Field name made lowercase.  # noqa
    path = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = MANAGED
        db_table = "ressource"
        app_label = "restriction"


class Ressourceprivilege(models.Model):
    privilegeid = models.IntegerField(db_column="privilegeId")  # Field name made lowercase.
    ressourceid = models.IntegerField(db_column="ressourceId")  # Field name made lowercase.

    class Meta:
        managed = MANAGED
        db_table = "ressourceprivilege"
        unique_together = (("privilegeid", "ressourceid"),)
        app_label = "restriction"


class Revue(models.Model):
    titrerevabr = models.CharField(primary_key=True, max_length=20)
    revueid = models.CharField(max_length=45)
    revue = models.CharField(max_length=45, blank=True, null=True)

    class Meta:
        managed = MANAGED
        db_table = "revue"
        app_label = "restriction"


class Revueabonne(models.Model):
    abonneid = models.IntegerField()
    revueid = models.IntegerField()
    anneeabonnement = models.IntegerField(db_column="anneeAbonnement")  # Field name made lowercase.

    class Meta:
        managed = MANAGED
        db_table = "revueabonne"
        app_label = "restriction"
