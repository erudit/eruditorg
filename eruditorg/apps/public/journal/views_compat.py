from typing import Optional
from typing import Tuple

from django.urls import reverse
from django.db.models import Q
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.views.generic import RedirectView
from django.core.exceptions import MultipleObjectsReturned

from erudit.fedora.utils import get_pids
from erudit.models import Article
from erudit.models import Issue
from erudit.models import Journal
from erudit.solr.models import SolrData
from .viewmixins import (
    RedirectExceptionsToFallbackWebsiteMixin,
    SolrDataMixin,
)
from base.viewmixins import ActivateLegacyLanguageViewMixin


class JournalDetailCheckRedirectView(
    RedirectExceptionsToFallbackWebsiteMixin, RedirectView,
    ActivateLegacyLanguageViewMixin
):
    permanent = True

    def get_redirect_url(self, *args, **kwargs):
        self.activate_legacy_language(*args, **kwargs)

        if 'code' in kwargs:
            journal = Journal.legacy_objects.get_by_id_or_404(
                kwargs['code']
            )
            return reverse(
                'public:journal:journal_detail', args=[
                    journal.code,
                ]
            ) if journal.current_issue else reverse(self.pattern_name, args=[journal.code])
        raise Http404


class IssueDetailRedirectView(
    RedirectExceptionsToFallbackWebsiteMixin, RedirectView, ActivateLegacyLanguageViewMixin
):
    pattern_name = 'public:journal:issue_detail'
    permanent = True

    def get_redirect_url(self, *args, **kwargs):
        self.activate_legacy_language(*args, **kwargs)
        ticket = self.request.GET.get('ticket')

        # Get the journal or raise 404.
        journal_code = kwargs.get('journal_code')
        journal = Journal.legacy_objects.get_by_id_or_404(journal_code)

        # If a specific ID is included in the request, try to load it from Fedora and generate its
        # URL, otherwise raise 404. If a ticket is also included in the request, add it to the URL.
        if 'id' in self.request.GET:
            localidentifier = self.request.GET.get('id')
            try:
                issue = Issue.from_fedora_ids(
                    journal.code,
                    localidentifier
                )
                redirect_url = reverse(self.pattern_name, args=[
                    journal.code,
                    issue.volume_slug,
                    localidentifier,
                ])
                if ticket:
                    return "{url}?ticket={ticket}".format(
                        url=redirect_url,
                        ticket=ticket
                    )
                else:
                    return redirect_url
            except Issue.DoesNotExist:
                raise Http404()

        # Otherwise, we need to figure out wich issue is requested. We first get a queryset of all
        # issues related to the journal.
        issue_qs = Issue.objects.select_related('journal').filter(journal=journal)

        # Get all the provided keyword arguments.
        localidentifier = kwargs.get('localidentifier', '')
        year = kwargs.get('year', '')
        volume = kwargs.get('v', '')
        number = kwargs.get('n', '')

        # Then, based on the provided keyword arguments, we generate additional filters, trying to
        # make them not too strict to avoid no results and not too wide to avoid multiple results.
        additional_filter = Q()
        if localidentifier:
            additional_filter.add(Q(localidentifier=localidentifier), Q.AND)
        else:
            if year:
                additional_filter.add((Q(year=year) | Q(publication_period__contains=year)), Q.AND)
            if volume:
                volume_filter = Q(_connector=Q.OR)
                volume_filter.add(Q(volume=volume), Q.OR)
                # If we get multiple volumes like "1-3", we need to search for "1-3" OR "1" OR "3".
                if '-' in volume:
                    for v in volume.split('-'):
                        volume_filter.add(Q(volume=v), Q.OR)
                # Or if we get only "3", we need to search for "3" OR "3-*" OR "*-3".
                else:
                    volume_filter.add(
                        Q(volume__startswith='{}-'.format(volume)) |
                        Q(volume__endswith='-{}'.format(volume)),
                        Q.OR
                    )
                additional_filter.add(volume_filter, Q.AND)
            if number:
                number_filter = Q(_connector=Q.OR)
                number_filter.add(Q(number=number) | Q(localidentifier=number), Q.OR)
                # If we get multiple numbers like "1-3", we need to search for "1-3" OR "1" OR "3".
                if '-' in number:
                    for n in number.split('-'):
                        number_filter.add(Q(number=n) | Q(localidentifier=n), Q.OR)
                # Or if we get only "3", we need to search for "3" OR "3-*" OR "*-3".
                else:
                    number_filter.add(
                        Q(number__startswith='{}-'.format(number)) |
                        Q(number__endswith='-{}'.format(number)) |
                        Q(localidentifier__startswith='{}-'.format(number)) |
                        Q(localidentifier__endswith='-{}'.format(number)),
                        Q.OR
                    )
                additional_filter.add(number_filter, Q.AND)

        # Try to get the object with the additional filters, or raise 404 if no object is found.
        # If multiple objects are found, we apply the filters again and default to the last one.
        try:
            issue = get_object_or_404(issue_qs, additional_filter)
        except MultipleObjectsReturned:
            issue = issue_qs.filter(additional_filter).last()
            if issue is None:
                raise Http404

        # Finally, we can generate the redirect URL.
        redirect_url = reverse(self.pattern_name, args=[
            journal.code,
            issue.volume_slug,
            issue.localidentifier,
        ])
        if ticket:
            return "{url}?ticket={ticket}".format(
                url=redirect_url,
                ticket=ticket
            )
        else:
            return redirect_url


class ArticleDetailRedirectView(
    ActivateLegacyLanguageViewMixin, RedirectExceptionsToFallbackWebsiteMixin,
    RedirectView, SolrDataMixin,
):
    pattern_name = 'public:journal:article_detail'
    permanent = True

    def get_redirect_url(self, *args, **kwargs):
        self.activate_legacy_language(*args, **kwargs)
        if 'format_identifier' in kwargs and kwargs['format_identifier'] == 'xml':
            self.pattern_name = 'public:journal:article_raw_xml'

        if 'format_identifier' in kwargs and kwargs['format_identifier'] == 'pdf':
            self.pattern_name = 'public:journal:article_raw_pdf'

        article_fedora_ids = get_fedora_ids_from_url_kwargs(self.solr_data, kwargs)
        if article_fedora_ids is None:
            raise Http404
        else:
            try:
                article = Article.from_fedora_ids(*article_fedora_ids)
            except Article.DoesNotExist:
                raise Http404
            url = super().get_redirect_url(
                journal_code=article.issue.journal.code, issue_slug=article.issue.volume_slug,
                issue_localid=article.issue.localidentifier,
                localid=article.localidentifier)
            ticket = self.request.GET.get('ticket')
            if ticket:
                url += '?ticket={}'.format(ticket)
            return url


def get_issue_from_year_volume_number(journal_code: str, year: str, volume: str,
                                      number: Optional[str]) -> Optional[Issue]:
    """
    Useful for URLS legacy_article_detail & legacy_article_detail_culture.

    """
    try:
        return Issue.objects.get(journal__code=journal_code,
                                 year=year,
                                 volume=volume,
                                 number=number)
    except Issue.DoesNotExist:
        return None


def get_fedora_ids_from_url_kwargs(
    solr_data: SolrData, kwargs: dict
) -> Optional[Tuple[str, str, str]]:
    journal_code = kwargs.get('journal_code')
    issue_localid = kwargs.get('issue_localid')
    article_localid = kwargs.get('localid')
    year = kwargs.get('year')
    volume = kwargs.get('v')
    number = kwargs.get('issue_number')
    if not article_localid:
        return None
    if journal_code and not issue_localid:
        # all URLs include the journal's code except for the `iderudit` ones
        # if the url has year, volume and maybe number we try to find the issue in the db
        issue = get_issue_from_year_volume_number(journal_code, year, volume, number)
        if issue:
            issue_localid = issue.localidentifier

    if not issue_localid:
        # We only have the article_localid, ex: iderudit URLs
        # we try with solr first, it's cheaper than searching in fedora
        ids = solr_data.get_fedora_ids(article_localid)
        if ids is not None:
            journal_code, issue_localid, _ = ids
        else:
            # if not found in solr, it might be in fedora anyway (eg. because it's prepublished)
            search_results = get_pids('pid~*.{}'.format(article_localid))
            if search_results:
                article_pid = search_results[0]
                journal_code, issue_localid = article_pid.split('.')[-3:-1]
            else:
                return None
    return journal_code, issue_localid, article_localid
