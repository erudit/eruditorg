from django import forms
from django.utils.translation import ugettext_lazy as _

from rules.permissions import permissions

from .models import Rule


class RuleForm(forms.ModelForm):

    permission = forms.ChoiceField()

    class Meta:
        model = Rule
        fields = ('user', 'group', 'permission', )

    def __init__(self, *args, **kwargs):
        super(RuleForm, self).__init__(*args, **kwargs)
        permission_rules = [(perm, _(perm)) for perm in permissions.keys()]
        self.fields['permission'].choices = permission_rules
