# -*- coding: utf-8 -*-
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.views.generic import UpdateView
from django.views.generic import FormView
from django.views.generic.base import RedirectView
from django.http.response import HttpResponseForbidden
from django.contrib.auth.mixins import LoginRequiredMixin
from base.viewmixins import MenuItemMixin

from .forms import UserParametersForm
from .forms import UserPersonalDataForm
from .shortcuts import can_modify_account


class CanModifyAccountMixin:

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['can_modify_account'] = can_modify_account(self.request.user)
        return context


class UserPersonalDataUpdateView(
    CanModifyAccountMixin, LoginRequiredMixin, MenuItemMixin, UpdateView
):
    form_class = UserPersonalDataForm
    menu_account = 'personal'
    template_name = 'public/auth/personal_data.html'

    def get_object(self):
        return self.request.user

    def form_valid(self, form):
        messages.success(
            self.request, _('Vos informations personelles ont été mises à jour avec succès.'))
        return super(UserPersonalDataUpdateView, self).form_valid(form)

    def get_success_url(self):
        return reverse('public:auth:personal_data')


class UserParametersUpdateView(
    CanModifyAccountMixin, LoginRequiredMixin, MenuItemMixin, UpdateView
):
    form_class = UserParametersForm
    menu_account = 'parameters'
    template_name = 'public/auth/parameters.html'

    def dispatch(self, request, *args, **kwargs):
        user = self.request.user
        if not can_modify_account(user):
            return HttpResponseForbidden()
        return super().dispatch(request, *args, **kwargs)

    def get_object(self):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, _('Votre compte a été mis à jour avec succès.'))
        return super(UserParametersUpdateView, self).form_valid(form)

    def get_success_url(self):
        return reverse('public:auth:parameters')


class UserLoginLandingRedirectView(LoginRequiredMixin, RedirectView, CanModifyAccountMixin):
    """ Redirects the user on successful login

    Any user that has access to a dashboard will be redirected to his dashboard.
    Users that do not have access to the dashboard will be redirected to the value
    of ``request.META['HTTP_REFERER']``. If ``request.META['HTTP_REFERER']`` is unset,
    user will be redirected to the home page.
    """
    def get_redirect_url(self, *args, **kwargs):
        messages.success(self.request, _('Votre connexion a été effectuée avec succès.'))
        if self.request.user.has_perm('userspace.access'):
            return reverse('userspace:dashboard')

        next = self.request.GET.get('next')
        if next:
            return next
        return reverse('public:home')


class UserPasswordChangeView(CanModifyAccountMixin, LoginRequiredMixin, MenuItemMixin, FormView):
    form_class = PasswordChangeForm
    menu_account = 'password'
    template_name = 'public/auth/password_change.html'

    def get_form_kwargs(self):
        kwargs = super(UserPasswordChangeView, self).get_form_kwargs()
        kwargs.update({'user': self.request.user})
        return kwargs

    def get_success_url(self):
        return reverse('public:auth:password_change')

    def form_valid(self, form):
        form.save()
        messages.success(self.request, _('Votre mot de passe a été mis à jour avec succès'))
        update_session_auth_hash(self.request, form.user)
        return super(UserPasswordChangeView, self).form_valid(form)
