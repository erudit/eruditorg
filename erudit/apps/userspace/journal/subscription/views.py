# -*- coding: utf-8 -*-

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.views.generic.edit import CreateView
from django.views.generic.edit import DeleteView
from django.views.generic.edit import UpdateView
from django_filters.views import FilterView

from base.viewmixins import MenuItemMixin
from core.subscription.models import IndividualAccountProfile

from ..viewmixins import JournalScopeMixin

from .forms import IndividualAccountFilter
from .forms import IndividualAccountForm
from .forms import IndividualAccountResetPwdForm
from .viewmixins import OrganizationCheckMixin


class IndividualAccountList(JournalScopeMixin, MenuItemMixin, OrganizationCheckMixin, FilterView):
    filterset_class = IndividualAccountFilter
    menu_journal = 'subscription'
    paginate_by = 10
    template_name = 'userspace/journal/subscription/individualaccount_filter.html'


class IndividualAccountCreate(JournalScopeMixin, MenuItemMixin, OrganizationCheckMixin, CreateView):
    menu_journal = 'subscription'
    model = IndividualAccountProfile
    form_class = IndividualAccountForm

    template_name = 'userspace/journal/subscription/individualaccount_create.html'
    title = _("Créer un compte")

    def get_success_url(self):
        return reverse('userspace:journal:subscription:account_list',
                       args=(self.current_journal.pk, ))

    def get_form_kwargs(self):
        kwargs = super(IndividualAccountCreate, self).get_form_kwargs()
        kwargs.update({'user': self.request.user})
        return kwargs


class IndividualAccountUpdate(JournalScopeMixin, MenuItemMixin, OrganizationCheckMixin, UpdateView):
    menu_journal = 'subscription'
    model = IndividualAccountProfile
    form_class = IndividualAccountForm
    template_name = 'userspace/journal/subscription/individualaccount_update.html'

    def get_form_kwargs(self):
        kwargs = super(IndividualAccountUpdate, self).get_form_kwargs()
        kwargs.update({'user': self.request.user})
        return kwargs

    def get_success_url(self):
        return reverse('userspace:journal:subscription:account_list',
                       args=(self.current_journal.pk, ))


class IndividualAccountDelete(JournalScopeMixin, MenuItemMixin, OrganizationCheckMixin, DeleteView):
    menu_journal = 'subscription'
    model = IndividualAccountProfile
    template_name = 'userspace/journal/subscription/individualaccount_confirm_delete.html'

    def get_success_url(self):
        return reverse('userspace:journal:subscription:account_list',
                       args=(self.current_journal.pk, ))


class IndividualAccountResetPwd(
        JournalScopeMixin, MenuItemMixin, OrganizationCheckMixin, UpdateView):
    menu_journal = 'subscription'
    model = IndividualAccountProfile
    form_class = IndividualAccountResetPwdForm
    template_name = 'userspace/journal/subscription/individualaccount_reset_pwd.html'

    def get_success_url(self):
        return reverse('userspace:journal:subscription:account_list',
                       args=(self.current_journal.pk, ))
