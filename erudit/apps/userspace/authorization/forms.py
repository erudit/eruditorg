import itertools

from django import forms
from django.forms import ModelForm
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType

from core.authorization.models import Authorization
from erudit.models import Journal


class AuthorizationForm(ModelForm):
    """
    This form provides a way to define authorizations based on user journal membership
    (logged user), to filter available journals and users.
    journals are filtred from journal membership
    users are filtered with all users from same journals membership
    """

    journal = forms.ModelChoiceField(label=_("Revue"),
                                     queryset=Journal.objects.none(),
                                     empty_label=None)
    user = forms.ModelChoiceField(label=_("User"),
                                  queryset=User.objects.none(),
                                  empty_label=None)

    class Meta:
        model = Authorization
        fields = ['journal', 'user', 'authorization_codename', ]

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(AuthorizationForm, self).__init__(*args, **kwargs)
        journals_with_manage_permissions = user.journals.all()
        self.fields['journal'].queryset = journals_with_manage_permissions
        us = [j.members.all() for j in journals_with_manage_permissions]
        chain = itertools.chain(*us)
        users = [u.id for u in list(chain)]
        self.fields['user'].queryset = User.objects.filter(id__in=users)

    def clean(self):
        """
        check data integrity for the couple user / journal.
        (Ideally, the field user should be filtered based on journal selection.)
        """
        cleaned_data = super(AuthorizationForm, self).clean()
        self.user = cleaned_data.get("user")
        self.journal = cleaned_data.get("journal")

        if not bool(self.journal.members.filter(id=self.user.id).count()):
            journals = ", ".join([str(j) for j in self.user.journals.all()])
            raise forms.ValidationError("{} {}".format(
                _("Cet utilisateur n'est pas un membre de cette revue.\
                   Ses revues sont :"),
                journals))

    def save(self, *args, **kw):
        """
        Create the generic rule from form data
        """
        instance = super(AuthorizationForm, self).save(commit=False)
        ct = ContentType.objects.get(app_label="erudit", model="journal")
        instance.content_type = ct
        instance.object_id = self.journal.id
        instance.save()
        return instance
