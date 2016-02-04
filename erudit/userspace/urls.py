from django.conf.urls import url

from .views import (DashboardView, PermissionsListView, PermissionsCreateView,
                    PermissionsDeleteView)

urlpatterns = [
    url(r'permissions/$', PermissionsListView.as_view(), name='perm_list'),
    url(r'permissions/ajout/$', PermissionsCreateView.as_view(),
        name='perm_create'),
    url(r'permissions/(?P<pk>[0-9]+)/supprimer/$',
        PermissionsDeleteView.as_view(), name='perm_delete'),
    url(r'$', DashboardView.as_view(), name='dashboard'),
]
