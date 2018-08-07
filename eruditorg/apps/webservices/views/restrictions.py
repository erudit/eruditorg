import datetime as dt

from lxml import etree
from lxml.builder import E

from django.http import HttpResponse
from django.db.models import Q
from django.views.generic import View

from erudit.models import Journal


class RestrictionsView(View):
    http_method_names = ['get', ]

    def get(self, request):

        def get_journal_elem(journal):
            date_embargo_begins = journal.date_embargo_begins
            if not date_embargo_begins:
                return E.journal()
            min_year = dt.date.today().year + 1
            embargoed = []
            for issue in journal.published_issues:
                if issue.embargoed:
                    date_embargo_begins = min(date_embargo_begins, issue.date_published)
                    min_year = min(min_year, issue.date_published.year)
                    embargoed.append(issue.localidentifier)
            embargoed_years = range(min_year, dt.date.today().year + 1)
            return E.journal(
                E.years(';'.join(map(str, embargoed_years))),
                E.embargo_date(date_embargo_begins.strftime('%Y-%m-%d')),
                E.embargo_duration(
                    str(journal.embargo_in_months),
                    unit='month'
                ),
                E.embargoed_issues(*[E.issue(localidentifier=x) for x in embargoed]),
                code=journal.code,
                localidentifier=journal.localidentifier,
                embargo_duration=str(journal.embargo_in_months)
            )

        journals = Journal.objects.filter(
            collection__is_main_collection=True, open_access=False, active=True).filter(
            issues__is_published=True
        )
        root = E.journals(
            *map(get_journal_elem, journals.all())
        )
        return HttpResponse(etree.tostring(root), content_type='text/xml')


class RestrictionsByJournalView(View):
    http_method_names = ['get', ]

    def get(self, request, journal_code=None):

        def get_journal_elem(journal):

            embargoed_issues = []
            whitelisted_issues = []
            for issue in journal.published_issues:
                if issue.embargoed:
                    embargoed_issues.append(issue.localidentifier)
                if issue.force_free_access:
                    whitelisted_issues.append(issue.localidentifier)
            issues_elements = E.issues(
                *[E.issue(
                    E.number(str(x.number)),
                    E.volume(str(x.volume)),
                    E.year(str(x.year)),
                    localidentifier=x.localidentifier,
                    embargoed=str(x.embargoed),
                    whitelisted=str(issue.force_free_access)
                ) for x in journal.published_issues],
                count=str(len(journal.published_issues)),
                embargoed_count=str(len(embargoed_issues)),
                whitelisted_count=str(len(whitelisted_issues))
            )

            if journal.open_access:
                journal_element = E.journal(
                    issues_elements,
                    code=journal.code,
                    localidentifier=journal.localidentifier,
                    embargoed=str(not journal.open_access)
                )
            else:
                journal_element = E.journal(
                    E.embargo_date(journal.date_embargo_begins.strftime('%Y-%m-%d')),
                    E.embargo_duration(
                        str(journal.embargo_in_months),
                        unit='month'
                    ),
                    issues_elements,
                    code=journal.code,
                    localidentifier=journal.localidentifier,
                    embargoed=str(not journal.open_access)
                )

            return journal_element

        journal = Journal.objects.filter(
            Q(code=journal_code) | Q(localidentifier=journal_code),
            collection__is_main_collection=True,
            active=True
        )
        root = get_journal_elem(*journal)
        return HttpResponse(etree.tostring(root), content_type='text/xml')
