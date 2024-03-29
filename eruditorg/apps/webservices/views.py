import datetime as dt

from lxml import etree
from lxml.builder import E

from django.conf import settings
from django.http import HttpResponse
from django.db.models import Q
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.generic import View, TemplateView

from core.subscription.restriction.models import Abonne, Adressesip, Revueabonne
from erudit.models import Journal


@method_decorator(cache_page(settings.LONG_TTL), name="dispatch")
class RestrictionsView(View):
    http_method_names = [
        "get",
    ]

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
                E.years(";".join(map(str, embargoed_years))),
                E.embargo_date(date_embargo_begins.strftime("%Y-%m-%d")),
                E.embargo_duration(
                    str(int(journal.embargo_in_months * 30 + (journal.embargo_in_months / 12) * 5)),
                    unit="day",
                ),
                E.embargoed_issues(*[E.issue(localidentifier=x) for x in embargoed]),
                code=journal.code,
                localidentifier=journal.localidentifier,
            )

        journals = Journal.objects.filter(
            collection__is_main_collection=True, open_access=False, active=True
        ).filter(issues__is_published=True)
        root = E.journals(*map(get_journal_elem, journals.distinct().all()))
        return HttpResponse(etree.tostring(root), content_type="text/xml")


class RestrictionsByJournalView(View):
    http_method_names = [
        "get",
    ]

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
                *[
                    E.issue(
                        E.number(str(x.number)),
                        E.volume(str(x.volume)),
                        E.year(str(x.year)),
                        localidentifier=x.localidentifier,
                        embargoed=str(x.embargoed),
                        whitelisted=str(x.force_free_access),
                    )
                    for x in journal.published_issues
                ],
                count=str(len(journal.published_issues)),
                embargoed_count=str(len(embargoed_issues)),
                whitelisted_count=str(len(whitelisted_issues))
            )

            if journal.open_access:
                journal_element = E.journal(
                    issues_elements,
                    code=journal.code,
                    localidentifier=str(journal.localidentifier or ""),
                    embargoed=str(not journal.open_access),
                )
            else:
                journal_element = E.journal(
                    E.embargo_date(journal.date_embargo_begins.strftime("%Y-%m-%d")),
                    E.embargo_duration(
                        str(
                            int(
                                journal.embargo_in_months * 30
                                + (journal.embargo_in_months / 12) * 5
                            )
                        ),
                        unit="day",
                    ),
                    issues_elements,
                    code=journal.code,
                    localidentifier=str(journal.localidentifier or ""),
                    embargoed=str(not journal.open_access),
                )
            return journal_element

        journal = Journal.objects.filter(
            Q(code=journal_code) | Q(localidentifier=journal_code),
            collection__is_main_collection=True,
            active=True,
        )

        if journal.exists():
            root = get_journal_elem(*journal)
        else:
            root = E.error(journal_code + "This journal does not exist or is not yet configured")

        return HttpResponse(etree.tostring(root), content_type="text/xml")


class CrknIpUnbView(TemplateView):
    content_type = "text/xml"
    template_name = "webservices/crkn_ipunb.xml"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["listeips"] = {}

        # Get all UNB journals subscribers IDs for the current year from the `restriction` database
        # to filter IP addresses and subscribers in the next two queries. We need to do this
        # because there is no foreign keys in the `restriction` database so we can't use Django's
        # field lookups.
        subscribers_id = Revueabonne.objects.filter(
            revueid__in=["53", "55", "54", "59", "60", "62", "63", "64", "67", "75", "76", "100"],
            anneeabonnement=dt.datetime.now().year,
        ).values("abonneid")

        # Get all UNB journals subscribers from the `restriction` database.
        subscribers = (
            Abonne.objects.filter(
                abonneid__in=subscribers_id,
            )
            .order_by("abonne")
            .values("abonneid", "abonne")
        )

        # Get all UNB journals subscribers IP addresses from the `restriction` database.
        ip_addresses = (
            Adressesip.objects.filter(
                abonneid__in=subscribers_id,
            )
            .order_by("ip")
            .values("abonneid", "ip")
        )

        # Add the subscribers names and IP addresses to the `listeips` dict to send to the template.
        for subscriber in subscribers:
            context["listeips"][subscriber["abonneid"]] = {
                "abonne": subscriber["abonne"],
                "ips": [],
            }
        for ip_address in ip_addresses:
            context["listeips"][ip_address["abonneid"]]["ips"].append(ip_address["ip"])

        return context
