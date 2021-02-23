import pytest

from erudit.test.factories import CollectionFactory
from erudit.test.solr import FakeSolrData
from apps.public.search.forms import ResultsFilterForm
from apps.public.search.forms import SearchForm

pytestmark = pytest.mark.django_db


class TestSearchForm:
    @pytest.fixture(autouse=True)
    def search_form_solr_data(self, monkeypatch):
        monkeypatch.setattr(SearchForm, "solr_data", FakeSolrData())

    def test_cannot_validate_a_search_without_a_main_query(self):
        form_data = {}
        form = SearchForm(data=form_data)
        assert not form.is_valid()

    def test_can_be_lenient_with_incoherent_publication_years_period(self):
        form_data = {
            "basic_search_term": "test",
            "pub_year_start": 2014,
            "pub_year_end": 2012,
        }
        form = SearchForm(data=form_data)
        assert form.is_valid()
        assert form.cleaned_data["pub_year_start"] == "2012"
        assert form.cleaned_data["pub_year_end"] == "2014"


class TestResultsFilterForm:
    @pytest.fixture(autouse=True)
    def setUp(self):
        CollectionFactory(code="erudit", name="Érudit")
        self.aggregation_dict = {
            "article_type": {
                "Article": 99,
                "Compte rendu": 1,
                "Autre": 6,
            },
            "fund": {"Érudit": 257},
            "publication_type": {
                "Article": 106,
                "Culturel": 151,
            },
            "year": {
                "2011": 36,
                "2013": 11,
            },
            "language": {"en": 9, "fr": 248},
            "author": {
                "test1, foo": 2,
                "test2, bar": 10,
            },
            "collection": {
                "Foo": 75,
                "Bar": 151,
            },
        }

    def test_can_initialize_years_choices_from_aggregation_results(self):
        form = ResultsFilterForm(api_results={"aggregations": self.aggregation_dict})

        EXPECTED = [
            ("2013", "2013 (11)"),
            ("2011", "2011 (36)"),
        ]
        assert form.fields["filter_years"].choices == EXPECTED

    def test_can_initialize_article_types_choices_from_aggregation_results(self):
        # Run & check
        form = ResultsFilterForm(api_results={"aggregations": self.aggregation_dict})

        EXPECTED = [
            ("Article", "Article (99)"),
            ("Autre", "Autre (6)"),
            ("Compte rendu", "Compte rendu (1)"),
        ]
        assert form.fields["filter_article_types"].choices == EXPECTED

    def test_can_initialize_and_aggregate_article_types_choices_from_aggregation_results(self):
        ag_dict = dict(self.aggregation_dict)
        ag_dict["article_type"]["Compterendu"] = 1
        form = ResultsFilterForm(api_results={"aggregations": ag_dict})
        EXPECTED = [
            ("Article", "Article (99)"),
            ("Autre", "Autre (6)"),
            ("Compte rendu", "Compte rendu (2)"),
        ]
        assert form.fields["filter_article_types"].choices == EXPECTED

    def test_can_initialize_languages_choices_from_aggregation_results(self):
        form = ResultsFilterForm(api_results={"aggregations": self.aggregation_dict})

        EXPECTED = [
            ("fr", "Français (248)"),
            ("en", "Anglais (9)"),
        ]
        assert form.fields["filter_languages"].choices == EXPECTED

    def test_can_initialize_collections_choices_from_aggregation_results(self):
        form = ResultsFilterForm(api_results={"aggregations": self.aggregation_dict})
        EXPECTED = [
            ("Bar", "Bar (151)"),
            ("Foo", "Foo (75)"),
        ]
        assert form.fields["filter_collections"].choices == EXPECTED

    def test_can_initialize_authors_choices_from_aggregation_results(self):
        form = ResultsFilterForm(api_results={"aggregations": self.aggregation_dict})
        EXPECTED = [
            ("test2, bar", "test2, bar (10)"),
            ("test1, foo", "test1, foo (2)"),
        ]
        assert form.fields["filter_authors"].choices == EXPECTED

    def test_can_initialize_funds_choices_from_aggregation_results(self):
        form = ResultsFilterForm(api_results={"aggregations": self.aggregation_dict})
        EXPECTED = [
            ("Érudit", "Érudit (257)"),
        ]
        assert form.fields["filter_funds"].choices == EXPECTED

    def test_can_initialize_publication_types_choices_from_aggregation_results(self):
        form = ResultsFilterForm(api_results={"aggregations": self.aggregation_dict})
        EXPECTED = [
            ("Culturel", "Articles culturels (151)"),
            ("Article", "Articles savants (106)"),
        ]
        assert form.fields["filter_publication_types"].choices == EXPECTED
