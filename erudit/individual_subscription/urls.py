from django.conf.urls import url


from .views import (
    IndividualAccountCreate,
    IndividualAccountUpdate,
    IndividualAccountDelete,
    IndividualAccountList
)

urlpatterns = [
    url(r'^acces/$', IndividualAccountList.as_view(), name='account_list'),
    url(r'^acces/ajout', IndividualAccountCreate.as_view(), name='account_add'),
    url(r'^acces/supprimer/(?P<pk>[0-9]+)/$', IndividualAccountDelete.as_view(), name='account_delete'),
    url(r'^acces/(?P<pk>[0-9]+)/$', IndividualAccountUpdate.as_view(), name='account_update'),
]
