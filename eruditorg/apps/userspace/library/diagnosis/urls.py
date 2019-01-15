from django.conf.urls import url
from . import views

app_name = "diagnosis"

urlpatterns = [
    url(r'^$', views.DiagnosisLandingView.as_view(), name='landing'),
]
