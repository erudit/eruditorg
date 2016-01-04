import django_filters

from .models import IndividualAccount


class IndividualAccountFilter(django_filters.FilterSet):
    class Meta:
        model = IndividualAccount
        fields = {
            'firstname': ['icontains', ],
            'lastname': ['icontains', ],
            'organization_policy': ['exact', ]
        }
