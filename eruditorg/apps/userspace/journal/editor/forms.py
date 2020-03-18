# -*- coding: utf-8 -*-

from django import forms
from django.conf import settings
from django.utils.translation import gettext as _
from resumable_uploads.forms import PlUploadFormField
from resumable_uploads.models import ResumableFile

from core.editor.models import IssueSubmission


class ContactModelChoiceField(forms.ModelChoiceField):

    def label_from_instance(self, obj):
        return "{fullname}".format(
            fullname=obj.get_full_name() or obj.username
        )


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

        field_classes = {
            'contact': ContactModelChoiceField,
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
        path=settings.UPLOAD_ROOT,
        label=_("Fichier"),
        options={
            'max_file_size': '3000mb',
            'multi_selection': False,
            'auto_upload': True,
        },
    )
    file_comment = forms.CharField(
        label=_('Commentaires sur le fichier'),
        required=False,
        widget=forms.Textarea,
    )

    def __init__(self, *args, **kwargs):
        super(IssueSubmissionUploadForm, self).__init__(*args, **kwargs)

        # Update some fields
        initial_files = self.instance.last_files_version.submissions.all() \
            .values_list('id', flat=True)
        self.fields['submissions'].initial = ','.join(map(str, initial_files))

    def save(self, commit=True):
        submissions = self.cleaned_data.pop('submissions', '')
        instance = super(IssueSubmissionUploadForm, self).save(commit)
        # Automatically submit the submission when a new upload is saved.
        instance.submit()
        instance.save()

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

            # Saves the comment associated with the submission
            status_track = instance.last_status_track
            status_track.comment = self.cleaned_data.get('file_comment')
            status_track.save()

        return instance


class IssueSubmissionTransitionCommentForm(forms.Form):
    comment = forms.CharField(
        label=_('Commentaires'),
        required=False, widget=forms.Textarea)
