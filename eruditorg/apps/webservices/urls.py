from django.conf.urls import include
from django.conf.urls import url

from .views.restrictions import RetroRestrictionsView


urlpatterns = [
    url(r'^sushi/', include('apps.webservices.sushi.urls', namespace='sushi')),
    url(r'^restrictions-retro/$', RetroRestrictionsView.as_view(), name='restrictions_retro'),
]
