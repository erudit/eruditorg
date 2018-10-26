# -*- coding: utf-8 -*-

from ckeditor.widgets import CKEditorWidget
from django import forms
from django.forms.models import fields_for_model
from django.utils.translation import gettext as _

from erudit.models import JournalInformation


class JournalInformationForm(forms.ModelForm):
    i18n_field_bases = [
        'about', 'editorial_policy', 'subscriptions',
        'team', 'contact', 'partners', 'publishing_ethics', 'instruction_for_authors'
    ]

    # Fields that aren't translatable. You could be wanting to but them in Meta.fields, but that
    # would likely be a mistake because you'll notice that when you do that, the contents of the
    # i18n fields will be blank.
    non_i18n_field_names = [
        'organisation_name', 'email', 'subscription_email', 'languages',
        'phone', 'facebook_url', 'facebook_enable_feed',
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
            self.get_i18n_field_name('about'): _("Décrivez les objectifs, \
            les champs d'étude et l’historique de votre revue. Vous pouvez \
            également y présenter l’éditeur (société savante, département, \
            groupe de recherche) et votre calendrier de publication. "),
            self.get_i18n_field_name('editorial_policy'): _("Présentez la \
            politique éditoriale, le processus de révision par les pairs, \
            la politique de droits d’auteur, incluant votre licence de \
            diffusion; dans le cas d’une revue en libre accès diffusée sous \
            une licence Creative Commons, vous pouvez insérer un lien vers le \
            site de la licence. Vous pouvez également y présenter le contrat \
            auteur-revue s’il y a lieu, la politique anti-plagiat, ainsi que \
            les instructions aux auteurs pour la soumission d’articles à la \
            revue."),
            self.get_i18n_field_name('team'): _("Décrivez le comité éditorial, \
            le conseil d’administration, le comité scientifique \
            international (incluant l’affiliation institutionnelle de chacun \
            de ses membres)."),
            self.get_i18n_field_name('subscriptions'): _("Décrivez les \
            modalités d’abonnements numérique et papier de votre revue \
            (coordonnées de la personne-ressource). "),
            self.get_i18n_field_name('partners'): _("Présentez les partenaires \
            de votre revue (Organismes subventionnaires, départements ou \
            associations) qui soutiennent votre revue. Vous pouvez insérer le \
            logo de ces partenaires et/ou un lien vers leur site."),
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
