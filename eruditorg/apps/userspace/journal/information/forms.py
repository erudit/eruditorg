# -*- coding: utf-8 -*-

from ckeditor.widgets import CKEditorWidget
from django import forms
from django.forms.models import fields_for_model
from django.utils.translation import gettext as _

from erudit.models import JournalInformation


class JournalInformationForm(forms.ModelForm):
    i18n_field_bases = [
        'about', 'team', 'editorial_policy', 'publishing_ethics', 'instruction_for_authors',
        'subscriptions', 'partners', 'contact',
    ]

    # Fields that aren't translatable. You could be wanting to but them in Meta.fields, but that
    # would likely be a mistake because you'll notice that when you do that, the contents of the
    # i18n fields will be blank.
    non_i18n_field_names = [
        'organisation_name', 'email', 'subscription_email', 'languages',
        'phone', 'facebook_url', 'facebook_enable_feed', 'frequency',
        'twitter_url', 'twitter_enable_feed', 'website_url',
        'peer_review_process'
    ]

    class Meta:
        model = JournalInformation
        fields = []

    def __init__(self, *args, **kwargs):
        self.language_code = kwargs.pop('language_code')
        super().__init__(*args, **kwargs)

        # Fetches proper labels for for translatable fields: this is necessary
        # in order to remove language indications from labels (eg. "Team [en]")
        i18n_fields_label = {
            self.get_i18n_field_name(fname): self._meta.model._meta.get_field(fname).verbose_name
            for fname in self.i18n_field_bases}

        # All translatable fields are TextField and will use CKEditor
        i18n_field_widgets = {fname: CKEditorWidget() for fname in self.i18n_field_names}

        # Inserts the translatable fields into the form fields.
        self.fields.update(
            fields_for_model(
                self.Meta.model,
                fields=self.i18n_field_names,
                labels=i18n_fields_label,
                widgets=i18n_field_widgets,
                help_texts=self.i18n_field_help_texts,
            )
        )

        self.fields.update(
            fields_for_model(
                self.Meta.model,
                fields=self.non_i18n_field_names,
            )
        )

    @property
    def i18n_field_names(self):
        return [self.get_i18n_field_name(fname) for fname in self.i18n_field_bases]

    @property
    def i18n_field_help_texts(self):
        return {
            self.get_i18n_field_name('about'): _("<p>Décrivez :</p><ul><li>les objectifs, \
            <li>les champs d’étude</li> <li>et l’historique de votre revue.</li></ul>"),
            self.get_i18n_field_name('team'): _("<p>Présentez :</p><ul><li>le comité éditorial,</li>\
            <li>le conseil d’administration,</li><li>le comité scientifique \
            international (incluant l’affiliation institutionnelle de chacun \
            de ses membres).</li></ul>"),
            self.get_i18n_field_name('editorial_policy'): _("<p>Présentez :</p><ul><li>la \
            politique éditoriale,</li><li>le processus de révision par les pairs</li> \
            <li>et la politique de droits d’auteur, incluant votre licence de \
            diffusion.</li></ul>"),
            self.get_i18n_field_name('publishing_ethics'): _("<p>Décrivez :</p><ul><li>la \
            politique anti-plagiat,</li><li>ou tout autre élément se rapportant aux règles \
            d’éthique.</li></ul>"),
            self.get_i18n_field_name('instruction_for_authors'): _("<p>Décrivez :</p><ul><li>le \
            contrat auteur-revue (s’il y a lieu)</li><li>et les instructions aux auteurs pour la \
            soumission d’articles à la revue.</li></ul>"),
            self.get_i18n_field_name('subscriptions'): _("<p>Décrivez les \
            modalités d’abonnements numérique et papier de votre revue, et présentez les \
            coordonnées des personnes-ressources.</p>"),
            self.get_i18n_field_name('partners'): _("<p>Présentez les partenaires \
            de votre revue (Organismes subventionnaires, départements ou \
            associations) qui soutiennent votre revue.</p><p>Vous pouvez insérer le \
            logo de ces partenaires et/ou un lien vers leur site.</p>"),
        }

    def get_i18n_field_name(self, fname):
        return fname + '_' + self.language_code

    def get_textbox_fields(self):
        return [f for f in self if f.name[:-3] in self.i18n_field_bases]

    def save(self, commit=True):
        obj = super().save(commit)
        # Our dynamically-generated fields aren't automatically saved. Save them.
        for fname in self.i18n_field_names + self.non_i18n_field_names:
            setattr(obj, fname, self.cleaned_data[fname])

        if commit:
            obj.save()
        return obj
