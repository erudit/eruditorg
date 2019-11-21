import pytest

from apps.webservices.views import CrknIpUnbView
from core.subscription.restriction.test.factories import (
    AbonneFactory,
    AdressesipFactory,
    RevueabonneFactory,
    RevueFactory,
)
from erudit.test.factories import JournalFactory


@pytest.mark.django_db
class TestCrknIpUnbView:

    def test_get_context_data(self):
        # UNB journal
        JournalFactory(code='unb_journal', collection__code='unb')
        RevueFactory(revueid='1', titrerevabr='unb_journal')

        # Non-UNB journal
        JournalFactory(code='erudit_journal', collection__code='erudit')
        RevueFactory(revueid='2', titrerevabr='erudit_journal')

        # Valid UNB subscribers
        RevueabonneFactory(revueid='1', abonneid='1', anneeabonnement='2019')
        AbonneFactory(abonneid='1', abonne='Abonné UNB 1')
        AdressesipFactory(abonneid='1', ip='0.0.0.1')
        AdressesipFactory(abonneid='1', ip='1.1.1.*')
        RevueabonneFactory(revueid='1', abonneid='2', anneeabonnement='2019')
        AbonneFactory(abonneid='2', abonne='Abonné UNB 2')
        AdressesipFactory(abonneid='2', ip='0.0.0.2')
        AdressesipFactory(abonneid='2', ip='2.2.2.*')

        # Non-UNB subscriber
        RevueabonneFactory(revueid='2', abonneid='3', anneeabonnement='2019')
        AbonneFactory(abonneid='3', abonne='Abonné UNB 3')
        AdressesipFactory(abonneid='3', ip='3.3.3.3')

        # Invalid UNB subscriber
        RevueabonneFactory(revueid='1', abonneid='1', anneeabonnement='2018')
        AbonneFactory(abonneid='4', abonne='Abonné Érudit')
        AdressesipFactory(abonneid='4', ip='4.4.4.4')

        view = CrknIpUnbView()
        context = view.get_context_data()
        assert context['listeips'] == {
            1: {
                'abonne': 'Abonné UNB 1',
                'ips': [
                    '0.0.0.1',
                    '1.1.1.*',
                ],
            },
            2: {
                'abonne': 'Abonné UNB 2',
                'ips': [
                    '0.0.0.2',
                    '2.2.2.*',
                ],
            },
        }
