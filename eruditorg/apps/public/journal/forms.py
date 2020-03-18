from django import forms
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify
from erudit.models import Journal, JournalType, Collection, Discipline


class JournalListFilterForm(forms.Form):
    open_access = forms.BooleanField(label=_('Libre accès'), required=False)
    is_new = forms.BooleanField(label=_('Nouveautés'), required=False)
    types = forms.MultipleChoiceField(
        label=_('Par type'), required=False,
        help_text=_(
            "Les revues savantes publient des articles scientifiques révisés par les pairs ; "
            "les revues culturelles présentent des articles dans les domaines artistique, "
            "littéraire et socioculturel."
        )
    )
    collections = forms.MultipleChoiceField(
        label=_('Par fonds'), required=False,
        help_text=_(
            "Les revues diffusées sur Érudit sont consultables directement sur la plateforme ; les "
            "revues des collections Persée et NRC Research Press redirigent vers la plateforme du "
            "partenaire."
        )
    )
    disciplines = forms.MultipleChoiceField(
        label=_('Par discipline'), required=False,
        help_text=_(
            "Cliquez sur la boîte suivante afin de voir la liste complète des disciplines OU "
            "recherchez en saisissant le terme."
        )
    )

    def clean_collections(self):
        data = self.cleaned_data['collections']
        if not data:
            main_collections_codes = [
                c.code for c in Collection.objects.filter(is_main_collection=True)
            ]
            self['collections'].value = main_collections_codes
            return main_collections_codes
        return data

    def __init__(self, *args, **kwargs):
        super(JournalListFilterForm, self).__init__(*args, **kwargs)

        journal_types = JournalType.objects.order_by('name')
        self.fields['types'].choices = [(t.code, t.name) for t in journal_types]

        journals = Journal.objects.select_related('collection').all()
        journal_collections = sorted(
            {j.collection for j in journals},
            key=lambda c: slugify(c.name))
        self.fields['collections'].choices = [(c.code, c.name) for c in journal_collections]

        journal_disciplines = Discipline.objects.order_by('name')
        self.fields['disciplines'].choices = [(d.code, d.name) for d in journal_disciplines]
