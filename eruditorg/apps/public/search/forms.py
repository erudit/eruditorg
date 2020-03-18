import datetime as dt
import structlog
import re

from django import forms
from django.utils.encoding import force_str
from django.utils.translation import gettext_lazy as _, pgettext

from erudit.models import Collection
from erudit.solr.models import get_solr_data, LANGUAGE_LABELS, SolrData
from erudit.utils import locale_aware_sort

from apps.public.search import legacy

logger = structlog.getLogger(__name__)


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


def get_funds_choices():
    db_keys = ['erudit', 'unb', 'persee']
    solr_keys = ['Érudit', 'UNB', 'Persée']

    collections = Collection.objects.filter(code__in=db_keys).order_by('id').values_list('name')
    collections = zip(solr_keys, map(lambda x: x[0], collections))

    return list(collections) + [('FRQ', _('Fonds de Recherche du Québec'))]


PUB_TYPES_CHOICES = (
    ('Article', _('Articles savants')),
    ('Culturel', _('Articles culturels')),
    ('Thèses', _('Thèses et mémoires')),
    ('Livres', _('Livres')),
    ('Actes', _('Actes')),
    ('Dépot', _('Rapports de recherche')),
)

ARTICLE_TYPES_CHOICES = (
    ('Article', _("Article")),
    ('Compte rendu', _("Compte rendu")),
    ('Autre', _("Autre")),
    ('Note', pgettext("Article Note", "Note")),
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


def build_language_filter_choices(filter_languages=None):
    """ :returns: the language choices for the Search forms"""
    language_choices = []
    filter_languages = sorted(filter_languages, key=lambda x: x[1], reverse=True)
    for v, c in filter_languages:
        try:
            assert re.match(r'^[a-zA-Z]+$', v)
            language_name = LANGUAGE_LABELS[v]
        except AssertionError:  # pragma: no cover
            continue
        except KeyError:
            language_name = v
        language_choices.append((v, "{language_name} ({c})".format(
            language_name=language_name,
            c=c
        )))
    return language_choices


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
        label=_('De…'), widget=forms.Select,
        choices=get_years_range(add_empty_choice=True), required=False)
    pub_year_end = forms.ChoiceField(
        label=_('À…'), widget=forms.Select,
        choices=get_years_range(reverse=True, add_empty_choice=True), required=False)

    available_since = forms.ChoiceField(
        label=_('Dans Érudit depuis'), widget=forms.Select, choices=AVAILABILITY_CHOICES,
        required=False)

    funds = forms.MultipleChoiceField(
        label=_('Fonds'), widget=forms.CheckboxSelectMultiple, choices=get_funds_choices,
        required=False,
        help_text=_(
            "Les revues diffusées sur Érudit sont consultables directement sur la "
            "plateforme ; les revues des collections Persée et NRC Research Press redirigent "
            "vers la plateforme du partenaire."
        ),
        initial=('Érudit', 'UNB')
    )

    publication_types = forms.MultipleChoiceField(
        label=_('Types de publication'), widget=forms.CheckboxSelectMultiple,
        choices=PUB_TYPES_CHOICES, required=False,
        help_text=_(
            "Les revues savantes publient des articles scientifiques révisés par les pairs ; "
            "les revues culturelles présentent des articles dans les domaines artistique, "
            "littéraire et socioculturel."
        ))

    article_types = forms.MultipleChoiceField(
        label=_("Types d’articles savants"), widget=forms.CheckboxSelectMultiple,
        choices=ARTICLE_TYPES_CHOICES, required=False,
        help_text=_(
            "Ces filtres s’appliquent aux articles savants uniquement."
        ))

    disciplines = forms.MultipleChoiceField(label=_('Disciplines'), required=False)
    languages = forms.MultipleChoiceField(label=_('Langues'), required=False)
    journals = forms.MultipleChoiceField(label=_('Revues'), required=False)

    @property
    def solr_data(self) -> SolrData:
        return get_solr_data()

    def __init__(self, *args, **kwargs):
        super(SearchForm, self).__init__(*args, **kwargs)

        # Update some fields
        for fkey in ['basic_search_term', 'advanced_search_term1', 'advanced_search_term2',
                     'advanced_search_term3', 'advanced_search_term4', 'advanced_search_term5']:
            self.fields[fkey].widget.attrs['placeholder'] = _('Expression ou mot-clé')

        facets = self.solr_data.get_search_form_facets()
        self.fields['disciplines'].choices = locale_aware_sort(
            facets['disciplines'],
            lambda x: x[1],
        )
        self.fields['languages'].choices = locale_aware_sort(
            facets['languages'],
            lambda x: force_str(x[1]),
        )
        self.fields['journals'].choices = locale_aware_sort(
            facets['journals'],
            lambda x: x[1],
        )

    def clean(self):
        cleaned_data = super(SearchForm, self).clean()

        # Validates publication year fields
        pub_year_start = cleaned_data.get('pub_year_start', None)
        pub_year_end = cleaned_data.get('pub_year_end', None)

        if pub_year_start and pub_year_end and int(pub_year_start) > int(pub_year_end):
            cleaned_data['pub_year_start'] = pub_year_end
            cleaned_data['pub_year_end'] = pub_year_start


class ResultsFilterForm(forms.Form):
    filter_extra_q = forms.CharField(
        label=_('Dans les résultats'), widget=forms.TextInput, required=False)
    filter_years = forms.MultipleChoiceField(label=_('Années'), required=False)
    filter_article_types = forms.MultipleChoiceField(
        label=_('Types d’articles savants'),
        help_text=_(
            "Ces filtres s’appliquent aux articles savants uniquement."
        ),
        required=False)
    filter_languages = forms.MultipleChoiceField(label=_('Langues'), required=False)
    # It is intentional to have a discrepancy between the "Revues" label and "Collections" below.
    # See #1814 for details.
    filter_collections = forms.MultipleChoiceField(label=_('Collections'), required=False)
    filter_authors = forms.MultipleChoiceField(label=_('Auteurs'), required=False)
    filter_funds = forms.MultipleChoiceField(
        label=_('Fonds'),
        help_text=_("""Les revues diffusées sur Érudit sont consultables
                    directement sur la plateforme ; les revues des collections Persée et NRC
                    Research Press redirigent vers la plateforme du partenaire."""),
        required=False)
    filter_publication_types = forms.MultipleChoiceField(
        label=_('Types de publications'),
        help_text=_("""Les revues savantes publient des articles scientifiques révisés
                    par les pairs ; les revues culturelles présentent des articles dans les
                    domaines artistique, littéraire et socioculturel."""),
        required=False)

    article_type_correspondence = {
        'Compte rendu': ['Compterendu']
    }

    language_code_correspondence = {
        'de': ['ge', 'gw', ],
        'el': ['gr', 'grc', ],
        'es': ['sp', ],
        'fr': ['un', ],
        'ru': ['uz', ],
        'en': ['zx', 've'],
        'pt': ['po', ],
    }

    def __init__(self, *args, **kwargs):
        # The filters form fields choices are initialized from search results
        api_results = kwargs.pop('api_results', {})
        aggregations = api_results.get('aggregations')
        EXPECTED_AGGREGATIONS = {
            'year', 'article_type', 'collection', 'author', 'fund', 'publication_type', 'language'}
        for expected in EXPECTED_AGGREGATIONS:
            aggregations.setdefault(expected, {})
        super(ResultsFilterForm, self).__init__(*args, **kwargs)

        self.fields['filter_extra_q'].widget.attrs['placeholder'] = _('Mots-clés')

        if aggregations:
            self.fields['filter_years'].choices = self._get_aggregation_choices(
                aggregations['year'], sort_key=lambda x: x[0], sort_reverse=True)
            self.fields['filter_years'].choices = filter(
                lambda y: re.match(r'^\d+$', y[0]), self.fields['filter_years'].choices)

            legacy.group_results_by_field_correspondence(
                aggregations,
                'article_type',
                self.article_type_correspondence
            )

            legacy.group_results_by_field_correspondence(
                aggregations,
                'language',
                self.language_code_correspondence
            )

            self.fields['filter_article_types'].choices = self._get_aggregation_choices(
                aggregations['article_type'],
                sort_key=lambda x: (x[1], x[0]),
                sort_reverse=True,
                display_names=dict(ARTICLE_TYPES_CHOICES),
            )

            # Prepares the languages fields
            language_choices = build_language_filter_choices(
                filter_languages=aggregations['language'].items()
            )

            self.fields['filter_languages'].choices = language_choices

            self.fields['filter_collections'].choices = self._get_aggregation_choices(
                aggregations['collection'],
                sort_key=lambda x: (x[1], x[0]),
                sort_reverse=True
            )
            self.fields['filter_authors'].choices = self._get_aggregation_choices(
                aggregations['author'],
                sort_key=lambda x: (x[1], x[0]),
                sort_reverse=True
            )

            funds_choices = get_funds_choices()
            funds_code = [funds[0] for funds in funds_choices]
            self.fields['filter_funds'].choices = self._get_aggregation_choices(
                aggregations['fund'],
                sort_key=lambda x: funds_code.index(x[0]) if x[0] in funds_code else -1,
                display_names=dict(funds_choices),
            )

            self.fields['filter_publication_types'].choices = self._get_aggregation_choices(
                aggregations['publication_type'],
                sort_key=lambda x: (x[1], x[0]), sort_reverse=True,
                display_names=dict(PUB_TYPES_CHOICES)
            )

    def _get_aggregation_choices(
            self, aggregation_dict, sort_key=None, sort_reverse=False, display_names=None):
        items = aggregation_dict.items()
        if sort_key:
            items = sorted(items, key=sort_key, reverse=sort_reverse)

        def get_display(v):
            if display_names:
                return display_names.get(v, v)
            else:
                return v

        return [(v, '{v} ({count})'.format(v=get_display(v), count=c)) for v, c in items]


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
