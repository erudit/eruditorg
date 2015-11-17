from django.conf.urls import url

from editor.views import IssueSubmissionCreate, IssueSubmissionUpdate, DashboardView

urlpatterns = [
    url(r'^numero/ajout', IssueSubmissionCreate.as_view(), name='add'),
    url(r'^numero/(?P<pk>[0-9]+)/$', IssueSubmissionUpdate.as_view(), name='update'),
    url(r'', DashboardView.as_view(), name='dashboard')
]
