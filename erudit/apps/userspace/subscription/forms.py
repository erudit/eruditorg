from django import forms
from django.forms import ModelForm
from django.utils.translation import ugettext_lazy as _

import django_filters

from core.subscription.models import IndividualAccount, Policy


class IndividualAccountFilter(django_filters.FilterSet):
    class Meta:
        model = IndividualAccount
        fields = {
            'first_name': ['icontains', ],
            'last_name': ['icontains', ],
            'policy': ['exact', ]
        }


class IndividualAccountForm(ModelForm):
    class Meta:
        model = IndividualAccount
        fields = ['first_name', 'last_name', 'email', 'policy', ]

    def __init__(self, user, *args, **kwargs):
        super(IndividualAccountForm, self).__init__(*args, **kwargs)
        org_ids = [o.id for o in user.organizations_managed.all()]
        if not (user.is_staff or user.is_superuser):
            self.fields['policy'] = forms.ModelChoiceField(
                queryset=Policy.objects.filter(id__in=org_ids),
                label=Policy._meta.verbose_name)


class IndividualAccountResetPwdForm(ModelForm):
    password = forms.CharField(
        initial='',
        widget=forms.PasswordInput,
        label=_('Mot de passe'),
        required=False)

    class Meta:
        model = IndividualAccount
        fields = ['password', ]

    def save(self, **kwargs):
        # password should not be specify here, but empty value are not set
        # to the instance property
        self.instance.password = self.cleaned_data['password']
        return super().save(**kwargs)
