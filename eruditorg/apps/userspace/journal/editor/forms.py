# -*- coding: utf-8 -*-

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms
from django.utils.translation import gettext as _
from django_select2.forms import Select2Widget
from plupload.forms import PlUploadFormField
from plupload.models import ResumableFile

from core.editor.models import IssueSubmission


class IssueSubmissionForm(forms.ModelForm):

    required_css_class = 'required'

    class Meta:
        model = IssueSubmission

        fields = [
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
            'year', 'contact', 'number',
            'volume', 'comment',
            'submissions',
        )

        for field in fields:
            self.fields[field].widget.attrs['disabled'] = True

    def __init__(self, *args, **kwargs):
        self.journal = kwargs.pop('journal')
        self.user = kwargs.pop('user')
        kwargs.setdefault('label_suffix', '')
        super(IssueSubmissionForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_class = 'form-vertical'
        self.helper.form_method = 'post'

        self.helper.add_input(
            Submit('submit', _("Envoyer le fichier"))
        )
        self.populate_select(self.user)

        self.instance.journal = self.journal

    def populate_select(self, user):
        journals_members = self.journal.members.all()
        member_first = journals_members.first()
        self.fields['contact'].queryset = journals_members
        if member_first:
            self.fields['contact'].initial = member_first.id


class IssueSubmissionUploadForm(IssueSubmissionForm):

    class Meta(IssueSubmissionForm.Meta):

        fields = (
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
        },
    )

    def __init__(self, *args, **kwargs):
        super(IssueSubmissionUploadForm, self).__init__(*args, **kwargs)

        # Update some fields
        initial_files = self.instance.last_files_version.submissions.all() \
            .values_list('id', flat=True)
        self.fields['submissions'].initial = ','.join(map(str, initial_files))
        self.fields['submissions'].widget.template_name = \
            'userspace/journal/editor/plupload_widget.html'

    def save(self, commit=True):
        submissions = self.cleaned_data.pop('submissions', '')
        instance = super(IssueSubmissionUploadForm, self).save(commit)

        # Saves the resumable files associated to the submission
        if commit:
            fversion = instance.last_files_version
            fversion.submissions.clear()
            if submissions:
                file_ids = submissions.split(',')
                for fid in file_ids:
                    try:
                        rfile = ResumableFile.objects.get(id=fid)
                    except ResumableFile.DoesNotExist:
                        pass
                    else:
                        fversion.submissions.add(rfile)

        return instance


class IssueSubmissionTransitionCommentForm(forms.Form):
    comment = forms.CharField(
        label=_('Vous pouvez ajouter un commentaire afin d\'expliquer vos raisons'),
        required=False, widget=forms.Textarea)
