from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.i18n import i18n_patterns
from django.views.generic import RedirectView
from django.contrib import admin
from django.contrib.sitemaps import views as sitemap_views
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.cache import cache_page
from django.views.generic import TemplateView
from django.views.i18n import JavaScriptCatalog
from django_js_reverse import views as js_reverse_views

from resumable_uploads import urls as resumable_uploads_urls

from . import sitemaps
from . import urls_compat
from . import views

js_info_dict = {
    'packages': ['base', ],
}

sitemaps_dict = {
    'journal': sitemaps.JournalSitemap,
    'issue': sitemaps.IssueSitemap,
    'article': sitemaps.ArticleSitemap,
}

urlpatterns = [
    url(r'^index\.html$', RedirectView.as_view(pattern_name="public:home")),
    url(r'^robots\.txt$', TemplateView.as_view(template_name='robots.txt',
        content_type="text/plain"), name='robots-txt'),
    url(r'^sitemap\.xml$', sitemap_views.index,
        {'sitemaps': sitemaps_dict, 'sitemap_url_name': 'sitemaps'}, name="sitemap"),
    url(r'^sitemap-(?P<section>.+)\.xml$', cache_page(86400)(sitemap_views.sitemap),
        {'sitemaps': sitemaps_dict}, name='sitemaps'),
    # Canonical URLS (see #1934)
    url(r'^revues/', views.canonical_journal_urls_view, name='canonical_journal_urls'),
    # Compatibility URLs
    url('^', include(urls_compat.urlpatterns)),
]

urlpatterns += i18n_patterns(
    url(r'^jsi18n/$', JavaScriptCatalog.as_view(), js_info_dict, name='javascript-catalog'),
    url(r'^jsreverse/$', js_reverse_views.urls_js, name='js_reverse'),

    url(r'^' + settings.ADMIN_URL, admin.site.urls),
    url(r'^upload/', include((resumable_uploads_urls.urlpatterns, "resumable_uploads",))),

    # The PDF viewer exposes a PDF.js template
    url(r'^pdf-viewer\.html$',
        TemplateView.as_view(template_name='pdf_viewer.html'), name='pdf-viewer'),

    # Apps
    url(_(r'^espace-utilisateur/'), include('apps.userspace.urls')),
    url(r'^webservices/', include('apps.webservices.urls')),
    url(r'^', include('apps.public.urls')),
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
        url(r'^403/$', TemplateView.as_view(template_name='public/403.html')),
        url(r'^404/$', TemplateView.as_view(template_name='public/404.html')),
        url(r'^500/$', TemplateView.as_view(template_name='public/500.html')),
        url(r'^503/$', TemplateView.as_view(template_name='public/503.html')),

        url(r'^%s/(?P<path>.*)$' % media_url, serve, {'document_root': settings.MEDIA_ROOT}),
    ]
    import debug_toolbar
    urlpatterns = [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns


handler404 = 'apps.public.views.not_found_view'
handler500 = 'apps.public.views.internal_error_view'
