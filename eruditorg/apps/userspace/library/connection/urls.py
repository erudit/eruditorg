from django.conf.urls import url
from . import views

app_name = "connection"

urlpatterns = [
    url(r"^$", views.ConnectionLandingView.as_view(), name="landing"),
]
