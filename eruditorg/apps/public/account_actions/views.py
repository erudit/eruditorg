# -*- coding: utf-8 -*-

from account_actions.views.generic import AccountActionLandingView as BaseAccountActionLandingView
from account_actions.views.generic import AccountActionConsumeView  # noqa
from account_actions.views.generic import AccountActionTokenMixin
from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth import login
from django.views.generic import CreateView
from rules.contrib.views import PermissionRequiredMixin

from .forms import AccountActionRegisterForm


class AccountActionLandingView(BaseAccountActionLandingView):
    # We assume that the 'landing_page_template_name' attribute is defined on all the actions.
    template_name = None


class AccountActionRegisterView(PermissionRequiredMixin, AccountActionTokenMixin, CreateView):
    """
    Allows to create a User account using an account action token. The considered can only create
    an account if the token can be consumed.
    """
    form_class = AccountActionRegisterForm
    raise_exception = True
    template_name = 'public/account_actions/register.html'

    def form_valid(self, form):
        response = super(AccountActionRegisterView, self).form_valid(form)

        # We log the user in
        new_authenticated_user = authenticate(
            username=form.cleaned_data['username'],
            password=form.cleaned_data['password1'])
        login(self.request, new_authenticated_user)

        return response

    def get_form_kwargs(self):
        kwargs = super(AccountActionRegisterView, self).get_form_kwargs()
        kwargs.update({'token': self.token})
        return kwargs

    def get_success_url(self):
        messages.success(
            self.request, self.action.get_consumption_success_message(self.token))
        return self.action.get_consumption_redirect_url(self.token)

    def has_permission(self):
        return not self.request.user.is_authenticated and self.token.can_be_consumed
