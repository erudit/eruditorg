from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django_filters.views import FilterView

from core.subscription.models import IndividualAccountProfile

from .viewmixins import (IndividualAccountBreadcrumbsMixin,
                         OrganizationCheckMixin)
from .forms import (IndividualAccountFilter, IndividualAccountForm,
                    IndividualAccountResetPwdForm)


class IndividualAccountList(IndividualAccountBreadcrumbsMixin,
                            OrganizationCheckMixin, FilterView):
    filterset_class = IndividualAccountFilter
    paginate_by = 10
    template_name = 'userspace/subscription/individualaccount_filter.html'


class IndividualAccountCreate(IndividualAccountBreadcrumbsMixin,
                              OrganizationCheckMixin, CreateView):
    model = IndividualAccountProfile
    form_class = IndividualAccountForm

    template_name = 'userspace/subscription/individualaccount_create.html'
    title = _("Créer un compte")

    def get_success_url(self):
        return reverse('userspace:subscription:account_list')

    def get_form_kwargs(self):
        kwargs = super(IndividualAccountCreate, self).get_form_kwargs()
        kwargs.update({'user': self.request.user})
        return kwargs


class IndividualAccountUpdate(IndividualAccountBreadcrumbsMixin,
                              OrganizationCheckMixin, UpdateView):
    model = IndividualAccountProfile
    template_name = 'userspace/subscription/individualaccount_update.html'
    form_class = IndividualAccountForm

    def get_form_kwargs(self):
        kwargs = super(IndividualAccountUpdate, self).get_form_kwargs()
        kwargs.update({'user': self.request.user})
        return kwargs

    def get_title(self):
        return _("Modifier un compte")

    def get_success_url(self):
        return reverse('userspace:subscription:account_list')


class IndividualAccountDelete(IndividualAccountBreadcrumbsMixin,
                              OrganizationCheckMixin, DeleteView):
    model = IndividualAccountProfile
    template_name = 'userspace/subscription/individualaccount_confirm_delete.html'

    def get_title(self):
        return _("Supprimer un compte")

    def get_success_url(self):
        return reverse('userspace:subscription:account_list')


class IndividualAccountResetPwd(IndividualAccountBreadcrumbsMixin,
                                OrganizationCheckMixin, UpdateView):
    model = IndividualAccountProfile
    form_class = IndividualAccountResetPwdForm
    template_name = 'userspace/subscription/individualaccount_reset_pwd.html'

    def get_title(self):
        return _("Réinitialiser le mot de passe d'un compte")

    def get_success_url(self):
        return reverse('userspace:subscription:account_list')
