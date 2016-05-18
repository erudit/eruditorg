from django.conf.urls import url
from django.utils.translation import ugettext_lazy as _

from . import views


urlpatterns = [
    url(_(r'^numero/$'), views.IssueSubmissionList.as_view(), name='issues'),
    url(_(r'^numero/ajout/$'), views.IssueSubmissionCreate.as_view(), name='add'),
    url(_(r'^numero/(?P<pk>[0-9]+)/$'), views.IssueSubmissionUpdate.as_view(), name='update'),

    url(_(r'^numero/(?P<pk>[0-9]+)/soumettre/$'),
        views.IssueSubmissionSubmitView.as_view(), name='transition_submit'),
    url(_(r'^numero/(?P<pk>[0-9]+)/approuver/$'),
        views.IssueSubmissionApproveView.as_view(), name='transition_approve'),
    url(_(r'^numero/(?P<pk>[0-9]+)/refuser/$'),
        views.IssueSubmissionRefuseView.as_view(), name='transition_refuse'),
    url(_(r'^numero/(?P<pk>[0-9]+)/archiver/$'),
        views.IssueSubmissionArchiveView.as_view(), name='transition_archive'),

    url(_(r'^numero/fichier/(?P<pk>[0-9]+)/$'),
        views.IssueSubmissionAttachmentView.as_view(), name='attachment_detail'),
]
