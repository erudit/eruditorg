import datetime as dt
from django import forms
from django.utils.translation import gettext as _

current_year = dt.datetime.now().year

COLLECTION_CHOICES = (
    ('all', _('Tout')),
    ('erudit', 'Érudit'),
    ('unb', 'UNB'),
)

TYPE_CHOICES = (
    ('all', _('Tout')),
    ('academic', _('Savantes')),
    ('cultural', _('Culturelles')),
)

ACCESS_CHOICES = (
    ('all', _('Tout')),
    ('openaccess', _('Libre accès')),
    ('restriction', _('Sous commercialisation')),
    ('endPublication', _('Abandon de publication numérique'))
)


class KBARTForm(forms.Form):

    collection = forms.ChoiceField(
        label=_("Fonds"), widget=forms.Select(), choices=COLLECTION_CHOICES, required=False
    )

    typeRevue = forms.ChoiceField(
        label=_("Type de revues"), widget=forms.Select(), choices=TYPE_CHOICES, required=False
    )

    access = forms.ChoiceField(
        label=_("Mode d’accès"), widget=forms.Select(), choices=ACCESS_CHOICES, required=False
    )
