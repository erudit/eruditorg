from datetime import datetime as dt
import factory
import factory.fuzzy

from ..models import Abonne, Revue, Revueabonne


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
