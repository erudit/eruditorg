# -*- coding: utf-8 -*-

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms
from django.contrib.auth.models import User
from django.forms import ModelForm
from django.utils.translation import ugettext_lazy as _

from core.authorization.models import Authorization


class AuthorizationForm(ModelForm):
    """
    This form provides a way to define authorizations based on user journal membership
    (logged user), to filter available journals and users.
    journals are filtred from journal membership
    users are filtered with all users from same journals membership
    """
    user = forms.ModelChoiceField(
        label=_('Utilisateur'), queryset=User.objects.none(), empty_label=None)

    class Meta:
        model = Authorization
        fields = ['user', ]

    def __init__(self, *args, **kwargs):
        self.authorization_codename = kwargs.pop('codename')
        self.journal = kwargs.pop('journal')

        super(AuthorizationForm, self).__init__(*args, **kwargs)

        # Update some fields
        self.fields['user'].queryset = self.journal.members.all()

        # TODO: remove crispy-forms
        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.add_input(Submit('submit', _('Valider')))

    def save(self, commit=True):
        """
        Create the generic rule from form data
        """
        instance = super(AuthorizationForm, self).save(commit=False)
        instance.authorization_codename = self.authorization_codename
        instance.content_object = self.journal

        if commit:
            instance.save()

        return instance
