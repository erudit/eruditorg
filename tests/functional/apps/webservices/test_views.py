import datetime as dt

import pytest
from lxml import etree
from django.core.urlresolvers import reverse
from django.test import Client

from erudit.test.factories import IssueFactory

pytestmark = pytest.mark.django_db


class TestRestrictionsView:
    def test_that_it_works(self):
        issue = IssueFactory(journal__collection__code='erudit')
        url = reverse('webservices:restrictions')
        response = Client().get(url)
        root = etree.fromstring(response.content.decode())
        assert root[0].attrib['identifier'] == issue.journal.code
        TODAY = dt.date.today()
        EXPECTED = str(TODAY.year)
        assert root[0].find('years').text == EXPECTED
        EXPECTED = issue.journal.date_embargo_begins.strftime('%Y-%m-%d')
        assert root[0].find('embargo_date').text == EXPECTED
        elem = root[0].find('embargoed_issues')
        assert len(elem[:]) == 1

    def test_whitelisting(self):
        issue = IssueFactory(journal__collection__code='erudit')
        IssueFactory(journal=issue.journal, force_free_access=True)
        url = reverse('webservices:restrictions')
        response = Client().get(url)
        root = etree.fromstring(response.content.decode())
        elem = root[0].find('embargoed_issues')
        assert len(elem[:]) == 1
        assert elem[0].attrib['localidentifier'] == issue.localidentifier
