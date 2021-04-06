from django.urls import re_path
from . import views

app_name = "diagnosis"

urlpatterns = [
    re_path(r"^$", views.DiagnosisLandingView.as_view(), name="landing"),
]
