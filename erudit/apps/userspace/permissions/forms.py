import itertools

from django import forms
from django.forms import ModelForm
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType

from rules.permissions import permissions

from core.permissions.models import Rule
from erudit.models import Journal


class RuleForm(ModelForm):
    """
    This form provides a way to define rules based on user journal membership
    (logged user), to filter available journals, users and permisions.
    journals are filtred from journal membership
    users are filtered with all users from same journals membership
    permissions are filtred from a special class method
    """
    permission_filters = (
        'userspace.manage_permissions',
        'editor.manage_issuesubmission',
        'subscription.manage_account',
        'editor.review_issuesubmission',
    )

    journal = forms.ModelChoiceField(label=_("Revue"),
                                     queryset=Journal.objects.none(),
                                     empty_label=None)
    user = forms.ModelChoiceField(label=_("User"),
                                  queryset=User.objects.none(),
                                  empty_label=None)
    permission = forms.ChoiceField(label=_("Permission"))

    class Meta:
        model = Rule
        fields = ['journal', 'user', 'permission', ]

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(RuleForm, self).__init__(*args, **kwargs)
        journals_with_manage_permissions = user.journals.all()
        self.fields['journal'].queryset = journals_with_manage_permissions
        us = [j.members.all() for j in journals_with_manage_permissions]
        chain = itertools.chain(*us)
        users = [u.id for u in list(chain)]
        self.fields['user'].queryset = User.objects.filter(id__in=users)
        declared_rules = [(perm, _(perm)) for perm in permissions.keys()
                          if perm in self.get_permission_filters()]
        self.fields['permission'].choices = declared_rules

    def get_permission_filters(self):
        """
        Function used to filter permissions available in the ChoiceField.
        """
        return self.permission_filters

    def clean(self):
        """
        check data integrity for the couple user / journal.
        (Ideally, the field user should be filtered based on journal selection.)
        """
        cleaned_data = super(RuleForm, self).clean()
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
        instance = super(RuleForm, self).save(commit=False)
        ct = ContentType.objects.get(app_label="erudit", model="journal")
        instance.content_type = ct
        instance.object_id = self.journal.id
        instance.save()
        return instance
