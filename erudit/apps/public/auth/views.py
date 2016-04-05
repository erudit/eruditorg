# -*- coding: utf-8 -*-

from django.contrib import messages
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.views.generic import FormView

from base.viewmixins import LoginRequiredMixin

from .forms import PasswordChangeForm


class UserPasswordChangeView(LoginRequiredMixin, FormView):
    form_class = PasswordChangeForm
    template_name = 'public/auth/password_change.html'

    def get_form_kwargs(self):
        kwargs = super(UserPasswordChangeView, self).get_form_kwargs()
        kwargs.update({'user': self.request.user})
        return kwargs

    def get_success_url(self):
        messages.success(self.request, _('Votre mot de passe a été mis à jour avec succès'))
        return reverse('public:auth:password_change')

    def form_valid(self, form):
        form.save()
        return super(UserPasswordChangeView, self).form_valid(form)
