from django.conf.urls import url

from .views import RestrictionsView, RestrictionsByJournalView

app_name = "webservices"

urlpatterns = [
    url(r"^restrictions/$", RestrictionsView.as_view(), name="restrictions"),
    url(
        r"^restrictionsByJournal/(?P<journal_code>\w+)/$",
        RestrictionsByJournalView.as_view(),
        name="restrictionsByJournal",
    ),
]
