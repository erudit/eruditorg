import datetime as dt

import pytest
from lxml import etree
from django.core.urlresolvers import reverse
from django.test import Client
from erudit.test.factories import IssueFactory, EmbargoedIssueFactory
from django.test import RequestFactory

pytestmark = pytest.mark.django_db


class TestRestrictionsView:
    def test_that_it_works(self):
        issue = IssueFactory(journal__collection__code='erudit')
        url = reverse('webservices:restrictions')
        response = Client().get(url)
        root = etree.fromstring(response.content.decode())
        assert root[0].attrib['code'] == issue.journal.code
        assert root[0].attrib['localidentifier'] == issue.journal.localidentifier
        TODAY = dt.date.today()
        EXPECTED = str(TODAY.year)
        assert root[0].find('years').text == EXPECTED
        EXPECTED = issue.journal.date_embargo_begins.strftime('%Y-%m-%d')
        assert root[0].find('embargo_date').text == EXPECTED

    def test_excludes_journals_with_unpublished_issues(self):

        issue = IssueFactory(journal__collection__code='erudit')
        issue.is_published = False
        issue.save()
        url = reverse('webservices:restrictions')
        response = Client().get(url)
        root = etree.fromstring(response.content.decode())
        assert len(root) == 0

    def test_whitelisting(self):
        issue = IssueFactory(journal__collection__code='erudit')
        IssueFactory(journal=issue.journal, force_free_access=True)
        url = reverse('webservices:restrictions')
        response = Client().get(url)
        root = etree.fromstring(response.content.decode())
        elem = root[0].find('embargoed_issues')
        assert len(elem[:]) == 1
        assert elem[0].attrib['localidentifier'] == issue.localidentifier


class TestRestrictionsByJournalView:

    def test_that_journal_and_all_issues_works(self):
        issue = EmbargoedIssueFactory(journal__collection__code='erudit')
        url = reverse('webservices:restrictionsByJournal',  kwargs={'journal_code':issue.journal.localidentifier})
        response = Client().get(url)
        root = etree.fromstring(response.content.decode())

        # Check the attributes of the journal
        assert root.tag == 'journal'
        assert root.attrib['code'] == issue.journal.code
        assert root.attrib['localidentifier'] == issue.journal.localidentifier
        assert root.attrib['embargoed'] == 'True'

        # Check the presence and the values of other elements
        for child in root:
            assert child.tag in ('embargo_date', 'embargo_duration', 'issues')

        embargo_date = issue.journal.date_embargo_begins.strftime('%Y-%m-%d')
        embargo_duration = str(issue.journal.embargo_in_months)
        assert root.find('embargo_date').text == embargo_date
        assert root.find('embargo_duration').text == embargo_duration

        # Check the attributes of the issues
        issues_element = root.find('issues')
        assert issues_element.attrib['count'] == str(len(issue.journal.published_issues))
        assert issues_element.attrib['embargoed_count'] == str(len(issue.journal.published_issues))
        whitelisted_issues=issue.journal.published_issues.filter(force_free_access=True)
        assert issues_element.attrib['whitelisted_count'] == str(len(whitelisted_issues))

        # Check the attributes of the last issue (index = 0)
        issue_element = issues_element[0]
        assert issue_element.attrib['embargoed'] == str(issue.embargoed)
        assert issue_element.attrib['whitelisted'] == str(issue.force_free_access)
        assert issue_element.attrib['localidentifier'] == issue.localidentifier
