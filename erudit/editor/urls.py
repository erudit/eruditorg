from django.conf.urls import url

from editor.views import JournalSubmissionCreate

urlpatterns = [
    url(r'^add/', JournalSubmissionCreate.as_view(), name='add'),
]
