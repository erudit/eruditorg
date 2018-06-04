from django.conf.urls import include
from django.conf.urls import url
from django.views.decorators.cache import cache_page

from .views.restrictions import RestrictionsView


urlpatterns = [
    url(r'^sushi/', include('apps.webservices.sushi.urls', namespace='sushi')),
    url(
        r'^restrictions/$',
        cache_page(3600 * 24)(RestrictionsView.as_view()), name='restrictions'
    ),
]
