import datetime as dt

from lxml import etree
from lxml.builder import E

from django.http import HttpResponse
from django.views.generic import View

from erudit.models import Journal


class RetroRestrictionsView(View):
    http_method_names = ['get', ]

    def get(self, request):
        def get_revue_elem(journal):
            min_year = dt.date.today().year + 1
            for issue in journal.published_issues:
                if issue.embargoed:
                    min_year = min(min_year, issue.date_published.year)
            embargoed_years = range(min_year, dt.date.today().year + 1)
            return E.revue(
                E.years(';'.join(map(str, embargoed_years))),
                identifier=journal.legacy_code)

        journals = Journal.objects.filter(
            collection__is_main_collection=True, open_access=False, active=True)
        root = E.revues(
            *map(get_revue_elem, journals.all())
        )
        return HttpResponse(etree.tostring(root), content_type='text/xml')
