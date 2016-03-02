from django.utils.translation import ugettext_lazy as _
from django import forms
from django.core import urlresolvers

from crispy_forms.layout import Layout, Field, Fieldset, Div
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

FILTER_FIELDS = {
    "years": _("Années de publication"),
    # "article_types": _("Types d'articles"),
    "languages": _("Langues"),
    # "collections": _("Collections"),
    "authors": _("Auteurs"),
    "funds": _("Fonds"),
    "publication_types": _("Types de publication"),
}

OPERATORS = (
    ("AND", _("Et")),
    ("OR", _("Ou")),
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
                Fieldset(
                    "",
                    Div(
                        Field('search_term', tabIndex=1),
                        Field('sort', tabIndex=2),
                        Field('sort_order', tabIndex=3),
                    ),
                ),
                Fieldset(
                    _("Recherche avancée"),
                    Div(
                        Field('advanced_search_operator1'),
                        Field('advanced_search_term1'),
                        Field('advanced_search_field1'),
                    ),
                    Div(
                        Field('advanced_search_operator2'),
                        Field('advanced_search_term2'),
                        Field('advanced_search_field2'),
                    ),
                    Div(
                        Field('advanced_search_operator3'),
                        Field('advanced_search_term3'),
                        Field('advanced_search_field3'),
                    ),
                    Div(
                        Field('advanced_search_operator4'),
                        Field('advanced_search_term4'),
                        Field('advanced_search_field4'),
                    ),
                    Div(
                        Field('advanced_search_operator5'),
                        Field('advanced_search_term5'),
                        Field('advanced_search_field5'),
                    ),
                    Div(
                        Field('advanced_search_operator6'),
                        Field('advanced_search_term6'),
                        Field('advanced_search_field6'),
                    ),
                    Div(
                        Field('advanced_search_operator7'),
                        Field('advanced_search_term7'),
                        Field('advanced_search_field7'),
                    ),
                    Div(
                        Field('advanced_search_operator8'),
                        Field('advanced_search_term8'),
                        Field('advanced_search_field8'),
                    ),
                    Div(
                        Field('advanced_search_operator9'),
                        Field('advanced_search_term9'),
                        Field('advanced_search_field9'),
                    ),
                    Div(
                        Field('advanced_search_operator10'),
                        Field('advanced_search_term10'),
                        Field('advanced_search_field10'),
                    ),
                ),
            ),
        )


class SearchForm(forms.Form):
    search_term = forms.CharField(label=_("Recherche"), widget=forms.TextInput, required=False, )
    sort = forms.ChoiceField(
        label=_("Tri"), widget=forms.Select, choices=SORT_CHOICES, required=False
    )
    sort_order = forms.ChoiceField(
        label=_("Ordre"), widget=forms.Select, choices=SORT_ORDER_CHOICES, required=False
    )
    page = forms.IntegerField(label=_("Page"), widget=forms.HiddenInput, initial=1, )

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

    def __init__(self, *args, **kwargs):
        super(SearchForm, self).__init__(*args, **kwargs)

        self.helper = SearchFormHelper()
