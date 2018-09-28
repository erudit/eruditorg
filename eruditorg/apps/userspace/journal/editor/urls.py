from django.conf.urls import url
from django.utils.translation import ugettext_lazy as _

from . import views

app_name = "editor"

urlpatterns = [
    url(_(r'^numero/$'), views.IssueSubmissionListView.as_view(), name='issues'),
    url(_(r'^numero/ajout/$'), views.IssueSubmissionCreate.as_view(), name='add'),
    url(_(r'^numero/(?P<pk>[0-9]+)/$'), views.IssueSubmissionDetailView.as_view(), name='detail'),
    url(_(r'^numero/(?P<pk>[0-9]+)/edition/$'),
        views.IssueSubmissionUpdate.as_view(), name='update'),

    url(_(r'^numero/(?P<pk>[0-9]+)/soumettre/$'),
        views.IssueSubmissionSubmitView.as_view(), name='transition_submit'),
    url(_(r'^numero/(?P<pk>[0-9]+)/approuver/$'),
        views.IssueSubmissionApproveView.as_view(), name='transition_approve'),
    url(_(r'^numero/(?P<pk>[0-9]+)/refuser/$'),
        views.IssueSubmissionRefuseView.as_view(), name='transition_refuse'),

    url(_(r'^numero/(?P<pk>[0-9]+)/supprimer/$'),
        views.IssueSubmissionDeleteView.as_view(), name='delete'),

    url(_(r'^numero/fichier/(?P<pk>[0-9]+)/$'),
        views.IssueSubmissionAttachmentView.as_view(), name='attachment_detail'),
]
