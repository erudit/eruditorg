# -*- coding: utf-8 -*-

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.views.generic.edit import CreateView
from django.views.generic.edit import DeleteView
from django.views.generic.edit import UpdateView
from django_filters.views import FilterView

from core.subscription.models import IndividualAccountProfile

from ..viewmixins import JournalScopeMixin

from .forms import IndividualAccountFilter
from .forms import IndividualAccountForm
from .forms import IndividualAccountResetPwdForm
from .viewmixins import IndividualAccountBreadcrumbsMixin
from .viewmixins import OrganizationCheckMixin


class IndividualAccountList(JournalScopeMixin, IndividualAccountBreadcrumbsMixin,
                            OrganizationCheckMixin, FilterView):
    filterset_class = IndividualAccountFilter
    paginate_by = 10
    template_name = 'userspace/journal/subscription/individualaccount_filter.html'


class IndividualAccountCreate(JournalScopeMixin, IndividualAccountBreadcrumbsMixin,
                              OrganizationCheckMixin, CreateView):
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


class IndividualAccountUpdate(JournalScopeMixin, IndividualAccountBreadcrumbsMixin,
                              OrganizationCheckMixin, UpdateView):
    model = IndividualAccountProfile
    form_class = IndividualAccountForm
    template_name = 'userspace/journal/subscription/individualaccount_update.html'

    def get_title(self):
        return _("Modifier un compte")

    def get_success_url(self):
        return reverse('userspace:journal:subscription:account_list',
                       args=(self.current_journal.pk, ))


class IndividualAccountDelete(JournalScopeMixin, IndividualAccountBreadcrumbsMixin,
                              OrganizationCheckMixin, DeleteView):
    model = IndividualAccountProfile
    template_name = 'userspace/journal/subscription/individualaccount_confirm_delete.html'

    def get_title(self):
        return _("Supprimer un compte")

    def get_success_url(self):
        return reverse('userspace:journal:subscription:account_list',
                       args=(self.current_journal.pk, ))


class IndividualAccountResetPwd(JournalScopeMixin, IndividualAccountBreadcrumbsMixin,
                                OrganizationCheckMixin, UpdateView):
    model = IndividualAccountProfile
    form_class = IndividualAccountResetPwdForm
    template_name = 'userspace/journal/subscription/individualaccount_reset_pwd.html'

    def get_title(self):
        return _("Réinitialiser le mot de passe d'un compte")

    def get_success_url(self):
        return reverse('userspace:journal:subscription:account_list',
                       args=(self.current_journal.pk, ))
