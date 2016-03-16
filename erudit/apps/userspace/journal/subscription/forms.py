from django import forms
from django.forms import ModelForm
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User

import django_filters

from core.subscription.models import IndividualAccountProfile, Policy


class IndividualAccountFilter(django_filters.FilterSet):
    class Meta:
        model = IndividualAccountProfile
        fields = {
            'user__first_name': ['icontains', ],
            'user__last_name': ['icontains', ],
            'policy': ['exact', ]
        }


class IndividualAccountForm(forms.Form):
    first_name = forms.CharField(
        label=_('Prénom'),
        )
    last_name = forms.CharField(
        label=_('Nom'),
        )
    email = forms.EmailField(
        label=_('Courriel'),
        )
    policy = forms.ModelChoiceField(queryset=Policy.objects.all())

    def __init__(self, user, instance=None, *args, **kwargs):
        super(IndividualAccountForm, self).__init__(*args, **kwargs)
        org_ids = [o.id for o in user.organizations_managed.all()]
        if not (user.is_staff or user.is_superuser):
            self.fields['policy'] = forms.ModelChoiceField(
                queryset=Policy.objects.filter(id__in=org_ids),
                label=Policy._meta.verbose_name)
        if instance:
            self.instance = instance
            self.fields['first_name'].initial = instance.user.first_name
            self.fields['last_name'].initial = instance.user.last_name
            self.fields['email'].initial = instance.user.email
            self.fields['policy'].initial = instance.policy

    def save(self):
        email = self.cleaned_data['email'].lower()
        first_name = self.cleaned_data['first_name'].lower()
        last_name = self.cleaned_data['last_name'].lower()
        email = self.cleaned_data['email'].lower()
        policy = self.cleaned_data['policy']

        if hasattr(self, 'instance'):
            user = self.instance.user
            profile = self.instance
        else:
            user, created = User.objects.get_or_create(email__iexact=email)
            profile = IndividualAccountProfile()

        if not user.username or user.username == user.email:
            user.username = email
        user.email = email
        user.first_name = first_name
        user.last_name = last_name
        user.save()
        profile.user = user
        profile.policy = policy
        profile.save()


class IndividualAccountResetPwdForm(ModelForm):
    password = forms.CharField(
        initial='',
        widget=forms.PasswordInput,
        label=_('Mot de passe'),
        required=False)

    class Meta:
        model = IndividualAccountProfile
        fields = ['password', ]

    def save(self, **kwargs):
        # password should not be specify here, but empty value are not set
        # to the instance property
        self.instance.password = self.cleaned_data['password']
        return super().save(**kwargs)
