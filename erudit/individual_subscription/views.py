from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.core.urlresolvers import reverse

from django_filters.views import FilterView
from rules.contrib.views import PermissionRequiredMixin

from editor.views import LoginRequiredMixin

from .forms import (IndividualAccountFilter, IndividualAccountForm,
                    IndividualAccountResetPwdForm)
from .models import IndividualAccount


class OrganizationCheckMixin(PermissionRequiredMixin, LoginRequiredMixin):
    permission_required = 'individual_subscription.manage_account'

    def get_queryset(self):
        qs = IndividualAccount.objects.order_by('-id')
        ids = [account.id for account in qs if self.request.user.has_perm(
               'individual_subscription.manage_account', account)]
        return qs.filter(id__in=ids)


class IndividualAccountList(OrganizationCheckMixin, FilterView):
    filterset_class = IndividualAccountFilter
    paginate_by = 10


class IndividualAccountCreate(OrganizationCheckMixin, CreateView):
    model = IndividualAccount
    form_class = IndividualAccountForm
    template_name = 'individual_subscription/individualaccount_create.html'

    def get_success_url(self):
        return reverse('individual_subscription:account_list')

    def get_form_kwargs(self):
        kwargs = super(IndividualAccountCreate, self).get_form_kwargs()
        kwargs.update({'user': self.request.user})
        return kwargs


class IndividualAccountUpdate(OrganizationCheckMixin, UpdateView):
    model = IndividualAccount
    template_name = 'individual_subscription/individualaccount_update.html'
    fields = ['firstname', 'lastname', 'email', ]

    def get_success_url(self):
        return reverse('individual_subscription:account_list')


class IndividualAccountDelete(OrganizationCheckMixin, DeleteView):
    model = IndividualAccount

    def get_success_url(self):
        return reverse('individual_subscription:account_list')


class IndividualAccountResetPwd(OrganizationCheckMixin, UpdateView):
    model = IndividualAccount
    form_class = IndividualAccountResetPwdForm
    template_name = 'individual_subscription/individualaccount_reset_pwd.html'

    def get_success_url(self):
        return reverse('individual_subscription:account_list')
