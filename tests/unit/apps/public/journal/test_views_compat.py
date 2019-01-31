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
    # Issue that covers several years.
    IssueFactory(journal=journal1, localidentifier='issue41', year='2004', volume='4', number='1', publication_period='2004-2005')
    # Issues with multiple volumes.
    IssueFactory(journal=journal1, localidentifier='issue51', year='2005', volume='5-6', number='1')
    IssueFactory(journal=journal1, localidentifier='issue71', year='2005', volume='7', number='1')
    # Issues with multiple numbers.
    IssueFactory(journal=journal1, localidentifier='issue91', year='2006', volume='9', number='1-2')
    IssueFactory(journal=journal1, localidentifier='issue101', year='2006', volume='10', number='1')
    # Issue that covers several years, with multiple volumes and multiple numbers.
    IssueFactory(journal=journal1, localidentifier='issue1221', year='2008', volume='12-21', number='34-43', publication_period='2007-2008')

    # Journal with volumes only.
    journal2 = JournalFactory(code='journal2', localidentifier='journal2')
    IssueFactory(journal=journal2, localidentifier='issue1v', year='2001', volume='1')
    IssueFactory(journal=journal2, localidentifier='issue2v', year='2002', volume='2')
    IssueFactory(journal=journal2, localidentifier='issue3v', year='2003', volume='3')
    # Issue that covers several years.
    IssueFactory(journal=journal2, localidentifier='issue4v', year='2004', volume='4', publication_period='2004-2005')
    # Issues with multiple volumes.
    IssueFactory(journal=journal2, localidentifier='issue5v', year='2005', volume='5-6')
    IssueFactory(journal=journal2, localidentifier='issue7v', year='2005', volume='7')

    # Journal with numbers only.
    journal3 = JournalFactory(code='journal3', localidentifier='journal3')
    IssueFactory(journal=journal3, localidentifier='issue1n', year='2001', number='1')
    IssueFactory(journal=journal3, localidentifier='issue2n', year='2002', number='2')
    IssueFactory(journal=journal3, localidentifier='issue3n', year='2003', number='3')
    # Issue that covers several years.
    IssueFactory(journal=journal3, localidentifier='issue4n', year='2004', number='4', publication_period='2004-2005')
    # Issues with multiple numbers.
    IssueFactory(journal=journal3, localidentifier='issue5n', year='2005', number='5-6')
    IssueFactory(journal=journal3, localidentifier='issue7n', year='2005', number='7')

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
        ('1999', '1', '1', False),
        ('2001', '0', '1', False),
        ('2001', '1', '0', False),
        # Issue that covers several years should be found by any year that is covered.
        ('2004', '4', '1', '/fr/revues/journal1/2004-v4-n1-issue41/'),
        ('2005', '4', '1', '/fr/revues/journal1/2004-v4-n1-issue41/'),
        # Issues with multiple volumes should be found by any volume.
        ('2005', '5-6', '1', '/fr/revues/journal1/2005-v5-6-n1-issue51/'),
        ('2005', '5', '1', '/fr/revues/journal1/2005-v5-6-n1-issue51/'),
        ('2005', '6', '1', '/fr/revues/journal1/2005-v5-6-n1-issue51/'),
        ('2005', '7-8', '1', '/fr/revues/journal1/2005-v7-n1-issue71/'),
        ('2005', '7', '1', '/fr/revues/journal1/2005-v7-n1-issue71/'),
        # Issues with multiple numbers should be found by any number.
        ('2006', '9', '1-2', '/fr/revues/journal1/2006-v9-n1-2-issue91/'),
        ('2006', '9', '1', '/fr/revues/journal1/2006-v9-n1-2-issue91/'),
        ('2006', '9', '2', '/fr/revues/journal1/2006-v9-n1-2-issue91/'),
        ('2006', '10', '1-2', '/fr/revues/journal1/2006-v10-n1-issue101/'),
        ('2006', '10', '1', '/fr/revues/journal1/2006-v10-n1-issue101/'),
        # Issue that covers several years, with multiple volumes and multiple numbers.
        ('2007', '12-21', '34-43', '/fr/revues/journal1/2008-v12-21-n34-43-issue1221/'),
        ('2008', '12-21', '34-43', '/fr/revues/journal1/2008-v12-21-n34-43-issue1221/'),
        ('2007', '12', '34-43', '/fr/revues/journal1/2008-v12-21-n34-43-issue1221/'),
        ('2007', '21', '34-43', '/fr/revues/journal1/2008-v12-21-n34-43-issue1221/'),
        ('2007', '12-21', '34', '/fr/revues/journal1/2008-v12-21-n34-43-issue1221/'),
        ('2007', '12-21', '43', '/fr/revues/journal1/2008-v12-21-n34-43-issue1221/'),
        ('2008', '12', '43', '/fr/revues/journal1/2008-v12-21-n34-43-issue1221/'),
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
        ('0', '1', False),
        ('1', '0', False),
        # Issues with multiple volumes should be found by any volume.
        ('5-6', '1', '/fr/revues/journal1/2005-v5-6-n1-issue51/'),
        ('5', '1', '/fr/revues/journal1/2005-v5-6-n1-issue51/'),
        ('6', '1', '/fr/revues/journal1/2005-v5-6-n1-issue51/'),
        ('7-8', '1', '/fr/revues/journal1/2005-v7-n1-issue71/'),
        ('7', '1', '/fr/revues/journal1/2005-v7-n1-issue71/'),
        #with multiple numbers should be found by any number.
        ('9', '1-2', '/fr/revues/journal1/2006-v9-n1-2-issue91/'),
        ('9', '1', '/fr/revues/journal1/2006-v9-n1-2-issue91/'),
        ('9', '2', '/fr/revues/journal1/2006-v9-n1-2-issue91/'),
        ('10', '1-2', '/fr/revues/journal1/2006-v10-n1-issue101/'),
        ('10', '1', '/fr/revues/journal1/2006-v10-n1-issue101/'),
        # Issue that covers several years, with multiple volumes and multiple numbers.
        ('12-21', '34-43', '/fr/revues/journal1/2008-v12-21-n34-43-issue1221/'),
        ('12', '34-43', '/fr/revues/journal1/2008-v12-21-n34-43-issue1221/'),
        ('21', '34-43', '/fr/revues/journal1/2008-v12-21-n34-43-issue1221/'),
        ('12-21', '34', '/fr/revues/journal1/2008-v12-21-n34-43-issue1221/'),
        ('12', '34', '/fr/revues/journal1/2008-v12-21-n34-43-issue1221/'),
    ])
    def test_get_redirect_url_with_volume_and_number(self, volume, number, expected_url, view):
        if expected_url:
            assert expected_url == view.get_redirect_url(journal_code='journal1', v=volume, n=number)
        else:
            with pytest.raises(Http404):
                view.get_redirect_url(journal_code='journal1', v=volume, n=number)

    @pytest.mark.parametrize('year, volume, expected_url', [
        ('2001', '1', '/fr/revues/journal2/2001-v1-issue1v/'),
        ('2002', '2', '/fr/revues/journal2/2002-v2-issue2v/'),
        ('2003', '3', '/fr/revues/journal2/2003-v3-issue3v/'),
        # Wrong year or volume should raise 404.
        ('1999', '1', False),
        ('2001', '0', False),
        # Issue that covers several years should be found by any year that is covered.
        ('2004', '4', '/fr/revues/journal2/2004-v4-issue4v/'),
        ('2005', '4', '/fr/revues/journal2/2004-v4-issue4v/'),
        # Issues with multiple volumes should be found by any volume.
        ('2005', '5-6', '/fr/revues/journal2/2005-v5-6-issue5v/'),
        ('2005', '5', '/fr/revues/journal2/2005-v5-6-issue5v/'),
        ('2005', '6', '/fr/revues/journal2/2005-v5-6-issue5v/'),
        ('2005', '7-8', '/fr/revues/journal2/2005-v7-issue7v/'),
        ('2005', '7', '/fr/revues/journal2/2005-v7-issue7v/'),
    ])
    def test_get_redirect_url_with_year_and_volume(self, year, volume, expected_url, view):
        if expected_url:
            assert expected_url == view.get_redirect_url(journal_code='journal2', year=year, v=volume)
        else:
            with pytest.raises(Http404):
                view.get_redirect_url(journal_code='journal2', year=year, v=volume)

    @pytest.mark.parametrize('volume, expected_url', [
        ('1', '/fr/revues/journal2/2001-v1-issue1v/'),
        ('2', '/fr/revues/journal2/2002-v2-issue2v/'),
        ('3', '/fr/revues/journal2/2003-v3-issue3v/'),
        # Wrong volume should raise 404.
        ('0', False),
        # Issues with multiple volumes should be found by any volume.
        ('5-6', '/fr/revues/journal2/2005-v5-6-issue5v/'),
        ('5', '/fr/revues/journal2/2005-v5-6-issue5v/'),
        ('6', '/fr/revues/journal2/2005-v5-6-issue5v/'),
        ('7-8', '/fr/revues/journal2/2005-v7-issue7v/'),
        ('7', '/fr/revues/journal2/2005-v7-issue7v/'),
    ])
    def test_get_redirect_url_with_volume(self, volume, expected_url, view):
        if expected_url:
            assert expected_url == view.get_redirect_url(journal_code='journal2', v=volume)
        else:
            with pytest.raises(Http404):
                view.get_redirect_url(journal_code='journal2', v=volume)

    @pytest.mark.parametrize('year, number, expected_url', [
        ('2001', '1', '/fr/revues/journal3/2001-n1-issue1n/'),
        ('2002', '2', '/fr/revues/journal3/2002-n2-issue2n/'),
        ('2003', '3', '/fr/revues/journal3/2003-n3-issue3n/'),
        # Wrong year or number should raise 404.
        ('1999', '1', False),
        ('2001', '0', False),
        # Issue that covers several years should be found by any year that is covered.
        ('2004', '4', '/fr/revues/journal3/2004-n4-issue4n/'),
        ('2005', '4', '/fr/revues/journal3/2004-n4-issue4n/'),
        # Issues with multiple numbers should be found by any number.
        ('2005', '5-6', '/fr/revues/journal3/2005-n5-6-issue5n/'),
        ('2005', '5', '/fr/revues/journal3/2005-n5-6-issue5n/'),
        ('2005', '6', '/fr/revues/journal3/2005-n5-6-issue5n/'),
        ('2005', '7-8', '/fr/revues/journal3/2005-n7-issue7n/'),
        ('2005', '7', '/fr/revues/journal3/2005-n7-issue7n/'),
    ])
    def test_get_redirect_url_with_year_and_number(self, year, number, expected_url, view):
        if expected_url:
            assert expected_url == view.get_redirect_url(journal_code='journal3', year=year, n=number)
        else:
            with pytest.raises(Http404):
                view.get_redirect_url(journal_code='journal3', year=year, n=number)

    @pytest.mark.parametrize('number, expected_url', [
        ('1', '/fr/revues/journal3/2001-n1-issue1n/'),
        ('2', '/fr/revues/journal3/2002-n2-issue2n/'),
        ('3', '/fr/revues/journal3/2003-n3-issue3n/'),
        # Wrong number should raise 404.
        ('0', False),
        # Issues with multiple numbers should be found by any number.
        ('5-6', '/fr/revues/journal3/2005-n5-6-issue5n/'),
        ('5', '/fr/revues/journal3/2005-n5-6-issue5n/'),
        ('6', '/fr/revues/journal3/2005-n5-6-issue5n/'),
        ('7-8', '/fr/revues/journal3/2005-n7-issue7n/'),
        ('7', '/fr/revues/journal3/2005-n7-issue7n/'),
    ])
    def test_get_redirect_url_with_number(self, number, expected_url, view):
        if expected_url:
            assert expected_url == view.get_redirect_url(journal_code='journal3', n=number)
        else:
            with pytest.raises(Http404):
                view.get_redirect_url(journal_code='journal3', n=number)
