import itertools

from django import forms
from django.forms import ModelForm
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType

from rules.permissions import permissions

from erudit.models import Journal
from permissions.models import Rule


class RuleForm(ModelForm):
    journal = forms.ModelChoiceField(queryset=Journal.objects.none(),
                                     empty_label=None)
    user = forms.ModelChoiceField(queryset=User.objects.none(), empty_label=None)
    permission = forms.ChoiceField()

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
        declared_rules = [(perm, _(perm)) for perm in permissions.keys()]
        self.fields['permission'].choices = declared_rules

    def clean(self):
        cleaned_data = super(RuleForm, self).clean()
        self.user = cleaned_data.get("user")
        self.journal = cleaned_data.get("journal")

        if not bool(self.journal.members.filter(id=self.user.id).count()):
            raise forms.ValidationError(
                _("This user is not a member of that journal"))

    def save(self, *args, **kw):
        instance = super(RuleForm, self).save(commit=False)
        ct = ContentType.objects.get(app_label="erudit", model="journal")
        instance.content_type = ct
        instance.object_id = self.journal.id
        instance.save()
        return instance
