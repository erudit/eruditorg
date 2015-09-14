from django.db import models
from erudit import models as e


class SubscriptionPrice(models.Model):
    """Tarif d'abonnement"""

    journal
    zone
    type # individual, organisation ?

    price
    currency
    year
    #date_start
    #date_end

    approved
    date_approved

class SubscriptionPriceType(models.Model):
    name

class SubscriptionPriceModificationNotice(models.Model):
    """Avis de modification de tarif d'abonnement"""

    subscription_price
    date_sent

class SubscriptionZone(models.Model):
    """Zone d'abonnement"""
    # {UE, CA, other}

class Subscription(models.Model):

    person | organisation
    journal
    subscription_price

class IndividualSubscription(models.Model):

class OrganisationalSubscription(models.Model):


class Basket(models.Model):
    """Panier"""

    # {all, sc_soc, sc_hum, discovery, legal}
    code
    name
    journals

