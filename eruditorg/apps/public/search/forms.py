# -*- coding: utf-8 -*-

import datetime as dt
import re

from django import forms
from django.utils.translation import ugettext_lazy as _

from erudit.models import Discipline
from erudit.models import Journal

from apps.public.search import legacy

OPERATORS = (
    ('AND', _('Et')),
    ('OR', _('Ou')),
    ('NOT', _('Sauf')),
)

ADVANCED_SEARCH_FIELDS = (
    ('all', _('Tous les champs')),
    ('meta', _('Tous les champs (sauf texte intégral)')),
    ('full_text', _('Texte intégral')),
    ('title_abstract_keywords', _('Titre, résumé, mots-clés')),
    ('title', _('Titre')),
    ('author', _('Auteur')),
    ('author_affiliation', _("Affiliation de l'auteur")),
    ('journal_title', _('Titre de la revue')),
    ('bibliography', _('Bibliographie')),
    ('title_reviewd', _('Ouvrage recensé')),
    ('issn', _('ISSN')),
    ('isbn', _('ISBN')),
)

AVAILABILITY_CHOICES = (
    ('', ''),
    ((dt.date.today() - dt.timedelta(days=1)), _('1 jour')),
    ((dt.date.today() - dt.timedelta(days=7)), _('1 semaine')),
    ((dt.date.today() - dt.timedelta(days=14)), _('2 semaines')),
    ((dt.date.today() - dt.timedelta(days=31)), _('1 mois')),
    ((dt.date.today() - dt.timedelta(days=183)), _('6 mois')),
    ((dt.date.today() - dt.timedelta(days=365)), _('1 an')),
)

FUNDS_CHOICES = (
    ('Érudit', _('Érudit')),
    ('Persée', _('Persée')),
    ('UNB', _('UNB Libraries')),
    ('NRC', _('NRC Research Press')),
)

PUB_TYPES_CHOICES = (
    ('Article', _('Articles savants')),
    ('Culturel', _('Articles culturels')),
    ('Thèses', _('Thèses')),
    ('Livres', _('Livres')),
    ('Actes', _('Actes')),
    ('Depot', _('Littérature grise')),
)


def get_years_range(
        year_start=1900, year_end=(dt.date.today().year + 1), reverse=False, add_empty_choice=False,
        empty_string=''):
    if not reverse:
        years_range = [(str(year), str(year)) for year in range(year_start, year_end)]
    else:
        years_range = [(str(year), str(year)) for year in reversed(range(year_start, year_end))]

    if add_empty_choice:
        years_range.insert(0, ('', empty_string))

    return years_range


class SearchForm(forms.Form):
    basic_search_term = forms.CharField(label=_('Recherche'), widget=forms.TextInput)
    basic_search_field = forms.ChoiceField(
        label=_('Inclure les champs'), widget=forms.Select, choices=ADVANCED_SEARCH_FIELDS,
        required=False)

    advanced_search_operator1 = forms.ChoiceField(
        label=None, widget=forms.Select, choices=OPERATORS, required=False)
    advanced_search_term1 = forms.CharField(label=None, widget=forms.TextInput, required=False)
    advanced_search_field1 = forms.ChoiceField(
        label=None, widget=forms.Select, choices=ADVANCED_SEARCH_FIELDS, required=False)
    advanced_search_operator2 = forms.ChoiceField(
        label=None, widget=forms.Select, choices=OPERATORS, required=False)
    advanced_search_term2 = forms.CharField(label=None, widget=forms.TextInput, required=False)
    advanced_search_field2 = forms.ChoiceField(
        label=None, widget=forms.Select, choices=ADVANCED_SEARCH_FIELDS, required=False)
    advanced_search_operator3 = forms.ChoiceField(
        label=None, widget=forms.Select, choices=OPERATORS, required=False)
    advanced_search_term3 = forms.CharField(label="", widget=forms.TextInput, required=False)
    advanced_search_field3 = forms.ChoiceField(
        label=None, widget=forms.Select, choices=ADVANCED_SEARCH_FIELDS, required=False)
    advanced_search_operator4 = forms.ChoiceField(
        label=None, widget=forms.Select, choices=OPERATORS, required=False)
    advanced_search_term4 = forms.CharField(label=None, widget=forms.TextInput, required=False)
    advanced_search_field4 = forms.ChoiceField(
        label=None, widget=forms.Select, choices=ADVANCED_SEARCH_FIELDS, required=False)
    advanced_search_operator5 = forms.ChoiceField(
        label=None, widget=forms.Select, choices=OPERATORS, required=False)
    advanced_search_term5 = forms.CharField(label=None, widget=forms.TextInput, required=False)
    advanced_search_field5 = forms.ChoiceField(
        label=None, widget=forms.Select, choices=ADVANCED_SEARCH_FIELDS, required=False)

    pub_year_start = forms.ChoiceField(
        label=_('Publiés entre'), widget=forms.Select,
        choices=get_years_range(add_empty_choice=True), required=False)
    pub_year_end = forms.ChoiceField(
        label=None, widget=forms.Select,
        choices=get_years_range(reverse=True, add_empty_choice=True), required=False)

    available_since = forms.ChoiceField(
        label=_('Dans Érudit depuis'), widget=forms.Select, choices=AVAILABILITY_CHOICES,
        required=False)

    funds = forms.MultipleChoiceField(
        label=_('Fonds'), widget=forms.CheckboxSelectMultiple, choices=FUNDS_CHOICES,
        required=False)

    publication_types = forms.MultipleChoiceField(
        label=_('Types de publication'), widget=forms.CheckboxSelectMultiple,
        choices=PUB_TYPES_CHOICES, required=False)

    languages = forms.MultipleChoiceField(
        label=_('Langues'),
        choices=[('fr', _('Français')), ('en', _('Anglais')), ('es', _('Espagnol'))],
        required=False)

    disciplines = forms.MultipleChoiceField(label=_('Disciplines'), required=False)

    journals = forms.MultipleChoiceField(label=_('Revues'), required=False)

    def __init__(self, *args, **kwargs):
        super(SearchForm, self).__init__(*args, **kwargs)

        # Update some fields
        for fkey in ['basic_search_term', 'advanced_search_term1', 'advanced_search_term2',
                     'advanced_search_term3', 'advanced_search_term4', 'advanced_search_term5']:
            self.fields[fkey].widget.attrs['placeholder'] = _('Expression ou mot-clé')

        self.fields['disciplines'].choices = [(d.name_fr, d.name) for d in Discipline.objects.all()]
        self.fields['journals'].choices = [(j.name_fr, j.name) for j in Journal.objects.all()]

    def clean(self):
        cleaned_data = super(SearchForm, self).clean()

        # Validates publication year fields
        pub_year_start = cleaned_data.get('pub_year_start', None)
        pub_year_end = cleaned_data.get('pub_year_end', None)
        if pub_year_start and pub_year_end and int(pub_year_start) > int(pub_year_end):
            self.add_error('pub_year_start', _('Cette intervalle est incorrecte'))


class ResultsFilterForm(forms.Form):
    filter_extra_q = forms.CharField(
        label=_('Dans les résultats'), widget=forms.TextInput, required=False)
    filter_years = forms.MultipleChoiceField(label=_('Années'), required=False)
    filter_article_types = forms.MultipleChoiceField(label=_('Types d\'articles'), required=False)
    filter_languages = forms.MultipleChoiceField(label=_('Langues'), required=False)
    filter_collections = forms.MultipleChoiceField(label=_('Collections'), required=False)
    filter_authors = forms.MultipleChoiceField(label=_('Auteurs'), required=False)
    filter_funds = forms.MultipleChoiceField(
        label=_('Fonds'), help_text=_('Identifie le fond duquel le document fait partie'),
        required=False)
    filter_publication_types = forms.MultipleChoiceField(
        label=_('Types de publications'),
        help_text=_('Identifie le corpus duquel le document fait partie'), required=False)

    article_type_correspondence = {
        'Compte rendu': ['Compterendu']
    }

    languages_correspondence = {
        'ar': _('Arabe'),
        'ca': _('Catalan'),
        'en': _('Anglais'),
        'es': _('Espagnol'),
        'de': _('Allemand'),
        'el': _('Grec moderne'),
        'fr': _('Français'),
        'he': _('Hébreu'),
        'ht': _('Créole haïtien'),
        'iro': _('Langues iroquoiennes'),
        'it': _('Italien'),
        'ja': _('Japonais'),
        'ko': _('Coréen'),
        'la': _('Latin'),
        'pt': _('Portugais'),
        'ro': _('Roumain'),
        'ru': _('Russe'),
        'zh': _('Chinois'),
    }

    def __init__(self, *args, **kwargs):
        # The filters form fields choices are initialized from search results
        api_results = kwargs.pop('api_results', {})
        aggregations = api_results.get('aggregations')
        super(ResultsFilterForm, self).__init__(*args, **kwargs)

        self.fields['filter_extra_q'].widget.attrs['placeholder'] = _('Mots-clés')

        if aggregations:
            self.fields['filter_years'].choices = self._get_aggregation_choices(
                aggregations['year'])
            self.fields['filter_years'].choices = filter(
                lambda y: re.match(r'^\d+$', y[0]), self.fields['filter_years'].choices)

            legacy.group_results_by_field_correspondence(
                aggregations,
                'article_type',
                self.article_type_correspondence
            )

            self.fields['filter_article_types'].choices = self._get_aggregation_choices(
                aggregations['article_type']
            )

            # Prepares the languages fields
            language_choices = []
            for v, c in aggregations['language'].items():
                try:
                    assert re.match(r'^[a-zA-Z]+$', v)
                    language_name = self.languages_correspondence[v]
                    language_choices.append((v, '{v} ({count})'.format(v=language_name, count=c)))
                except AssertionError:  # pragma: no cover
                    continue
                except KeyError:
                    continue

            self.fields['filter_languages'].choices = sorted(language_choices, key=lambda x: x[0])
            self.fields['filter_collections'].choices = self._get_aggregation_choices(
                aggregations['collection'])
            self.fields['filter_authors'].choices = self._get_aggregation_choices(
                aggregations['author'])
            self.fields['filter_funds'].choices = self._get_aggregation_choices(
                aggregations['fund'])
            self.fields['filter_publication_types'].choices = self._get_aggregation_choices(
                aggregations['publication_type'])

    def _get_aggregation_choices(self, aggregation_dict):
        return sorted([
            (v, '{v} ({count})'.format(v=v, count=c)) for v, c in aggregation_dict.items()],
            key=lambda x: x[0])


class ResultsOptionsForm(forms.Form):
    page_size = forms.ChoiceField(
        label=_('Résultats par page'), choices=[(x, x) for x in (10, 25, 50)], required=False)
    sort_by = forms.ChoiceField(
        label=_('Trier par...'),
        choices=[
            ('relevance', _('Pertinence')),
            ('title_asc', _('Titre (A–Z)')),
            ('title_desc', _('Titre (Z–A)')),
            ('author_asc', _('Premier auteur (A–Z)')),
            ('author_desc', _('Premier auteur (Z–A)')),
            ('pubdate_asc', _('Date de publication (croissant)')),
            ('pubdate_desc', _('Date de publication (décroissant)')),
        ], required=False)
