from django import forms
from django.utils.translation import gettext as _

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

from django_select2.forms import Select2Widget

from plupload.forms import PlUploadFormField

from editor.models import IssueSubmission


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

    def __init__(self, *args, **kwargs):

        kwargs.setdefault('label_suffix', '')
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_class = 'form-vertical'
        self.helper.form_method = 'post'

        self.helper.add_input(
            Submit('submit', _("Envoyer le fichier"))
        )


class IssueSubmissionUploadForm(IssueSubmissionForm):

    class Meta(IssueSubmissionForm.Meta):

        fields = (
            'journal',
            'year',
            'volume',
            'number',
            'contact',
            'comment',
            'submission_file',
        )

    submission_file = PlUploadFormField(
        path='uploads',
        label=_("Fichier"),
        options={
            "max_file_size": '5000mb'
        }
    )
