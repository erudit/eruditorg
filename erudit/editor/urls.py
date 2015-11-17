from django.conf.urls import url

from editor.views import JournalSubmissionCreate, JournalSubmissionUpdate, DashboardView

urlpatterns = [
    url(r'^numero/ajout', JournalSubmissionCreate.as_view(), name='add'),
    url(r'^numero/(?P<pk>[0-9]+)/$', JournalSubmissionUpdate.as_view(), name='update'),
    url(r'', DashboardView.as_view(), name='dashboard')
]
