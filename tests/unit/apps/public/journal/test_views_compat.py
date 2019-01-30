import os
import pytest
import unittest.mock

from django.http import Http404

from erudit.test.factories import JournalFactory, IssueFactory
from apps.public.journal.views_compat import IssueDetailRedirectView


pytestmark = pytest.mark.django_db

@pytest.fixture()
def view():
    # Journal with volumes and numbers.
    journal1 = JournalFactory(code='journal1', localidentifier='journal1')
    IssueFactory(journal=journal1, localidentifier='issue11', year='2001', volume='1', number='1')
    IssueFactory(journal=journal1, localidentifier='issue21', year='2002', volume='2', number='1')
    IssueFactory(journal=journal1, localidentifier='issue22', year='2002', volume='2', number='2')
    IssueFactory(journal=journal1, localidentifier='issue31', year='2003', volume='3', number='1')
    IssueFactory(journal=journal1, localidentifier='issue32', year='2003', volume='3', number='2')
    IssueFactory(journal=journal1, localidentifier='issue33', year='2003', volume='3', number='3')
    # Journal with only volumes.
    journal2 = JournalFactory(code='journal2', localidentifier='journal2')
    IssueFactory(journal=journal2, localidentifier='issue1', year='2001', volume='1')
    IssueFactory(journal=journal2, localidentifier='issue2', year='2002', volume='2')
    IssueFactory(journal=journal2, localidentifier='issue3', year='2003', volume='3')
    # Journal with only numbers.
    journal3 = JournalFactory(code='journal3', localidentifier='journal3')
    IssueFactory(journal=journal3, localidentifier='issue4', year='2004', number='4')
    IssueFactory(journal=journal3, localidentifier='issue5', year='2005', number='5')
    IssueFactory(journal=journal3, localidentifier='issue6', year='2006', number='6')
    # View.
    view = IssueDetailRedirectView()
    view.request = unittest.mock.MagicMock()
    yield view


class TestIssueDetailRedirectView:

    @pytest.mark.parametrize('localidentifier, ticket, expected_url', [
        ('issue11', '', '/fr/revues/journal1/2001-v1-n1-issue11/'),
        ('issue21', '', '/fr/revues/journal1/2002-v2-n1-issue21/'),
        ('issue22', '', '/fr/revues/journal1/2002-v2-n2-issue22/'),
        ('issue31', '', '/fr/revues/journal1/2003-v3-n1-issue31/'),
        ('issue32', '', '/fr/revues/journal1/2003-v3-n2-issue32/'),
        ('issue33', '', '/fr/revues/journal1/2003-v3-n3-issue33/'),
        # Ticket in request should be added to URL.
        ('issue11', 'foobar', '/fr/revues/journal1/2001-v1-n1-issue11/?ticket=foobar'),
        # Nonexistent localidentifier should raise 404.
        ('issue404', '', False),
    ])
    def test_get_redirect_url_with_id_in_request(self, localidentifier, ticket, expected_url, view):
        view.request.GET = {'id': localidentifier, 'ticket': ticket}
        if expected_url:
            assert expected_url == view.get_redirect_url(journal_code='journal1')
        else:
            with pytest.raises(Http404):
                view.get_redirect_url(journal_code='journal1')

    @pytest.mark.parametrize('localidentifier, expected_url', [
        ('issue11', '/fr/revues/journal1/2001-v1-n1-issue11/'),
        ('issue21', '/fr/revues/journal1/2002-v2-n1-issue21/'),
        ('issue22', '/fr/revues/journal1/2002-v2-n2-issue22/'),
        ('issue31', '/fr/revues/journal1/2003-v3-n1-issue31/'),
        ('issue32', '/fr/revues/journal1/2003-v3-n2-issue32/'),
        ('issue33', '/fr/revues/journal1/2003-v3-n3-issue33/'),
        # Nonexistent localidentifier should raise 404.
        ('issue404', False),
    ])
    def test_get_redirect_url_with_localidentifier(self, localidentifier, expected_url, view):
        if expected_url:
            assert expected_url == view.get_redirect_url(journal_code='journal1', localidentifier=localidentifier)
        else:
            with pytest.raises(Http404):
                view.get_redirect_url(journal_code='journal1', localidentifier=localidentifier)

    @pytest.mark.parametrize('year, volume, number, expected_url', [
        ('2001', '1', '1', '/fr/revues/journal1/2001-v1-n1-issue11/'),
        ('2002', '2', '1', '/fr/revues/journal1/2002-v2-n1-issue21/'),
        ('2002', '2', '2', '/fr/revues/journal1/2002-v2-n2-issue22/'),
        ('2003', '3', '1', '/fr/revues/journal1/2003-v3-n1-issue31/'),
        ('2003', '3', '2', '/fr/revues/journal1/2003-v3-n2-issue32/'),
        ('2003', '3', '3', '/fr/revues/journal1/2003-v3-n3-issue33/'),
        # If volume is omitted, the right issue should still be found.
        ('2001', '', '1', '/fr/revues/journal1/2001-v1-n1-issue11/'),
        # Wrong year, volume or number should raise 404.
        ('2004', '4', '1', False),
        ('2001', '1', '4', False),
    ])
    def test_get_redirect_url_with_year_volume_and_number(self, year, volume, number, expected_url, view):
        if expected_url:
            assert expected_url == view.get_redirect_url(journal_code='journal1', year=year, v=volume, n=number)
        else:
            with pytest.raises(Http404):
                view.get_redirect_url(journal_code='journal1', year=year, v=volume, n=number)

    @pytest.mark.parametrize('volume, number, expected_url', [
        ('1', '1', '/fr/revues/journal1/2001-v1-n1-issue11/'),
        ('2', '1', '/fr/revues/journal1/2002-v2-n1-issue21/'),
        ('2', '2', '/fr/revues/journal1/2002-v2-n2-issue22/'),
        ('3', '1', '/fr/revues/journal1/2003-v3-n1-issue31/'),
        ('3', '2', '/fr/revues/journal1/2003-v3-n2-issue32/'),
        ('3', '3', '/fr/revues/journal1/2003-v3-n3-issue33/'),
        # Wrong volume or number should raise 404.
        ('4', '1', False),
        ('1', '4', False),
    ])
    def test_get_redirect_url_with_volume_and_number(self, volume, number, expected_url, view):
        if expected_url:
            assert expected_url == view.get_redirect_url(journal_code='journal1', v=volume, n=number)
        else:
            with pytest.raises(Http404):
                view.get_redirect_url(journal_code='journal1', v=volume, n=number)

    @pytest.mark.parametrize('year, volume, expected_url', [
        ('2001', '1', '/fr/revues/journal2/2001-v1-issue1/'),
        ('2002', '2', '/fr/revues/journal2/2002-v2-issue2/'),
        ('2003', '3', '/fr/revues/journal2/2003-v3-issue3/'),
        # Wrong year or volume should raise 404.
        ('2004', '1', False),
        ('2001', '4', False),
    ])
    def test_get_redirect_url_with_year_and_volume(self, year, volume, expected_url, view):
        if expected_url:
            assert expected_url == view.get_redirect_url(journal_code='journal2', year=year, v=volume)
        else:
            with pytest.raises(Http404):
                view.get_redirect_url(journal_code='journal2', year=year, v=volume)

    @pytest.mark.parametrize('volume, expected_url', [
        ('1', '/fr/revues/journal2/2001-v1-issue1/'),
        ('2', '/fr/revues/journal2/2002-v2-issue2/'),
        ('3', '/fr/revues/journal2/2003-v3-issue3/'),
        # Wrong volume should raise 404.
        ('4', False),
    ])
    def test_get_redirect_url_with_volume(self, volume, expected_url, view):
        if expected_url:
            assert expected_url == view.get_redirect_url(journal_code='journal2', v=volume)
        else:
            with pytest.raises(Http404):
                view.get_redirect_url(journal_code='journal2', v=volume)
