from django import forms
from django.utils.translation import gettext as _

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

from datetimewidget.widgets import DateWidget
from django_select2.forms import Select2Widget

from plupload.forms import PlUploadFormField

from editor.models import IssueSubmission


class IssueSubmissionForm(forms.ModelForm):
    class Meta:
        model = IssueSubmission

        fields = [
            'journal',
            'volume',
            'date_created',
            'contact',
            'comment',
        ]

        widgets = {
            'date_created': DateWidget(
                attrs={'id': "date_created"},
                usel10n=True,
                bootstrap_version=3,
                options={
                    'todayHighlight': True,
                }
            ),
            'journal': Select2Widget,
            'contact': Select2Widget,
        }

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_class = 'form-vertical'
        # self.helper.label_class = 'col-xs-12'
        # self.helper.field_class = 'col-xs-12'
        self.helper.form_method = 'post'

        self.helper.add_input(
            Submit('submit', _("Envoyer le fichier"))
        )


class IssueSubmissionUploadForm(IssueSubmissionForm):

    class Meta(IssueSubmissionForm.Meta):

        fields = (
            'journal',
            'volume',
            'date_created',
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
