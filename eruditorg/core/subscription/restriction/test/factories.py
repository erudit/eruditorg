import factory
import factory.fuzzy

from ..models import Abonne, Revue, Revueabonne


class AbonneFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = Abonne

    courriel = factory.fuzzy.FuzzyText()
    abonne = factory.fuzzy.FuzzyText()


class RevueFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = Revue

    titrerevabr = factory.fuzzy.FuzzyText()
    revueid = factory.Sequence(lambda n: str(n))


class RevueabonneFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = Revueabonne
