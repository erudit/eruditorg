from datetime import date, timedelta

from django.utils.translation import ugettext_lazy as _
from django import forms
from django.core import urlresolvers

from crispy_forms.layout import Layout, Field, Fieldset, Div, HTML
from crispy_forms.helper import FormHelper

SORT_CHOICES = (
    ("relevance", _("Pertinance")),
    ("year", _("Année")),
    ("author", _("Auteur")),  # not indexed in Solr
    # ("title", _("Titre")),    # not indexed in Solr
)

SORT_ORDER_CHOICES = (
    ("asc", _("Croissant")),
    ("desc", _("Décroissant")),
)

OPERATORS = (
    ("AND", _("Et")),
    ("OR", _("Ou")),
    ("NOT", _("Sauf")),
)

BASIC_SEARCH_OPERATORS = (
    ("", _("")),
    ("NOT", _("Sauf")),
)

ADVANCED_SEARCH_FIELDS = (
    ("all", _("Tous les champs")),
    ("meta", _("Tous les champs (sauf texte intégral)")),
    ("full_text", _("Texte intégral")),
    ("title_abstract_keywords", _("Titre, résumé, mots-clés")),
    ("title", _("Titre")),
    ("author", _("Auteur")),
    ("author_affiliation", _("Affiliation de l'auteur")),
    ("journal_title", _("Titre de la revue")),
    ("bibliography", _("Bibliographie")),
    ("title_reviewd", _("Ouvrage recensé")),
    ("issn", _("ISSN")),
    ("isbn", _("ISBN")),
)

AVAILABILITY_CHOICES = (
    ("", ""),
    ((date.today() - timedelta(days=1)), _("1 jour")),
    ((date.today() - timedelta(days=7)), _("1 semaine")),
    ((date.today() - timedelta(days=14)), _("2 semaines")),
    ((date.today() - timedelta(days=31)), _("1 mois")),
    ((date.today() - timedelta(days=183)), _("6 mois")),
    ((date.today() - timedelta(days=365)), _("1 an")),
)

FUNDS_CHOICES = (
    ("Érudit", _("Érudit")),
    ("UNB", _("UNB (University of New-Brunswick)")),
    ("Persée", _("Persée")),
)

PUB_TYPES_CHOICES = (
    ("Article", _("Article de revue scientifique")),
    ("Culturel", _("Article de revue culturelle")),
    ("Actes", _("Actes de colloque")),
    ("Thèses", _("Thèses")),
    ("Livres", _("Livres")),
    ("Depot", _("Document déposé dans le dépôt de données (littérature grise)")),
)


def get_years_range(year_start=1900, year_end=(date.today().year + 1), reverse=False,
                    add_empty_choice=False, empty_string=""):
    if not reverse:
        years_range = [(str(year), str(year)) for year in range(year_start, year_end)]
    else:
        years_range = [(str(year), str(year)) for year in reversed(range(year_start, year_end))]

    if add_empty_choice:
        years_range.insert(0, ("", empty_string))

    return years_range


class SearchFormHelper(FormHelper):
    def __init__(self, *args, **kwargs):
        super(SearchFormHelper, self).__init__(*args, **kwargs)

        self.form_tag = False
        self.html5_required = True
        self.render_hidden_fields = True

        self.form_id = 'id-search'
        self.form_class = 'search'
        self.form_method = 'get'
        self.form_action = urlresolvers.reverse("public:search:search")

        self.layout = Layout(
            Div(
                HTML(
                    "<header class='search-header'><h3 class='h2'>%s</h3></header>" % _("Filtres")
                ),
                Fieldset(
                    "",
                    Div(
                        Div(
                            Field('basic_search_term', tabIndex=1),
                            HTML(
                                '<button type="submit"><i class="ion ion-ios-search"></i></button>'
                            ),
                            css_class="basic-search-field",
                        ),
                        Field('basic_search_operator', tabIndex=2),
                        Field('basic_search_field', tabIndex=3),
                    ),
                ),
                Fieldset(
                    "",
                    HTML(
                        '<label class="control-label akkordion-title"> \
                            %s <i class="ion-ios-arrow-down icon"></i> \
                        </label>'
                        % _("Options de recherche avancées")
                    ),
                    Div(
                        Div(
                            Field('advanced_search_operator1'),
                            Field('advanced_search_term1'),
                            Field('advanced_search_field1'),
                            css_class="search-operator show",
                        ),
                        Div(
                            Field('advanced_search_operator2'),
                            Field('advanced_search_term2'),
                            Field('advanced_search_field2'),
                            css_class="search-operator -hide",
                        ),
                        Div(
                            Field('advanced_search_operator3'),
                            Field('advanced_search_term3'),
                            Field('advanced_search_field3'),
                            css_class="search-operator -hide",
                        ),
                        Div(
                            Field('advanced_search_operator4'),
                            Field('advanced_search_term4'),
                            Field('advanced_search_field4'),
                            css_class="search-operator -hide",
                        ),
                        Div(
                            Field('advanced_search_operator5'),
                            Field('advanced_search_term5'),
                            Field('advanced_search_field5'),
                            css_class="search-operator -hide",
                        ),
                        Div(
                            Field('advanced_search_operator6'),
                            Field('advanced_search_term6'),
                            Field('advanced_search_field6'),
                            css_class="search-operator -hide",
                        ),
                        Div(
                            Field('advanced_search_operator7'),
                            Field('advanced_search_term7'),
                            Field('advanced_search_field7'),
                            css_class="search-operator -hide",
                        ),
                        Div(
                            Field('advanced_search_operator8'),
                            Field('advanced_search_term8'),
                            Field('advanced_search_field8'),
                            css_class="search-operator -hide",
                        ),
                        Div(
                            Field('advanced_search_operator9'),
                            Field('advanced_search_term9'),
                            Field('advanced_search_field9'),
                            css_class="search-operator -hide",
                        ),
                        Div(
                            Field('advanced_search_operator10'),
                            Field('advanced_search_term10'),
                            Field('advanced_search_field10'),
                            css_class="search-operator -hide",
                        ),
                        Div(
                            Field('pub_year_start'),
                            Field('pub_year_end'),
                            Field('available_since'),
                        ),
                        Div(
                            Field('funds_limit'),
                        ),
                        Div(
                            Field('pub_types'),
                        ),
                        css_class="advanced-search-fields akkordion-content",
                    ),
                    css_class="advanced-search akkordion hide",
                ),
                Fieldset(
                    "",
                    Div(
                        Field('sort'),
                        Field('sort_order'),
                    ),
                    css_class="hide",
                ),
            ),
        )


class SearchForm(forms.Form):
    page = forms.IntegerField(
        label=_("Page"), widget=forms.HiddenInput, required=False, initial=1
    )

    basic_search_operator = forms.ChoiceField(
        label=_("Inclure?"), widget=forms.Select, choices=BASIC_SEARCH_OPERATORS, required=False
    )
    basic_search_term = forms.CharField(
        label=_("Recherche"), widget=forms.TextInput, required=False,
    )
    basic_search_field = forms.ChoiceField(
        label=_("Champs"), widget=forms.Select, choices=ADVANCED_SEARCH_FIELDS, required=False
    )

    advanced_search_operator1 = forms.ChoiceField(
        label="", widget=forms.Select, choices=OPERATORS, required=False
    )
    advanced_search_term1 = forms.CharField(label="", widget=forms.TextInput, required=False, )
    advanced_search_field1 = forms.ChoiceField(
        label="", widget=forms.Select, choices=ADVANCED_SEARCH_FIELDS, required=False
    )
    advanced_search_operator2 = forms.ChoiceField(
        label="", widget=forms.Select, choices=OPERATORS, required=False
    )
    advanced_search_term2 = forms.CharField(label="", widget=forms.TextInput, required=False, )
    advanced_search_field2 = forms.ChoiceField(
        label="", widget=forms.Select, choices=ADVANCED_SEARCH_FIELDS, required=False
    )
    advanced_search_operator3 = forms.ChoiceField(
        label="", widget=forms.Select, choices=OPERATORS, required=False
    )
    advanced_search_term3 = forms.CharField(label="", widget=forms.TextInput, required=False, )
    advanced_search_field3 = forms.ChoiceField(
        label="", widget=forms.Select, choices=ADVANCED_SEARCH_FIELDS, required=False
    )
    advanced_search_operator4 = forms.ChoiceField(
        label="", widget=forms.Select, choices=OPERATORS, required=False
    )
    advanced_search_term4 = forms.CharField(label="", widget=forms.TextInput, required=False, )
    advanced_search_field4 = forms.ChoiceField(
        label="", widget=forms.Select, choices=ADVANCED_SEARCH_FIELDS, required=False
    )
    advanced_search_operator5 = forms.ChoiceField(
        label="", widget=forms.Select, choices=OPERATORS, required=False
    )
    advanced_search_term5 = forms.CharField(label="", widget=forms.TextInput, required=False, )
    advanced_search_field5 = forms.ChoiceField(
        label="", widget=forms.Select, choices=ADVANCED_SEARCH_FIELDS, required=False
    )

    pub_year_start = forms.ChoiceField(
        label=_("Publiés entre"), widget=forms.Select,
        choices=get_years_range(add_empty_choice=True), required=False
    )
    pub_year_end = forms.ChoiceField(
        label="", widget=forms.Select,
        choices=get_years_range(reverse=True, add_empty_choice=True), required=False
    )

    available_since = forms.ChoiceField(
        label=_("Dans Érudit depuis"), widget=forms.Select,
        choices=AVAILABILITY_CHOICES, required=False
    )

    funds_limit = forms.MultipleChoiceField(
        label=_("Fonds"), widget=forms.CheckboxSelectMultiple,
        choices=FUNDS_CHOICES, required=False
    )

    pub_types = forms.MultipleChoiceField(
        label=_("Types de publication"), widget=forms.CheckboxSelectMultiple,
        choices=PUB_TYPES_CHOICES, required=False
    )
    sort = forms.ChoiceField(
        label=False, widget=forms.Select, choices=SORT_CHOICES, required=False
    )
    sort_order = forms.ChoiceField(
        label=False, widget=forms.Select, choices=SORT_ORDER_CHOICES, required=False
    )

    def __init__(self, *args, **kwargs):
        super(SearchForm, self).__init__(*args, **kwargs)

        self.helper = SearchFormHelper()
