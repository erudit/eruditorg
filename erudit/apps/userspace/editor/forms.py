from django import forms
from django.utils.translation import gettext as _
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

from django_select2.forms import Select2Widget

from plupload.forms import PlUploadFormField
from plupload.models import ResumableFile

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
            'journal': Select2Widget(),
            'contact': Select2Widget(),
        }

    def disable_form(self):
        """ Disable all the fields of this form """
        fields = (
            'year', 'journal', 'contact', 'number',
            'volume', 'comment',
            'submissions',
        )

        for field in fields:
            self.fields[field].widget.attrs['disabled'] = True

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

        journal_qs = qs.filter(id__in=ids)
        journal_first = journal_qs.first()
        self.fields['journal'].queryset = journal_qs
        if journal_first:
            self.fields['journal'].initial = journal_first.id

        journals_members = User.objects.filter(
            journals=user.journals.all()
        ).distinct()

        journals_members
        member_first = journals_members.first()
        self.fields['contact'].queryset = journals_members
        if member_first:
            self.fields['contact'].initial = member_first.id

    def clean(self):
        cleaned_data = super().clean()
        journal = cleaned_data.get("journal")
        contact = cleaned_data.get("contact")
        if contact and not journal.members.filter(id=contact.id).count():
            raise ValidationError(
                _("Ce contact n'est pas membre de cette revue."))
        return cleaned_data


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

    def __init__(self, *args, **kwargs):
        super(IssueSubmissionUploadForm, self).__init__(*args, **kwargs)

        # Update some fields
        initial_files = self.instance.submissions.all() \
            .values_list('id', flat=True)
        self.fields['submissions'].initial = ','.join(map(str, initial_files))

    def save(self, commit=True):
        submissions = self.cleaned_data.pop('submissions', '')
        instance = super(IssueSubmissionUploadForm, self).save(commit)

        # Saves the resumable files associated to the submission
        if commit:
            instance.submissions.clear()
            if submissions:
                file_ids = submissions.split(',')
                for fid in file_ids:
                    try:
                        rfile = ResumableFile.objects.get(id=fid)
                    except ResumableFile.DoesNotExist:
                        pass
                    else:
                        instance.submissions.add(rfile)

        return instance
