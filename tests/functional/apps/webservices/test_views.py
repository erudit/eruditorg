import datetime as dt

import pytest
from lxml import etree
from django.urls import reverse
from django.test import Client
from erudit.models import JournalType
from erudit.test.factories import JournalFactory, IssueFactory, EmbargoedIssueFactory, NonEmbargoedIssueFactory

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

    def test_embargo_duration(self):
        journal_scientific = JournalFactory.create(type_code=JournalType.CODE_SCIENTIFIC)
        journal_cultural = JournalFactory.create(type_code=JournalType.CODE_CULTURAL)
        embargoed_issue_scientific = EmbargoedIssueFactory(journal=journal_scientific)
        embargoed_issue_cultural = EmbargoedIssueFactory(journal=journal_cultural)

        url = reverse('webservices:restrictions')
        response = Client().get(url)
        root = etree.fromstring(response.content.decode())

        assert root[0].find('embargo_duration').attrib['unit'] == 'day'

        embargo_duration_scientific = root.find(f"journal[@code='{journal_scientific.code}']/embargo_duration").text
        embargo_duration_cultural = root.find(f"journal[@code='{journal_cultural.code}']/embargo_duration").text

        assert embargo_duration_scientific == '365'
        assert embargo_duration_cultural == '1095'


class TestRestrictionsByJournalView:

    def test_that_journal_and_all_issues_works(self):
        issue_openAccess_1 = NonEmbargoedIssueFactory(journal__collection__code='erudit')
        journal = issue_openAccess_1.journal
        issue_openAccess_2 = NonEmbargoedIssueFactory(journal=journal)
        issue_openAccess_3 = NonEmbargoedIssueFactory(journal=journal)

        issue_whitelisted_1 = EmbargoedIssueFactory(journal=journal, force_free_access=True)
        issue_whitelisted_2 = EmbargoedIssueFactory(journal=journal, force_free_access=True)

        # we must create a embargoed issue at the end.
        # if we create a free issue at the end it will be considered as embargoed
        issue_embargoed_1 = EmbargoedIssueFactory(journal=journal)
        issue_embargoed_2 = EmbargoedIssueFactory(journal=journal)
        issue_embargoed_3 = EmbargoedIssueFactory(journal=journal)

        url = reverse('webservices:restrictionsByJournal',
                      kwargs={'journal_code': journal.localidentifier})
        response = Client().get(url)
        root = etree.fromstring(response.content.decode())

        # Check the attributes of the journal
        assert root.tag == 'journal'
        assert root.attrib['code'] == journal.code
        assert root.attrib['localidentifier'] == journal.localidentifier
        assert root.attrib['embargoed'] == 'True'

        # Check the presence and the values of other elements
        for child in root:
            assert child.tag in ('embargo_date', 'embargo_duration', 'issues')

        embargo_date = journal.date_embargo_begins.strftime('%Y-%m-%d')
        embargo_duration = '365'
        assert root.find('embargo_date').text == embargo_date
        assert root.find('embargo_duration').text == embargo_duration

        # Check the attributes of the issues
        issues_element = root.find('issues')
        assert issues_element.attrib['count'] == str(len(journal.published_issues))
        assert len(issues_element) == len(journal.published_issues)

        embargoed_count = journal.published_issues.count() - journal.published_open_access_issues.count()
        assert embargoed_count == 3
        assert issues_element.attrib['embargoed_count'] == str(embargoed_count)

        whitelisted_issues = journal.published_issues.filter(force_free_access=True)
        assert len(whitelisted_issues) == 2
        assert issues_element.attrib['whitelisted_count'] == str(len(whitelisted_issues))

        issue_element = issues_element[0]
        assert issues_element[0].attrib['embargoed'] == 'True'
        assert issues_element[1].attrib['embargoed'] == 'True'
        assert issues_element[2].attrib['embargoed'] == 'True'
        assert issues_element[3].attrib['embargoed'] == 'False'
        assert issues_element[4].attrib['embargoed'] == 'False'
        assert issues_element[5].attrib['embargoed'] == 'False'
        assert issues_element[6].attrib['embargoed'] == 'False'
        assert issues_element[7].attrib['embargoed'] == 'False'

        assert issues_element[0].attrib['whitelisted'] == 'False'
        assert issues_element[1].attrib['whitelisted'] == 'False'
        assert issues_element[2].attrib['whitelisted'] == 'False'
        assert issues_element[3].attrib['whitelisted'] == 'True'
        assert issues_element[4].attrib['whitelisted'] == 'True'
        assert issues_element[5].attrib['whitelisted'] == 'False'
        assert issues_element[6].attrib['whitelisted'] == 'False'
        assert issues_element[7].attrib['whitelisted'] == 'False'

        assert issues_element[0].attrib['localidentifier'] == issue_embargoed_3.localidentifier
        assert issues_element[1].attrib['localidentifier'] == issue_embargoed_2.localidentifier
        assert issues_element[2].attrib['localidentifier'] == issue_embargoed_1.localidentifier
        assert issues_element[3].attrib['localidentifier'] == issue_whitelisted_2.localidentifier
        assert issues_element[4].attrib['localidentifier'] == issue_whitelisted_1.localidentifier
        assert issues_element[5].attrib['localidentifier'] == issue_openAccess_3.localidentifier
        assert issues_element[6].attrib['localidentifier'] == issue_openAccess_2.localidentifier
        assert issues_element[7].attrib['localidentifier'] == issue_openAccess_1.localidentifier

    def test_that_journal_does_not_exist(self):
        url = reverse('webservices:restrictionsByJournal',
                      kwargs={'journal_code': 'undefined'})
        response = Client().get(url)
        root = etree.fromstring(response.content.decode())
        assert root.tag == 'error'

    def test_that_journal_without_issues(self):
        journal_without_issues = JournalFactory.create()
        url = reverse('webservices:restrictionsByJournal',
                      kwargs={'journal_code': str(journal_without_issues.localidentifier)})
        response = Client().get(url)
        root = etree.fromstring(response.content.decode())
        assert root.tag == 'journal'
        assert root.attrib['localidentifier'] == journal_without_issues.localidentifier

        issues_element = root.find('issues')
        assert issues_element.attrib['count'] == '0'
        assert issues_element.attrib['embargoed_count'] == '0'
        assert issues_element.attrib['whitelisted_count'] == '0'
        assert issues_element.find('issue') is None

        journal_without_issues.localidentifier = None
        journal_without_issues.save()
        response = Client().get(url)
        root = etree.fromstring(response.content.decode())
        assert root.tag == 'error'
