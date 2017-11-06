from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.DiagnosticLandingView.as_view(), name='landing'),
]
