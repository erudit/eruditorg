from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.DiagnosisLandingView.as_view(), name='landing'),
]
