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
from django.contrib import admin
from django.views.generic import RedirectView
from django.views.generic import TemplateView

from . import urls_compat


urlpatterns = [
    url('^', include('django.contrib.auth.urls')),

    url(r'^grappelli/', include('grappelli.urls')),
    url(r'^admin/', include(admin.site.urls)),

    url(r'^pdf-viewer\.html$',
        TemplateView.as_view(template_name='pdf/viewer.html'), name='pdf-viewer'),

    # User space urls
    url(r'^espace-utilisateur/editeur/',
        include('editor.urls', namespace='editor')),
    url(r'^espace-utilisateur/organisations/',
        include('individual_subscription.urls',
                namespace='individual_subscription')),
    url(r'^espace-utilisateur/',
        include('userspace.urls', namespace='userspace'),
        name="login"),

    # Public website urls
    url(r'^', include('journal.urls', namespace='journal')),
    url(r'^livre/', include('book.urls', namespace='book')),
    url(r'^recherche/', include('search.urls', namespace='search')),
    url(r'^these/', include('thesis.urls', namespace='thesis')),
    url(r'^organisations/', include('individual_subscription.urls',
        namespace='individual_subscription')),

    url(r'^upload/', include('plupload.urls', namespace='plupload'),),
    # TODO: move to user space
    url(r'^abonnements/', include('subscription.urls')),

    # Compatibility URLs
    url('^', include(urls_compat.urlpatterns)),

    # Catchall
    url(r'', RedirectView.as_view(url="/espace-utilisateur/", permanent=False)),
]
