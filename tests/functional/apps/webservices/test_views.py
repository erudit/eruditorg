import datetime as dt

import pytest
from lxml import etree
from django.core.urlresolvers import reverse
from django.test import Client

from erudit.test.factories import IssueFactory

pytestmark = pytest.mark.django_db


class TestRetroRestrictionsView:
    def test_that_it_works(self):
        # This view is transitional and mimicks legacy stuff. It's going away soon and we just
        # want to test that it works, not test all embargo scenarios.
        issue = IssueFactory(journal__collection__code='erudit')
        url = reverse('webservices:restrictions_retro')
        response = Client().get(url)
        root = etree.fromstring(response.content.decode())
        assert root[0].attrib['identifier'] == issue.journal.code
        assert root[0].find('years').text == str(dt.date.today().year)
