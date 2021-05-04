import reversion

from ckeditor.widgets import CKEditorWidget
from diff_match_patch import diff_match_patch
from django import forms
from django.conf import settings
from django.db.models import ManyToManyField
from django.forms.models import fields_for_model
from django.utils.translation import gettext as _
from django.forms import inlineformset_factory

from core.email import Email
from erudit.models import JournalInformation, Contributor
from erudit.admin.journal import JOURNAL_INFORMATION_COMPARE_EXCLUDE


class JournalInformationForm(forms.ModelForm):
    i18n_field_bases = [
        "about",
        "team",
        "editorial_policy",
        "publishing_ethics",
        "instruction_for_authors",
        "subscriptions",
        "partners",
        "contact",
    ]

    # Fields that aren't translatable. You could be wanting to but them in Meta.fields, but that
    # would likely be a mistake because you'll notice that when you do that, the contents of the
    # i18n fields will be blank.
    non_i18n_field_names = [
        "email",
        "subscription_email",
        "phone",
        "facebook_url",
        "facebook_enable_feed",
        "frequency",
        "twitter_url",
        "twitter_enable_feed",
        "website_url",
        "peer_review_process",
    ]

    class Meta:
        model = JournalInformation
        fields = [
            "email",
            "subscription_email",
            "phone",
            "facebook_url",
            "facebook_enable_feed",
            "frequency",
            "twitter_url",
            "twitter_enable_feed",
            "website_url",
            "peer_review_process",
            "about_fr",
            "team_fr",
            "editorial_policy_fr",
            "publishing_ethics_fr",
            "instruction_for_authors_fr",
            "subscriptions_fr",
            "partners_fr",
            "contact_fr",
            "about_en",
            "team_en",
            "editorial_policy_en",
            "publishing_ethics_en",
            "instruction_for_authors_en",
            "subscriptions_en",
            "partners_en",
            "contact_en",
        ]

    def __init__(self, *args, **kwargs):
        self.language_code = kwargs.pop("language_code")
        self.request = kwargs.pop("request")
        super().__init__(*args, **kwargs)

        # Fetches proper labels for for translatable fields: this is necessary
        # in order to remove language indications from labels (eg. "Team [en]")
        i18n_fields_label = {
            self.get_i18n_field_name(fname): self._meta.model._meta.get_field(fname).verbose_name
            for fname in self.i18n_field_bases
        }

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

        # Remove translatable fields not in the selected language.
        langcode = "en" if self.language_code == "fr" else "fr"
        [self.fields.pop(f"{field_name}_{langcode}") for field_name in self.i18n_field_bases]

    @property
    def i18n_field_names(self):
        return [self.get_i18n_field_name(fname) for fname in self.i18n_field_bases]

    @property
    def i18n_field_help_texts(self):
        return {
            self.get_i18n_field_name("about"): _(
                "<p>Décrivez :</p><ul><li>les objectifs, \
            <li>les champs d’étude</li> <li>et l’historique de votre revue.</li></ul>"
            ),
            self.get_i18n_field_name("team"): _(
                "<p>Présentez :</p><ul><li>le comité éditorial,</li>\
            <li>le conseil d’administration,</li><li>le comité scientifique \
            international (incluant l’affiliation institutionnelle de chacun \
            de ses membres).</li></ul>"
            ),
            self.get_i18n_field_name("editorial_policy"): _(
                "<p>Présentez :</p><ul><li>la \
            politique éditoriale,</li><li>le processus de révision par les pairs</li> \
            <li>et la politique de droits d’auteur, incluant votre licence de \
            diffusion.</li></ul>"
            ),
            self.get_i18n_field_name("publishing_ethics"): _(
                "<p>Décrivez :</p><ul><li>la \
            politique anti-plagiat,</li><li>ou tout autre élément se rapportant aux règles \
            d’éthique.</li></ul>"
            ),
            self.get_i18n_field_name("instruction_for_authors"): _(
                "<p>Décrivez :</p><ul><li>le \
            contrat auteur-revue (s’il y a lieu)</li><li>et les instructions aux auteurs pour la \
            soumission d’articles à la revue.</li></ul>"
            ),
            self.get_i18n_field_name("subscriptions"): _(
                "<p>Décrivez les \
            modalités d’abonnements numérique et papier de votre revue, et présentez les \
            coordonnées des personnes-ressources.</p>"
            ),
            self.get_i18n_field_name("partners"): _(
                "<p>Présentez les partenaires \
            de votre revue (Organismes subventionnaires, départements ou \
            associations) qui soutiennent votre revue.</p><p>Vous pouvez insérer le \
            logo de ces partenaires et/ou un lien vers leur site.</p>"
            ),
        }

    def get_i18n_field_name(self, fname):
        return fname + "_" + self.language_code

    def get_textbox_fields(self):
        return [f for f in self if f.name[:-3] in self.i18n_field_bases]

    def save(self, commit=True):
        obj = super().save(commit)
        # Our dynamically-generated fields aren't automatically saved. Save them.
        for fname in self.i18n_field_names + self.non_i18n_field_names:
            if isinstance(obj._meta.get_field(fname), ManyToManyField):
                attr = getattr(obj, fname)
                attr.set(self.cleaned_data[fname])
            else:
                setattr(obj, fname, self.cleaned_data[fname])

        if commit and self.changed_data:
            with reversion.create_revision():
                obj.save()
                changed_field_labels = [
                    str(self.fields[field_name].label) for field_name in self.changed_data
                ]
                reversion.set_user(self.request.user)
                reversion.set_comment(
                    "Champ(s) modifié(s) : {}".format(
                        ", ".join(changed_field_labels),
                    )
                )
            self.send_revision_email(obj)
        return obj

    def send_revision_email(self, obj):
        queryset = reversion.models.Version.objects.get_for_object(obj)
        if queryset.count() > 1:
            dmp = diff_match_patch()
            current_version = queryset[0]
            previous_version = queryset[1]
            compare_data = []
            for field_name in current_version.field_dict.keys():
                if field_name in JOURNAL_INFORMATION_COMPARE_EXCLUDE:
                    continue
                # Generate diffs between current and previous versions.
                diffs = dmp.diff_main(
                    str(previous_version.field_dict.get(field_name)),
                    str(current_version.field_dict.get(field_name)),
                )
                # diff_main() returns a list of tuples of differences. The first element of the
                # tuples is either 1 (insertion), -1 (deletion) or 0 (equality), and the second
                # element is the affected text.
                # If there is no differences in a field, diff_main() will return a list with only
                # one tuple with 0 (equality) as the first element and the unchanged field value as
                # the second element.
                # So, if there's only one element in the diffs, there is no differences and we
                # should skip that field.
                if len(diffs) <= 1:
                    continue
                # Make the diffs more human readable.
                dmp.diff_cleanupSemantic(diffs)
                compare_data.append(
                    {
                        "field": self._meta.model._meta.get_field(field_name),
                        "diff": dmp.diff_prettyHtml(diffs),
                    }
                )
            email = Email(
                recipient=settings.ACCOUNT_EMAIL,
                html_template="emails/information/journal_information_new_revision_content.html",
                subject_template="emails/information/journal_information_new_revision_subject.html",
                extra_context={
                    "journal": obj.journal,
                    "compare_data": compare_data,
                    "current_revision": current_version.revision,
                    "request": self.request,
                },
                tag="www-journal-information-new-revision",
            )
            email.send()


ContributorInlineFormset = inlineformset_factory(
    JournalInformation,
    Contributor,
    fields=("type", "name", "role"),
    can_delete=True,
    extra=1,
)
