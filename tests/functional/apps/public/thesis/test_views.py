import pytest
from django.core.urlresolvers import reverse
from django.core.cache import cache
from django.test import Client

from erudit.test.factories import (
    AuthorFactory, CollectionFactory, ThesisFactory, ThesisProviderFactory
)

pytestmark = pytest.mark.django_db


class TestThesisHomeView:
    def test_inserts_collection_information_into_the_context(self, solr_client):
        author = AuthorFactory.create()
        provider1 = ThesisProviderFactory.create()
        provider2 = ThesisProviderFactory.create()
        thesis_1 = ThesisFactory.create(
            localidentifier='thesis-1', author=author, publication_year=2010)
        solr_client.add_thesis(thesis_1, collection=provider1.solr_name)
        thesis_2 = ThesisFactory.create(
            localidentifier='thesis-2', author=author, publication_year=2012)
        solr_client.add_thesis(thesis_2, collection=provider1.solr_name)
        thesis_3 = ThesisFactory.create(
            localidentifier='thesis-3', author=author, publication_year=2013)
        solr_client.add_thesis(thesis_3, collection=provider1.solr_name)
        thesis_4 = ThesisFactory.create(
            localidentifier='thesis-4', author=author, publication_year=2014)
        solr_client.add_thesis(thesis_4, collection=provider1.solr_name)
        thesis_5 = ThesisFactory.create(  # noqa
            localidentifier='thesis-5', author=author, publication_year=2010)
        solr_client.add_thesis(thesis_5, collection=provider2.solr_name)
        thesis_6 = ThesisFactory.create(
            localidentifier='thesis-6', author=author, publication_year=2012)
        solr_client.add_thesis(thesis_6, collection=provider2.solr_name)
        thesis_7 = ThesisFactory.create(
            localidentifier='thesis-7', author=author, publication_year=2013)
        solr_client.add_thesis(thesis_7, collection=provider2.solr_name)
        thesis_8 = ThesisFactory.create(
            localidentifier='thesis-8', author=author, publication_year=2014)
        solr_client.add_thesis(thesis_8, collection=provider2.solr_name)
        url = reverse('public:thesis:home')
        response = Client().get(url)
        assert response.status_code == 200
        assert 'provider_summaries' in response.context
        assert len(response.context['provider_summaries']) == 2
        assert response.context['provider_summaries'][0]['thesis_count'] == 4
        assert response.context['provider_summaries'][1]['thesis_count'] == 4
        ids = [
            t.localidentifier for t in
            response.context['provider_summaries'][0]['recent_theses']]
        assert ids == [thesis_4.solr_id, thesis_3.solr_id, thesis_2.solr_id, ]
        ids = [
            t.localidentifier for t in
            response.context['provider_summaries'][1]['recent_theses']]
        assert ids == [thesis_8.solr_id, thesis_7.solr_id, thesis_6.solr_id, ]


class TestThesisCollectionHomeView:
    def test_inserts_the_recent_theses_into_the_context(self, solr_client):
        author = AuthorFactory.create()
        provider = ThesisProviderFactory.create()
        thesis_1 = ThesisFactory.create(
            localidentifier='thesis-1', author=author, publication_year=2010)
        solr_client.add_thesis(thesis_1, collection=provider.solr_name)
        thesis_2 = ThesisFactory.create(
            localidentifier='thesis-2', author=author, publication_year=2012)
        solr_client.add_thesis(thesis_2, collection=provider.solr_name)
        thesis_3 = ThesisFactory.create(
            localidentifier='thesis-3', author=author, publication_year=2013)
        solr_client.add_thesis(thesis_3, collection=provider.solr_name)
        thesis_4 = ThesisFactory.create(
            localidentifier='thesis-4', author=author, publication_year=2014)
        solr_client.add_thesis(thesis_4, collection=provider.solr_name)
        url = reverse('public:thesis:collection_home', args=(provider.code, ))
        response = Client().get(url)
        assert response.status_code == 200
        ids = [t.localidentifier for t in response.context['recent_theses']]
        assert ids == [thesis_4.solr_id, thesis_3.solr_id, thesis_2.solr_id, ]

    def test_inserts_the_thesis_count_into_the_context(self, solr_client):
        cache.clear()
        author = AuthorFactory.create()
        provider = ThesisProviderFactory.create()
        thesis_1 = ThesisFactory.create(
            localidentifier='thesis-1', author=author, publication_year=2010)
        solr_client.add_thesis(thesis_1, collection=provider.solr_name)
        thesis_2 = ThesisFactory.create(
            localidentifier='thesis-2', author=author, publication_year=2012)
        solr_client.add_thesis(thesis_2, collection=provider.solr_name)
        thesis_3 = ThesisFactory.create(
            localidentifier='thesis-3', author=author, publication_year=2013)
        solr_client.add_thesis(thesis_3, collection=provider.solr_name)
        thesis_4 = ThesisFactory.create(
            localidentifier='thesis-4', author=author, publication_year=2014)
        solr_client.add_thesis(thesis_4, collection=provider.solr_name)
        url = reverse('public:thesis:collection_home', args=(provider.code, ))
        response = Client().get(url)
        assert response.status_code == 200
        assert response.context['thesis_count'] == 4

    def test_inserts_the_thesis_counts_grouped_by_publication_years(self, solr_client):
        cache.clear()
        author = AuthorFactory.create()
        provider = ThesisProviderFactory.create()
        thesis_1 = ThesisFactory.create(
            localidentifier='thesis-1', author=author, publication_year=2010)
        solr_client.add_thesis(thesis_1, collection=provider.solr_name)
        thesis_2 = ThesisFactory.create(
            localidentifier='thesis-2', author=author, publication_year=2012)
        solr_client.add_thesis(thesis_2, collection=provider.solr_name)
        thesis_3 = ThesisFactory.create(
            localidentifier='thesis-3', author=author, publication_year=2013)
        solr_client.add_thesis(thesis_3, collection=provider.solr_name)
        thesis_4 = ThesisFactory.create(
            localidentifier='thesis-4', author=author, publication_year=2014)
        solr_client.add_thesis(thesis_4, collection=provider.solr_name)
        thesis_5 = ThesisFactory.create(
            localidentifier='thesis-5', author=author, publication_year=2012)
        solr_client.add_thesis(thesis_5, collection=provider.solr_name)
        thesis_6 = ThesisFactory.create(
            localidentifier='thesis-6', author=author, publication_year=2012)
        solr_client.add_thesis(thesis_6, collection=provider.solr_name)
        thesis_7 = ThesisFactory.create(
            localidentifier='thesis-7', author=author, publication_year=2014)
        solr_client.add_thesis(thesis_7, collection=provider.solr_name)
        url = reverse('public:thesis:collection_home', args=(provider.code, ))
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
        author_1 = AuthorFactory.create(lastname='Aname')
        author_2 = AuthorFactory.create(lastname='Bname')
        author_3 = AuthorFactory.create(lastname='Cname')
        author_4 = AuthorFactory.create(lastname='Dname')
        provider = ThesisProviderFactory.create()
        thesis_1 = ThesisFactory.create(
            localidentifier='thesis-1', author=author_1)
        solr_client.add_thesis(thesis_1, collection=provider.solr_name)
        thesis_2 = ThesisFactory.create(
            localidentifier='thesis-2', author=author_2)
        solr_client.add_thesis(thesis_2, collection=provider.solr_name)
        thesis_3 = ThesisFactory.create(
            localidentifier='thesis-3', author=author_3)
        solr_client.add_thesis(thesis_3, collection=provider.solr_name)
        thesis_4 = ThesisFactory.create(
            localidentifier='thesis-4', author=author_4)
        solr_client.add_thesis(thesis_4, collection=provider.solr_name)
        thesis_5 = ThesisFactory.create(
            localidentifier='thesis-5', author=author_2)
        solr_client.add_thesis(thesis_5, collection=provider.solr_name)
        thesis_6 = ThesisFactory.create(
            localidentifier='thesis-6', author=author_2)
        solr_client.add_thesis(thesis_6, collection=provider.solr_name)
        thesis_7 = ThesisFactory.create(
            localidentifier='thesis-7', author=author_4)
        solr_client.add_thesis(thesis_7, collection=provider.solr_name)
        url = reverse('public:thesis:collection_home', args=(provider.code, ))
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
        provider = ThesisProviderFactory.create()
        theses = [
            ThesisFactory.create(publication_year=2010),
            ThesisFactory.create(publication_year=2012),
            ThesisFactory.create(publication_year=2013),
            ThesisFactory.create(publication_year=2014),
            ThesisFactory.create(publication_year=2012),
            ThesisFactory.create(publication_year=2012),
            ThesisFactory.create(publication_year=2014),
        ]
        for thesis in theses:
            solr_client.add_thesis(thesis, collection=provider.solr_name)

        url = reverse('public:thesis:collection_list_per_year', args=(provider.code, 2012))
        response = Client().get(url)
        assert response.status_code == 200
        ids = {t.localidentifier for t in response.context['theses']}
        EXPECTED = {1, 4, 5}
        assert ids == {theses[i].solr_id for i in EXPECTED}

    def test_embeds_the_publication_years_aggregation_results_into_the_context(self, solr_client):
        cache.clear()
        provider = ThesisProviderFactory.create()
        theses = [
            ThesisFactory.create(publication_year=2010),
            ThesisFactory.create(publication_year=2012),
            ThesisFactory.create(publication_year=2013),
            ThesisFactory.create(publication_year=2014),
            ThesisFactory.create(publication_year=2012),
            ThesisFactory.create(publication_year=2012),
            ThesisFactory.create(publication_year=2014),
        ]
        for thesis in theses:
            solr_client.add_thesis(thesis, collection=provider.solr_name)

        url = reverse('public:thesis:collection_list_per_year', args=(provider.code, 2012))
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
        author_1 = AuthorFactory.create(lastname='Aname')
        author_2 = AuthorFactory.create(lastname='Cname')
        author_3 = AuthorFactory.create(lastname='Bname')
        provider = ThesisProviderFactory.create()
        theses = [
            ThesisFactory.create(publication_year=2012, author=author_1),
            ThesisFactory.create(publication_year=2012, author=author_2),
            ThesisFactory.create(publication_year=2012, author=author_3),
        ]
        for thesis in theses:
            solr_client.add_thesis(thesis, collection=provider.solr_name)
        url = reverse('public:thesis:collection_list_per_year', args=(provider.code, 2012))
        response = Client().get(url, {'sort_by': sort_by})
        assert response.status_code == 200
        ids = [t.localidentifier for t in response.context['theses']]
        EXPECTED = [0, 2, 1]
        if desc:
            EXPECTED = reversed(EXPECTED)
        assert ids == [theses[i].solr_id for i in EXPECTED]

    @pytest.mark.parametrize('sort_by,desc', [
        ('date_asc', False),
        ('date_desc', True),
    ])
    def test_can_sort_theses_by_date(self, sort_by, desc, solr_client):
        provider = ThesisProviderFactory.create()
        thesis_attrs = [
            (2012, '20120101'),
            (2012, '20140101'),
            (2012, '20120102'),
        ]
        theses = []
        for publication_year, date_added in thesis_attrs:
            thesis = ThesisFactory.create(publication_year=publication_year)
            theses.append(thesis)
            solr_client.add_thesis(thesis, collection=provider.solr_name, date_added=date_added)
        url = reverse('public:thesis:collection_list_per_year', args=(provider.code, 2012))
        response = Client().get(url, {'sort_by': sort_by})
        assert response.status_code == 200
        ids = [t.localidentifier for t in response.context['theses']]
        EXPECTED = [0, 2, 1]
        if desc:
            EXPECTED = reversed(EXPECTED)
        assert ids == [theses[i].solr_id for i in EXPECTED]


class TestThesisPublicationAuthorNameListView:
    def test_returns_only_theses_for_a_given_author_first_letter(self, solr_client):
        author_1 = AuthorFactory.create(lastname='Aname')
        author_2 = AuthorFactory.create(lastname='Bname')
        author_3 = AuthorFactory.create(lastname='Cname')
        provider = ThesisProviderFactory.create()
        theses = [
            ThesisFactory.create(author=author_1),
            ThesisFactory.create(author=author_2),
            ThesisFactory.create(author=author_3),
        ]
        for thesis in theses:
            solr_client.add_thesis(thesis, collection=provider.solr_name)
        url = reverse('public:thesis:collection_list_per_author_name', args=(provider.code, 'B'))
        response = Client().get(url)
        assert response.status_code == 200
        ids = {t.localidentifier for t in response.context['theses']}
        EXPECTED = {1}
        assert ids == {theses[i].solr_id for i in EXPECTED}

    def test_embeds_the_author_first_letter_aggregation_results_into_the_context(self, solr_client):
        cache.clear()
        author_1 = AuthorFactory.create(lastname='Aname')
        author_2 = AuthorFactory.create(lastname='Bname')
        author_3 = AuthorFactory.create(lastname='Cname')
        provider = ThesisProviderFactory.create()
        theses = [
            ThesisFactory.create(author=author_1),
            ThesisFactory.create(author=author_2),
            ThesisFactory.create(author=author_2),
            ThesisFactory.create(author=author_3),
            ThesisFactory.create(author=author_3),
            ThesisFactory.create(author=author_3),
        ]
        for thesis in theses:
            solr_client.add_thesis(thesis, collection=provider.solr_name)
        url = reverse('public:thesis:collection_list_per_author_name', args=(provider.code, 'B'))
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
        author_1 = AuthorFactory.create(lastname='BAname')
        author_2 = AuthorFactory.create(lastname='BCname')
        author_3 = AuthorFactory.create(lastname='BBname')
        provider = ThesisProviderFactory.create()
        theses = [
            ThesisFactory.create(author=author_1),
            ThesisFactory.create(author=author_2),
            ThesisFactory.create(author=author_3),
        ]
        for thesis in theses:
            solr_client.add_thesis(thesis, collection=provider.solr_name)
        url = reverse('public:thesis:collection_list_per_author_name', args=(provider.code, 'B'))
        response = Client().get(url, {'sort_by': sort_by})
        assert response.status_code == 200
        ids = [t.localidentifier for t in response.context['theses']]
        EXPECTED = [0, 2, 1]
        if desc:
            EXPECTED = reversed(EXPECTED)
        assert ids == [theses[i].solr_id for i in EXPECTED]

    @pytest.mark.parametrize('sort_by,desc', [
        ('date_asc', False),
        ('date_desc', True),
    ])
    def test_can_sort_theses_by_date(self, sort_by, desc, solr_client):
        author = AuthorFactory.create(lastname='Bname')
        provider = ThesisProviderFactory.create()
        thesis_attrs = [
            (2012, '20120101'),
            (2012, '20140101'),
            (2012, '20120102'),
            (2013, '20130101'),
        ]
        theses = []
        for publication_year, date_added in thesis_attrs:
            thesis = ThesisFactory.create(publication_year=publication_year, author=author)
            theses.append(thesis)
            solr_client.add_thesis(thesis, collection=provider.solr_name, date_added=date_added)
        url = reverse('public:thesis:collection_list_per_author_name', args=(provider.code, 'B'))
        response = Client().get(url, {'sort_by': sort_by})
        assert response.status_code == 200
        ids = [t.localidentifier for t in response.context['theses']]
        EXPECTED = [0, 2, 1, 3]
        if desc:
            EXPECTED = reversed(EXPECTED)
        assert ids == [theses[i].solr_id for i in EXPECTED]


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
        author = AuthorFactory.create(lastname=lastname, firstname=firstname)
        thesis = ThesisFactory.create(title=title, author=author)
        solr_client.add_thesis(thesis)
        url = reverse(view_name, args=[thesis.solr_id])
        response = Client().get(url)
        content = response.content.decode('utf-8')
        # values hasn't been mangled in the rendering process.
        assert title in content
        assert firstname in content
        assert lastname in content

    def test_no_html_escape_in_collection(self, solr_client):
        # same as test_no_html_escape_in_title_and_author but only bib has collection name
        cname = "Col'ection"
        collection = CollectionFactory.create(name=cname)
        thesis = ThesisFactory.create(collection=collection)
        solr_client.add_thesis(thesis)
        url = reverse(
            'public:thesis:thesis_citation_bib',
            args=[thesis.solr_id])
        response = Client().get(url)
        content = response.content.decode('utf-8')
        # values hasn't been mangled in the rendering process.
        assert cname in content
