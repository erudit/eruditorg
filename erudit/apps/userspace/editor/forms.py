from django import forms
from django.utils.translation import gettext as _
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

from django_select2.forms import Select2Widget

from plupload.forms import PlUploadFormField

from core.editor.models import IssueSubmission


class IssueSubmissionForm(forms.ModelForm):

    required_css_class = 'required'

    class Meta:
        model = IssueSubmission

        fields = [
            'journal',
            'year',
            'volume',
            'number',
            'contact',
            'comment',
        ]

        widgets = {
            'journal': Select2Widget,
            'contact': Select2Widget,
        }

    def disable_form(self):
        """ Disable all the fields of this form """
        fields = (
            'year', 'journal', 'contact', 'number',
            'volume', 'comment',
            'submissions',
        )

        for field in fields:
            self.fields[field].widget.attrs['readonly'] = True

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        kwargs.setdefault('label_suffix', '')
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_class = 'form-vertical'
        self.helper.form_method = 'post'

        self.helper.add_input(
            Submit('submit', _("Envoyer le fichier"))
        )
        self.populate_select(user)

    def populate_select(self, user):
        qs = user.journals.all()
        ids = [j.id for j in qs if user.has_perm(
               'editor.manage_issuesubmission', j)]
        qs.filter(id__in=ids)
        self.fields['journal'].queryset = qs.filter(id__in=ids)

        self.fields['journal'].initial = self.fields['journal'].queryset.first()

        journals_members = User.objects.filter(
            journals=user.journals.all()
        ).distinct()

        self.fields['contact'].queryset = journals_members
        self.fields['contact'].initial = self.fields['contact'].queryset.first()

    def clean(self):
        cleaned_data = super().clean()
        journal = cleaned_data.get("journal")
        contact = cleaned_data.get("contact")
        if not journal.members.filter(id=contact.id).count():
            raise ValidationError(
                _("Ce contact n'est pas membre de cette revue."))


class IssueSubmissionUploadForm(IssueSubmissionForm):

    class Meta(IssueSubmissionForm.Meta):

        fields = (
            'journal',
            'year',
            'volume',
            'number',
            'contact',
            'comment',
            'submissions',
        )

    submissions = PlUploadFormField(
        path='uploads',
        label=_("Fichier"),
        options={
            "max_file_size": '15000mb',
            "drop_element": 'drop_element',
            "container": 'drop_element',
            "browse_button": 'pickfiles'
        }
    )
