from django.conf.urls import url
from django.utils.translation import ugettext_lazy as _


from .views import (
    IndividualAccountCreate,
    IndividualAccountUpdate,
    IndividualAccountDelete,
    IndividualAccountList,
    IndividualAccountResetPwd,
)

urlpatterns = [
    url(_(r'^acces/$'), IndividualAccountList.as_view(), name='account_list'),
    url(_(r'^acces/ajout'), IndividualAccountCreate.as_view(), name='account_add'),
    url(_(r'^acces/supprimer/(?P<pk>[0-9]+)/$'), IndividualAccountDelete.as_view(),
        name='account_delete'),
    url(_(r'^acces/(?P<pk>[0-9]+)/$'), IndividualAccountUpdate.as_view(), name='account_update'),
    url(_(r'^acces/nouveau-mdp/(?P<pk>[0-9]+)/$'), IndividualAccountResetPwd.as_view(),
        name='account_reset_pwd'),
]
