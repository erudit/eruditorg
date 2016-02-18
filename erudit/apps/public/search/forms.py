from django.utils.translation import ugettext_lazy as _
from django import forms
from django.core import urlresolvers

from crispy_forms.layout import Layout, Field, Fieldset, Div, Submit
from crispy_forms.helper import FormHelper
from crispy_forms.bootstrap import FormActions

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


class SearchFormHelper(FormHelper):
    def __init__(self, *args, **kwargs):
        super(SearchFormHelper, self).__init__(*args, **kwargs)

        self.form_tag = True
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
                        Field('page', tabIndex=4),
                    ),
                ),

                Fieldset(
                    _("Filtrer les résultats"),
                    Div(
                        Field('years_filter', tabIndex=5),
                        Field('languages_filter', tabIndex=6),
                        Field('authors_filter', tabIndex=7),
                        Field('funds_filter', tabIndex=8),
                        Field('publication_types_filter', tabIndex=9),
                    ),
                ),
            ),
            FormActions(
                Submit('submit', _("Recherche"), css_class='btn btn-primary'),
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
    # page = forms.IntegerField(label=_("Page"), widget=forms.HiddenInput, initial=1, )
    page = forms.IntegerField(label=_("Page"), widget=forms.TextInput, required=False, initial=1, )

    # years_filter = forms.MultipleChoiceField(label=_("Années de publication"), choices={}, widget=forms.CheckboxSelectMultiple, required=False, )  # noqa
    # languages_filter = forms.MultipleChoiceField(label=_("Langues"), choices={}, widget=forms.CheckboxSelectMultiple, required=False, )  # noqa
    # authors_filter = forms.MultipleChoiceField(label=_("Auteurs"), choices={}, widget=forms.CheckboxSelectMultiple, required=False, )  # noqa
    # funds_filter = forms.MultipleChoiceField(label=_("Fonds"), choices={}, widget=forms.CheckboxSelectMultiple, required=False, )  # noqa
    # publication_types_filter = forms.MultipleChoiceField(label=_("Types de publication"), choices={}, widget=forms.CheckboxSelectMultiple, required=False, )  # noqa

    def __init__(self, *args, **kwargs):
        super(SearchForm, self).__init__(*args, **kwargs)

        self.helper = SearchFormHelper()
