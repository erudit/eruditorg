from django.conf import settings
from django.urls import include, re_path
from django.conf.urls.i18n import i18n_patterns
from django.views.generic import RedirectView
from django.contrib import admin
from django.contrib.sitemaps import views as sitemap_views
from django.utils.translation import gettext_lazy as _
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers
from django.views.generic import TemplateView
from django.views.i18n import JavaScriptCatalog
from django_js_reverse import views as js_reverse_views

from resumable_uploads import urls as resumable_uploads_urls

from . import sitemaps
from . import urls_compat
from apps.public.urls import public_urlpatterns
from apps.public.journal.urls import google_scholar_urlpatterns
from apps.public.journal.views import IssueRawCoverpageView, JournalRawLogoView
from apps.webservices.views import CrknIpUnbView

sitemaps_dict = {
    "journal": sitemaps.JournalSitemap,
    "issue": sitemaps.IssueSitemap,
    "article": sitemaps.ArticleSitemap,
}


urlpatterns = [
    re_path(r"^index\.html$", RedirectView.as_view(pattern_name="public:home")),
    re_path(
        r"^robots\.txt$",
        TemplateView.as_view(template_name="robots.txt", content_type="text/plain"),
        name="robots-txt",
    ),
    re_path(
        r"^sitemap\.xml$",
        sitemap_views.index,
        {"sitemaps": sitemaps_dict, "sitemap_url_name": "sitemaps"},
        name="sitemap",
    ),
    re_path(
        r"^sitemap-(?P<section>.+)\.xml$",
        cache_page(settings.LONG_TTL)(sitemap_views.sitemap),
        {"sitemaps": sitemaps_dict},
        name="sitemaps",
    ),
    # Google Scholar URLs
    re_path(r"^scholar/", include(google_scholar_urlpatterns)),
    # CRKN ipunb service.
    re_path(r"^ws/crkn/ipunb.xml", CrknIpUnbView.as_view(), name="crkn_ipunb"),
    re_path(
        _(r"^couverture/(?P<localidentifier>[\w-]+)/(?P<last_modified_date>[\w-]+).jpg"),
        vary_on_headers("accept-encoding")(IssueRawCoverpageView.as_view()),
        name="issue_coverpage_cdn",
    ),
    re_path(
        _(r"^logo/(?P<code>[\w-]+)/(?P<last_modified_date>[\w-]+).jpg"),
        JournalRawLogoView.as_view(),
        name="journal_logo_cdn",
    ),
    # Compatibility URLs
    re_path("^", include(urls_compat.urlpatterns)),
]

if settings.EXPOSE_OPENMETRICS:
    urlpatterns.append(
        re_path("^prometheus/", include("django_prometheus.urls")),
    )

urlpatterns += i18n_patterns(
    re_path(r"^jsi18n/$", JavaScriptCatalog.as_view(packages=["base"]), name="javascript-catalog"),
    re_path(r"^jsreverse/$", js_reverse_views.urls_js, name="js_reverse"),
    re_path(r"^" + settings.ADMIN_URL, admin.site.urls),
    re_path(
        r"^upload/",
        include(
            (
                resumable_uploads_urls.urlpatterns,
                "resumable_uploads",
            )
        ),
    ),
    # Apps
    re_path(_(r"^espace-utilisateur/"), include("apps.userspace.urls")),
    re_path(r"^webservices/", include("apps.webservices.urls")),
    re_path(r"^", include(public_urlpatterns)),
)

# In DEBUG mode, serve media files through Django.
if settings.DEBUG:
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns
    from django.views.static import serve

    urlpatterns += staticfiles_urlpatterns()
    # Remove leading and trailing slashes so the regex matches.
    media_url = settings.MEDIA_URL.lstrip("/").rstrip("/")
    urlpatterns += [
        # Test 503, 500, 404 and 403 pages
        re_path(r"^403/$", TemplateView.as_view(template_name="public/403.html")),
        re_path(r"^404/$", TemplateView.as_view(template_name="public/404.html")),
        re_path(r"^500/$", TemplateView.as_view(template_name="public/500.html")),
        re_path(r"^503/$", TemplateView.as_view(template_name="public/503.html")),
        re_path(r"^%s/(?P<path>.*)$" % media_url, serve, {"document_root": settings.MEDIA_ROOT}),
    ]
    import debug_toolbar

    urlpatterns = [
        re_path(r"^__debug__/", include(debug_toolbar.urls)),
    ] + urlpatterns


handler403 = "apps.public.views.forbidden_view"
handler404 = "apps.public.views.not_found_view"
handler500 = "apps.public.views.internal_error_view"
