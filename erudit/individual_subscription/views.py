from django.views.generic.edit import CreateView, UpdateView

from django.contrib.auth.decorators import user_passes_test
from django_filters.views import FilterView

from editor.views import LoginRequiredMixin

from .forms import IndividualAccountFilter
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


class IndividualAccountList(OrganizationCheckMixin, FilterView):
    filterset_class = IndividualAccountFilter

    def get_queryset(self):
        if self.request.user.is_superuser or self.request.user.is_staff:
            return IndividualAccount.objects.all()
        elif self.request.user.organizations_managed.count() > 0:
            org_ids = [o.id for o in self.request.user.organizations_managed.all()]
            return IndividualAccount.objects.filter(organization_policy__in=org_ids)
        else:
            return IndividualAccount.objects.none()


class IndividualAccountCreate(OrganizationCheckMixin, CreateView):
    model = IndividualAccount


class IndividualAccountUpdate(OrganizationCheckMixin, UpdateView):
    model = IndividualAccount
