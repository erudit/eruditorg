import datetime as dt

from lxml import etree
from lxml.builder import E

from django.http import HttpResponse
from django.views.generic import View

from erudit.models import Journal


class RestrictionsView(View):
    http_method_names = ['get', ]

    def get(self, request):
        def get_revue_elem(journal):
            date_embargo_begins = journal.date_embargo_begins
            if not date_embargo_begins:
                return E.revue()
            min_year = dt.date.today().year + 1
            embargoed = []
            for issue in journal.published_issues:
                if issue.embargoed:
                    date_embargo_begins = min(date_embargo_begins, issue.date_published)
                    min_year = min(min_year, issue.date_published.year)
                    embargoed.append(issue.localidentifier)
            embargoed_years = range(min_year, dt.date.today().year + 1)
            return E.revue(
                E.years(';'.join(map(str, embargoed_years))),
                E.embargo_date(date_embargo_begins.strftime('%Y-%m-%d')),
                E.embargoed_issues(*[E.issue(localidentifier=x) for x in embargoed]),
                identifier=journal.legacy_code)

        journals = Journal.objects.filter(
            collection__is_main_collection=True, open_access=False, active=True)
        root = E.revues(
            *map(get_revue_elem, journals.all())
        )
        return HttpResponse(etree.tostring(root), content_type='text/xml')
