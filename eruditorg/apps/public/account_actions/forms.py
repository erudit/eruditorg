# -* - coding: utf-8 -*-

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.forms import EmailField
from django.utils.translation import gettext_lazy as _


class AccountActionRegisterForm(UserCreationForm):
    email = EmailField(label=_('Adresse courriel'), required=True)

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'password1', 'password2', )

    def __init__(self, *args, **kwargs):
        self.token = kwargs.pop('token')
        super(AccountActionRegisterForm, self).__init__(*args, **kwargs)

        # Initializes some fields using the token values
        self.fields['email'].initial = self.token.email
        if self.token.first_name:
            self.fields['first_name'].initial = self.token.first_name
        if self.token.last_name:
            self.fields['last_name'].initial = self.token.last_name

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            self.add_error('email', _('Cette adresse courriel est déjà utilisée'))
        return email

    def save(self, commit=True):
        user = super(AccountActionRegisterForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        user.username = self.cleaned_data['email']

        if commit:
            user.save()
            # Consumes the token
            self.token.consume(user)

        return user
