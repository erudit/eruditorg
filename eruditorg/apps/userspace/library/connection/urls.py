from django.urls import re_path
from . import views

app_name = "connection"

urlpatterns = [
    re_path(r"^$", views.ConnectionLandingView.as_view(), name="landing"),
]
