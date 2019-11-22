from datetime import datetime as dt
import random
import factory
import factory.fuzzy

from ..models import Abonne, Revue, Revueabonne, Ipabonne, Adressesip


class IpabonneFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Ipabonne

    ip = ".".join(map(str, (random.randint(0, 255) for _ in range(4))))
    abonneid = factory.fuzzy.FuzzyText()
    id = factory.Sequence(lambda n: str(n))


class AbonneFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = Abonne

    courriel = factory.fuzzy.FuzzyText()
    abonne = factory.fuzzy.FuzzyText()
    abonneid = factory.Sequence(lambda n: str(n))


class RevueFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = Revue

    titrerevabr = factory.fuzzy.FuzzyText()
    revueid = factory.Sequence(lambda n: str(n))


class RevueabonneFactory(factory.django.DjangoModelFactory):

    anneeabonnement = dt.now().year

    class Meta:
        model = Revueabonne


class AdressesipFactory(factory.django.DjangoModelFactory):

    adresseipid = factory.Sequence(lambda n: int(n))

    class Meta:
        model = Adressesip
