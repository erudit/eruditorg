from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.core.urlresolvers import reverse

from django.contrib.auth.decorators import user_passes_test
from django_filters.views import FilterView

from editor.views import LoginRequiredMixin

from .forms import (IndividualAccountFilter, IndividualAccountForm,
                    IndividualAccountResetPwdForm)
from .models import IndividualAccount


class OrganizationCheckMixin(LoginRequiredMixin):

    @classmethod
    def check_access(cls, user):
        if user.is_superuser or user.is_staff:
            return True
        elif hasattr(user, 'organizations_managed') and \
                user.organizations_managed.count() > 0:
            return True
        else:
            return False

    @classmethod
    def as_view(cls, **initkwargs):
        view = super().as_view(**initkwargs)
        fct = user_passes_test(cls.check_access)
        return fct(view)

    def get_queryset(self):
        qs = IndividualAccount.objects.select_related('organization_policy').order_by('-id')
        if self.request.user.is_superuser or self.request.user.is_staff:
            return qs.all()
        elif self.request.user.organizations_managed.count() > 0:
            org_ids = [o.id for o in self.request.user.organizations_managed.all()]
            return qs.filter(organization_policy__in=org_ids)
        else:
            return qs.none()


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
