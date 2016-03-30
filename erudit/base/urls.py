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

from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from django.views.generic import RedirectView
from django.views.generic import TemplateView
from django.views.i18n import javascript_catalog
from apps.public.journal.views import LatestIssuesRSSView

from . import urls_compat


js_info_dict = {
    'packages': ('base', ),
}

urlpatterns = i18n_patterns(
    url('^', include('django.contrib.auth.urls')),
    url(r'^jsi18n/$', javascript_catalog, js_info_dict, name='javascript-catalog'),

    url(r'^grappelli/', include('grappelli.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^upload/', include('plupload.urls', namespace='plupload')),

    # The PDF viewer exposes a PDF.js template
    url(r'^pdf-viewer\.html$',
        TemplateView.as_view(template_name='pdf_viewer.html'), name='pdf-viewer'),

    url(_(r'^rss\.xml$'), LatestIssuesRSSView(), name='latest-issues-rss'),

    # Apps
    url(_(r'^espace-utilisateur/'), include('apps.userspace.urls', namespace='userspace')),
    url(r'^', include('apps.public.urls', namespace='public')),

    # Compatibility URLs
    url('^', include(urls_compat.urlpatterns)),

    # Catchall
    url(r'', RedirectView.as_view(url="/espace-utilisateur/", permanent=False)),
)

# In DEBUG mode, serve media files through Django.
if settings.DEBUG:
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns
    from django.views.static import serve
    urlpatterns += staticfiles_urlpatterns()
    # Remove leading and trailing slashes so the regex matches.
    media_url = settings.MEDIA_URL.lstrip('/').rstrip('/')
    urlpatterns += [
        # Test 503, 500, 404 and 403 pages
        url(r'^403/$', TemplateView.as_view(template_name='403.html')),
        url(r'^404/$', TemplateView.as_view(template_name='404.html')),
        url(r'^500/$', TemplateView.as_view(template_name='500.html')),
        url(r'^503/$', TemplateView.as_view(template_name='503.html')),

        url(r'^%s/(?P<path>.*)$' % media_url, serve, {'document_root': settings.MEDIA_ROOT}),
    ]
