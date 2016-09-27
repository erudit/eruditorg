# -*- coding: utf-8 -*-
import pytest
from erudit.test import BaseEruditTestCase

from apps.public.search.forms import ResultsFilterForm
from apps.public.search.forms import SearchForm


class TestSearchForm(BaseEruditTestCase):
    def test_cannot_validate_a_search_without_a_main_query(self):
        # Setup
        form_data = {}
        # Run & check
        form = SearchForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_cannot_validate_a_search_with_a_incoherent_publication_years_period(self):
        # Setup
        form_data = {
            'basic_search_term': 'test',
            'pub_year_start': 2014,
            'pub_year_end': 2012,
        }
        # Run & check
        form = SearchForm(data=form_data)
        self.assertFalse(form.is_valid())


class TestResultsFilterForm(BaseEruditTestCase):

    @pytest.fixture(autouse=True)
    def aggregation_dict(self):
        self.aggregation_dict = {
            'article_type': {
                'Article': 99,
                'Compte rendu': 1,
                'Autre': 6,
            },
            'fund': {
                'Érudit': 257
            },
            'publication_type': {
                'Article': 106,
                'Culturel': 151,
            },
            'year': {
                '2011': 36,
                '2013': 11,
            },
            'language': {
                'en': 9,
                'fr': 248
            },
            'author': {
                'test1, foo': 2,
                'test2, bar': 10,
            },
            'collection': {
                'Foo': 75,
                'Bar': 151,
            }
        }

    def test_can_initialize_years_choices_from_aggregation_results(self):
        # Run & check
        form = ResultsFilterForm(api_results={'aggregations': self.aggregation_dict})
        self.assertEqual(
            form.fields['filter_years'].choices,
            [
                ('2013', '2013 (11)'),
                ('2011', '2011 (36)'),
            ])

    def test_can_initialize_article_types_choices_from_aggregation_results(self):
        # Run & check
        form = ResultsFilterForm(api_results={'aggregations': self.aggregation_dict})

        self.assertEqual(
            form.fields['filter_article_types'].choices,
            [
                ('Article', 'Article (99)'),
                ('Autre', 'Autre (6)'),
                ('Compte rendu', 'Compte rendu (1)'),
            ])

    def test_can_initialize_and_aggregate_article_types_choices_from_aggregation_results(self):
        # Run & chec
        import copy
        ag_dict = copy.copy(self.aggregation_dict)
        ag_dict['article_type']['Compterendu'] = 1
        form = ResultsFilterForm(api_results={'aggregations': ag_dict})

        self.assertEqual(
            form.fields['filter_article_types'].choices,
            [
                ('Article', 'Article (99)'),
                ('Autre', 'Autre (6)'),
                ('Compte rendu', 'Compte rendu (2)'),
            ])

    def test_can_initialize_languages_choices_from_aggregation_results(self):
        # Run & check
        form = ResultsFilterForm(api_results={'aggregations': self.aggregation_dict})
        self.assertEqual(
            form.fields['filter_languages'].choices,
            [
                ('en', 'Anglais (9)'),
                ('fr', 'Français (248)'),
            ])

    def test_can_initialize_collections_choices_from_aggregation_results(self):
        # Run & check
        form = ResultsFilterForm(api_results={'aggregations': self.aggregation_dict})
        self.assertEqual(
            form.fields['filter_collections'].choices,
            [
                ('Bar', 'Bar (151)'),
                ('Foo', 'Foo (75)'),
            ])

    def test_can_initialize_authors_choices_from_aggregation_results(self):
        # Run & check
        form = ResultsFilterForm(api_results={'aggregations': self.aggregation_dict})
        self.assertEqual(
            form.fields['filter_authors'].choices,
            [
                ('test1, foo', 'test1, foo (2)'),
                ('test2, bar', 'test2, bar (10)'),
            ])

    def test_can_initialize_funds_choices_from_aggregation_results(self):
        # Run & check
        form = ResultsFilterForm(api_results={'aggregations': self.aggregation_dict})
        self.assertEqual(
            form.fields['filter_funds'].choices,
            [
                ('Érudit', 'Érudit (257)'),
            ])

    def test_can_initialize_publication_types_choices_from_aggregation_results(self):
        # Run & check
        form = ResultsFilterForm(api_results={'aggregations': self.aggregation_dict})
        self.assertEqual(
            form.fields['filter_publication_types'].choices,
            [
                ('Article', 'Article (106)'),
                ('Culturel', 'Culturel (151)'),
            ])
