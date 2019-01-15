import pytest
from django.urls import reverse
from django.core.cache import cache
from django.test import Client

from erudit.test.factories import (
    ThesisFactory, ThesisRepositoryFactory
)

pytestmark = pytest.mark.django_db


class TestThesisHomeView:
    def test_inserts_collection_information_into_the_context(self, solr_client):
        repository1 = ThesisRepositoryFactory.create()
        repository2 = ThesisRepositoryFactory.create()
        thesis_1 = ThesisFactory.create(repository=repository1)
        solr_client.add_document(thesis_1)
        thesis_2 = ThesisFactory.create(repository=repository1)
        solr_client.add_document(thesis_2)
        thesis_3 = ThesisFactory.create(repository=repository1)
        solr_client.add_document(thesis_3)
        thesis_4 = ThesisFactory.create(repository=repository1)
        solr_client.add_document(thesis_4)
        thesis_5 = ThesisFactory.create(repository=repository2)
        solr_client.add_document(thesis_5)
        thesis_6 = ThesisFactory.create(repository=repository2)
        solr_client.add_document(thesis_6)
        thesis_7 = ThesisFactory.create(repository=repository2)
        solr_client.add_document(thesis_7)
        thesis_8 = ThesisFactory.create(repository=repository2)
        solr_client.add_document(thesis_8)
        url = reverse('public:thesis:home')
        response = Client().get(url)
        assert response.status_code == 200
        assert 'repository_summaries' in response.context
        assert len(response.context['repository_summaries']) == 2
        assert response.context['repository_summaries'][0]['thesis_count'] == 4
        assert response.context['repository_summaries'][1]['thesis_count'] == 4
        ids = [
            t.localidentifier for t in
            response.context['repository_summaries'][0]['recent_theses']]
        assert ids == [thesis_4.id, thesis_3.id, thesis_2.id, ]
        ids = [
            t.localidentifier for t in
            response.context['repository_summaries'][1]['recent_theses']]
        assert ids == [thesis_8.id, thesis_7.id, thesis_6.id, ]


class TestThesisCollectionHomeView:
    def test_inserts_the_recent_theses_into_the_context(self, solr_client):
        theses = [ThesisFactory.create() for _ in range(4)]
        for thesis in theses:
            solr_client.add_document(thesis)
        url = reverse('public:thesis:collection_home', args=(theses[0].repository.code,))
        response = Client().get(url)
        assert response.status_code == 200
        EXPECTED = [3, 2, 1]
        ids = [t.localidentifier for t in response.context['recent_theses']]
        assert ids == [theses[i].id for i in EXPECTED]

    def test_inserts_the_thesis_count_into_the_context(self, solr_client):
        cache.clear()
        theses = [ThesisFactory.create() for _ in range(4)]
        for thesis in theses:
            solr_client.add_document(thesis)
        url = reverse('public:thesis:collection_home', args=(theses[0].repository.code,))
        response = Client().get(url)
        assert response.status_code == 200
        assert response.context['thesis_count'] == 4

    def test_inserts_the_thesis_counts_grouped_by_publication_years(self, solr_client):
        cache.clear()
        theses = [
            ThesisFactory.create(year=2010),
            ThesisFactory.create(year=2012),
            ThesisFactory.create(year=2013),
            ThesisFactory.create(year=2014),
            ThesisFactory.create(year=2012),
            ThesisFactory.create(year=2012),
            ThesisFactory.create(year=2014),
        ]
        for thesis in theses:
            solr_client.add_document(thesis)
        url = reverse('public:thesis:collection_home', args=(theses[0].repository.code,))
        response = Client().get(url)
        assert response.status_code == 200
        group = list(response.context['view'].by_publication_year())
        EXPECTED = [
            ('2014', 2),
            ('2013', 1),
            ('2012', 3),
            ('2010', 1),
        ]
        assert group == EXPECTED

    def test_inserts_the_thesis_counts_grouped_by_author_name(self, solr_client):
        cache.clear()
        theses = [
            ThesisFactory.create(authors=['Aname']),
            ThesisFactory.create(authors=['Bname']),
            ThesisFactory.create(authors=['Cname']),
            ThesisFactory.create(authors=['Dname']),
            ThesisFactory.create(authors=['Bname']),
            ThesisFactory.create(authors=['Bname']),
            ThesisFactory.create(authors=['Dname']),
        ]
        for thesis in theses:
            solr_client.add_document(thesis)
        url = reverse('public:thesis:collection_home', args=(theses[0].repository.code,))
        response = Client().get(url)
        assert response.status_code == 200
        group = list(response.context['view'].by_author_first_letter())
        EXPECTED = [
            ('A', 1),
            ('B', 3),
            ('C', 1),
            ('D', 2),
        ]
        assert group == EXPECTED


class TestThesisPublicationYearListView:
    def test_returns_only_theses_for_a_given_publication_year(self, solr_client):
        theses = [
            ThesisFactory.create(year=2010),
            ThesisFactory.create(year=2012),
            ThesisFactory.create(year=2013),
            ThesisFactory.create(year=2014),
            ThesisFactory.create(year=2012),
            ThesisFactory.create(year=2012),
            ThesisFactory.create(year=2014),
        ]
        for thesis in theses:
            solr_client.add_document(thesis)

        url = reverse(
            'public:thesis:collection_list_per_year', args=(theses[0].repository.code, 2012))
        response = Client().get(url)
        assert response.status_code == 200
        ids = {t.localidentifier for t in response.context['theses']}
        EXPECTED = {1, 4, 5}
        assert ids == {theses[i].id for i in EXPECTED}

    def test_embeds_the_publication_years_aggregation_results_into_the_context(self, solr_client):
        cache.clear()
        theses = [
            ThesisFactory.create(year=2010),
            ThesisFactory.create(year=2012),
            ThesisFactory.create(year=2013),
            ThesisFactory.create(year=2014),
            ThesisFactory.create(year=2012),
            ThesisFactory.create(year=2012),
            ThesisFactory.create(year=2014),
        ]
        for thesis in theses:
            solr_client.add_document(thesis)

        url = reverse(
            'public:thesis:collection_list_per_year', args=(theses[0].repository.code, 2012))
        response = Client().get(url)
        assert response.status_code == 200
        EXPECTED = [
            ('2014', 2),
            ('2013', 1),
            ('2012', 3),
            ('2010', 1),
        ]
        assert response.context['other_publication_years'] == EXPECTED

    @pytest.mark.parametrize('sort_by,desc', [
        ('author_asc', False),
        ('author_desc', True),
    ])
    def test_can_sort_theses_by_author_name(self, sort_by, desc, solr_client):
        theses = [
            ThesisFactory.create(year=2012, authors=['Aname']),
            ThesisFactory.create(year=2012, authors=['Cname']),
            ThesisFactory.create(year=2012, authors=['Bname']),
        ]
        for thesis in theses:
            solr_client.add_document(thesis)
        url = reverse(
            'public:thesis:collection_list_per_year', args=(theses[0].repository.code, 2012))
        response = Client().get(url, {'sort_by': sort_by})
        assert response.status_code == 200
        ids = [t.localidentifier for t in response.context['theses']]
        EXPECTED = [0, 2, 1]
        if desc:
            EXPECTED = reversed(EXPECTED)
        assert ids == [theses[i].id for i in EXPECTED]

    @pytest.mark.parametrize('sort_by,desc', [
        ('date_asc', False),
        ('date_desc', True),
    ])
    def test_can_sort_theses_by_date(self, sort_by, desc, solr_client):
        theses = [
            ThesisFactory.create(year=2012, date_added='20120101'),
            ThesisFactory.create(year=2012, date_added='20140101'),
            ThesisFactory.create(year=2012, date_added='20120102'),
        ]
        for thesis in theses:
            solr_client.add_document(thesis)
        url = reverse(
            'public:thesis:collection_list_per_year', args=(theses[0].repository.code, 2012))
        response = Client().get(url, {'sort_by': sort_by})
        assert response.status_code == 200
        ids = [t.localidentifier for t in response.context['theses']]
        EXPECTED = [0, 2, 1]
        if desc:
            EXPECTED = reversed(EXPECTED)
        assert ids == [theses[i].id for i in EXPECTED]

    def test_invalid_page_in_querystring(self, solr_client):
        thesis = ThesisFactory(year=2012)
        solr_client.add_document(thesis)
        url = reverse(
            'public:thesis:collection_list_per_year', args=(thesis.repository.code, 2012))
        url += '?page=10,11'
        response = Client().get(url)
        assert response.status_code == 200

    def test_rendered_contents(self, solr_client):
        thesis = ThesisFactory(title='foobar_title', authors=['foobar_author'], year=2012)
        solr_client.add_document(thesis)
        url = reverse(
            'public:thesis:collection_list_per_year', args=(thesis.repository.code, 2012))
        response = Client().get(url)
        assert b'foobar_author' in response.content
        assert b'foobar_title' in response.content


class TestThesisPublicationAuthorNameListView:
    def test_returns_only_theses_for_a_given_author_first_letter(self, solr_client):
        theses = [
            ThesisFactory.create(authors=['Aname']),
            ThesisFactory.create(authors=['Bname']),
            ThesisFactory.create(authors=['Cname']),
        ]
        for thesis in theses:
            solr_client.add_document(thesis)
        url = reverse(
            'public:thesis:collection_list_per_author_name', args=(theses[0].repository.code, 'B'))
        response = Client().get(url)
        assert response.status_code == 200
        ids = {t.localidentifier for t in response.context['theses']}
        EXPECTED = {1}
        assert ids == {theses[i].id for i in EXPECTED}

    def test_embeds_the_author_first_letter_aggregation_results_into_the_context(self, solr_client):
        cache.clear()
        theses = [
            ThesisFactory.create(authors=['Aname']),
            ThesisFactory.create(authors=['Bname']),
            ThesisFactory.create(authors=['Bname']),
            ThesisFactory.create(authors=['Cname']),
            ThesisFactory.create(authors=['Cname']),
            ThesisFactory.create(authors=['Cname']),
        ]
        for thesis in theses:
            solr_client.add_document(thesis)
        url = reverse(
            'public:thesis:collection_list_per_author_name', args=(theses[0].repository.code, 'B'))
        response = Client().get(url)
        assert response.status_code == 200
        EXPECTED = [
            ('A', 1),
            ('B', 2),
            ('C', 3),
        ]
        assert response.context['other_author_letters'] == EXPECTED

    @pytest.mark.parametrize('sort_by,desc', [
        ('author_asc', False),
        ('author_desc', True),
    ])
    def test_can_sort_theses_by_author_name(self, sort_by, desc, solr_client):
        theses = [
            ThesisFactory.create(authors=['BAname']),
            ThesisFactory.create(authors=['BCname']),
            ThesisFactory.create(authors=['BBname']),
        ]
        for thesis in theses:
            solr_client.add_document(thesis)
        url = reverse(
            'public:thesis:collection_list_per_author_name', args=(theses[0].repository.code, 'B'))
        response = Client().get(url, {'sort_by': sort_by})
        assert response.status_code == 200
        ids = [t.localidentifier for t in response.context['theses']]
        EXPECTED = [0, 2, 1]
        if desc:
            EXPECTED = reversed(EXPECTED)
        assert ids == [theses[i].id for i in EXPECTED]

    @pytest.mark.parametrize('sort_by,desc', [
        ('date_asc', False),
        ('date_desc', True),
    ])
    def test_can_sort_theses_by_date(self, sort_by, desc, solr_client):
        theses = [
            ThesisFactory.create(year=2012, date_added='20120101', authors=['Bname']),
            ThesisFactory.create(year=2012, date_added='20140101', authors=['Bname']),
            ThesisFactory.create(year=2012, date_added='20120102', authors=['Bname']),
            ThesisFactory.create(year=2013, date_added='20130101', authors=['Bname']),
        ]
        for thesis in theses:
            solr_client.add_document(thesis)
        url = reverse(
            'public:thesis:collection_list_per_author_name', args=(theses[0].repository.code, 'B'))
        response = Client().get(url, {'sort_by': sort_by})
        assert response.status_code == 200
        ids = [t.localidentifier for t in response.context['theses']]
        EXPECTED = [0, 2, 1, 3]
        if desc:
            EXPECTED = reversed(EXPECTED)
        assert ids == [theses[i].id for i in EXPECTED]


class TestCitationExports:
    ALL_EXPORT_VIEWS = [
        'public:thesis:thesis_citation_enw',
        'public:thesis:thesis_citation_ris',
        'public:thesis:thesis_citation_bib',
    ]

    @pytest.mark.parametrize('view_name', ALL_EXPORT_VIEWS)
    def test_no_html_escape_in_title_and_author(self, view_name, solr_client):
        # ref support#183
        title = "ceci contient une apostroph'"
        firstname = "Jo' est mon prénom"
        lastname = "Blo' est ma condition"
        thesis = ThesisFactory.create(title=title, authors=["{}, {}".format(lastname, firstname)])
        solr_client.add_document(thesis)
        url = reverse(view_name, args=[thesis.id])
        response = Client().get(url)
        content = response.content.decode('utf-8')
        # values hasn't been mangled in the rendering process.
        assert title in content
        assert firstname in content
        assert lastname in content

    def test_no_html_escape_in_collection(self, solr_client):
        # same as test_no_html_escape_in_title_and_author but only bib has collection name
        cname = "Col'ection"
        repository = ThesisRepositoryFactory.create(name=cname)
        thesis = ThesisFactory.create(repository=repository)
        solr_client.add_document(thesis)
        url = reverse(
            'public:thesis:thesis_citation_bib',
            args=[thesis.id])
        response = Client().get(url)
        content = response.content.decode('utf-8')
        # values hasn't been mangled in the rendering process.
        assert cname in content
