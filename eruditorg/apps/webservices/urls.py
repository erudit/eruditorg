from django.urls import re_path

from .views import RestrictionsView, RestrictionsByJournalView

app_name = "webservices"

urlpatterns = [
    re_path(r"^restrictions/$", RestrictionsView.as_view(), name="restrictions"),
    re_path(
        r"^restrictionsByJournal/(?P<journal_code>\w+)/$",
        RestrictionsByJournalView.as_view(),
        name="restrictionsByJournal",
    ),
]
