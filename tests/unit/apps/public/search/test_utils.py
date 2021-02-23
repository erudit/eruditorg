import pytest

from django.http.request import QueryDict

from apps.public.search.forms import SearchForm
from apps.public.search.utils import get_search_elements


class FakeSolrData:
    def get_search_form_facets(self):
        return {
            "disciplines": [],
            "languages": [
                ("fr", "Français"),
                ("en", "Anglais"),
            ],
            "journals": [
                ("foo", "Foo"),
                ("bar", "Bar"),
            ],
        }


@pytest.mark.parametrize(
    "queryparams, expected_elements",
    [
        ("", []),
        # Languages
        ("languages=es", []),
        (
            "languages=fr",
            [
                {
                    "field": "Langues",
                    "operator": "AND",
                    "str": " ET (Langues : ['Français'])",
                    "term": "['Français']",
                }
            ],
        ),
        (
            "languages=fr&languages=en",
            [
                {
                    "field": "Langues",
                    "operator": "AND",
                    "str": " ET (Langues : ['Anglais', 'Français'])",
                    "term": "['Anglais', 'Français']",
                }
            ],
        ),
        (
            "languages=fr&languages=en&languages=es",
            [
                {
                    "field": "Langues",
                    "operator": "AND",
                    "str": " ET (Langues : ['Anglais', 'Français'])",
                    "term": "['Anglais', 'Français']",
                }
            ],
        ),
        # Journals
        ("journal=baz", []),
        (
            "journals=foo",
            [
                {
                    "field": "Revues",
                    "operator": "AND",
                    "str": " ET (Revues : ['Foo'])",
                    "term": "['Foo']",
                }
            ],
        ),
        (
            "journals=foo&journals=bar",
            [
                {
                    "field": "Revues",
                    "operator": "AND",
                    "str": " ET (Revues : ['Bar', 'Foo'])",
                    "term": "['Bar', 'Foo']",
                }
            ],
        ),
        (
            "journals=foo&journals=bar&journals=baz",
            [
                {
                    "field": "Revues",
                    "operator": "AND",
                    "str": " ET (Revues : ['Bar', 'Foo'])",
                    "term": "['Bar', 'Foo']",
                }
            ],
        ),
        # Languages & Journals
        ("languages=es&journal=baz", []),
        (
            "languages=fr&journals=foo",
            [
                {
                    "field": "Langues",
                    "operator": "AND",
                    "str": " ET (Langues : ['Français'])",
                    "term": "['Français']",
                },
                {
                    "field": "Revues",
                    "operator": "AND",
                    "str": " ET (Revues : ['Foo'])",
                    "term": "['Foo']",
                },
            ],
        ),
        (
            "languages=fr&languages=en&journals=foo&journals=bar",
            [
                {
                    "field": "Langues",
                    "operator": "AND",
                    "str": " ET (Langues : ['Anglais', 'Français'])",
                    "term": "['Anglais', 'Français']",
                },
                {
                    "field": "Revues",
                    "operator": "AND",
                    "str": " ET (Revues : ['Bar', 'Foo'])",
                    "term": "['Bar', 'Foo']",
                },
            ],
        ),
    ],
)
def test_get_search_elements(queryparams, expected_elements, monkeypatch):
    monkeypatch.setattr(SearchForm, "solr_data", FakeSolrData())
    elements = get_search_elements(
        QueryDict(queryparams),
        SearchForm(),
    )
    base_elements = [
        {
            "term": "*",
            "field": "Tous les champs",
            "operator": None,
            "str": "(Tous les champs : *)",
        },
    ]
    assert base_elements + expected_elements == elements
