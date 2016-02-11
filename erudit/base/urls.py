"""erudit URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import include, url
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from django.views.generic import RedirectView
from django.views.generic import TemplateView

from . import urls_compat


urlpatterns = i18n_patterns(
    url('^', include('django.contrib.auth.urls')),

    url(r'^grappelli/', include('grappelli.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^upload/', include('plupload.urls', namespace='plupload')),

    # The PDF viewer exposes a PDF.js template
    url(r'^pdf-viewer\.html$',
        TemplateView.as_view(template_name='pdf/viewer.html'), name='pdf-viewer'),

    # Apps
    url(r'^', include('apps.public.urls')),
    url(_(r'^espace-utilisateur/'), include('apps.userspace.urls', namespace='userspace')),

    # Compatibility URLs
    url('^', include(urls_compat.urlpatterns)),

    # Catchall
    url(r'', RedirectView.as_view(url="/espace-utilisateur/", permanent=False)),
)
