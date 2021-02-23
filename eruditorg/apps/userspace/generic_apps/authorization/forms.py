# -*- coding: utf-8 -*-

from django import forms
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.forms import ModelForm
from django.utils.translation import gettext_lazy as _

from core.authorization.models import Authorization


class AuthorizationForm(ModelForm):
    """ This form provides a way to define authorizations associated with a target instance. """

    user = forms.ModelChoiceField(
        label=_("Utilisateur"), queryset=User.objects.none(), empty_label=None
    )

    class Meta:
        model = Authorization
        fields = [
            "user",
        ]

    def __init__(self, *args, **kwargs):
        self.authorization_codename = kwargs.pop("codename")
        self.target_instance = kwargs.pop("target")

        super(AuthorizationForm, self).__init__(*args, **kwargs)

        # Fetches existing authorizations for the considered (target instance, codename)
        authorizations = Authorization.objects.filter(
            content_type=ContentType.objects.get_for_model(self.target_instance),
            object_id=self.target_instance.id,
            authorization_codename=self.authorization_codename,
        )
        authorized_user_ids = list(authorizations.values_list("user_id", flat=True))

        # Update some fields
        self.fields["user"].queryset = self.get_target_instance_members().filter(
            ~Q(id__in=authorized_user_ids)
        )

    def get_target_instance_members(self):
        """Returns the "members" of the instance for which we want to create authorizations.

        The default implementations assumes that there is a "members" M2M on the considered model
        by this can be changed by overridding this method. Note that this method must return a
        QuerySet object.
        """
        return self.target_instance.members.all()

    def save(self, commit=True):
        """
        Create the generic rule from form data
        """
        instance = super(AuthorizationForm, self).save(commit=False)
        instance.authorization_codename = self.authorization_codename
        instance.content_object = self.target_instance

        if commit:
            instance.save()

        return instance
