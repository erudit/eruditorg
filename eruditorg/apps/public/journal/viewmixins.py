import json
import string
import structlog

from django.db.models import Q
from django.urls import reverse
from django.http import Http404
from django.http.response import HttpResponseRedirect
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.utils.functional import cached_property
from django.utils.translation import gettext as _
from ipware import get_client_ip
from prometheus_client import Counter
from typing import List, Optional

from erudit.models import Article
from erudit.models import Issue
from erudit.models import Journal
from erudit.models import JournalInformation
from erudit.solr.models import (
    SolrData,
    get_solr_data,
)

from .article_access_log import (
    ArticleAccessLog,
    ArticleAccessType,
)

embargoed_article_views_by_subscription_type = Counter(
    "eruditorg_embargoed_article_views_by_subscription_type",
    _("Nombre de consultations d'articles sous embargo par type d'abonnement"),
    ["subscription_type"],
)

logger = structlog.get_logger(__name__)


class SingleJournalMixin:
    """ Simply allows retrieving a Journal instance using its code or localidentifier. """

    def get_journal_queryset(self):
        return Journal.internal_objects.select_related("previous_journal", "next_journal")

    def get_journal(self):
        try:
            return self.get_journal_queryset().get(
                Q(code=self.kwargs["code"]) | Q(localidentifier=self.kwargs["code"])
            )
        except Journal.DoesNotExist:
            raise Http404

    def get_object(self, queryset=None):
        return self.get_journal()

    @cached_property
    def journal(self):
        return self.get_journal()


class ContentAccessCheckMixin:
    """ Defines a way to check whether the current user can browse a given Érudit content. """

    def get_content(self):
        """Returns the considered content.

        By default the method will try to fetch the content using the ``object`` attribute. If this
        attribute is not available the
        :meth:`get_object<django:django.views.generic.detail.SingleObjectMixin.get_object>` method
        will be used. But subclasses can override this to control the way the content is retrieved.
        """
        if hasattr(self, "object") and self.object is not None:
            return self.object
        return self.get_object()

    def _get_subscriptions_kwargs_for_content(self):
        content = self.get_content()
        kwargs = {}
        if isinstance(content, Article):
            # 1- Is the article in open access? Is the article subject to a movable limitation?
            kwargs["article"] = content
        elif isinstance(content, Issue):
            kwargs["issue"] = content
        elif isinstance(content, Journal):
            kwargs["journal"] = content
        return kwargs

    def dispatch(self, *args, **kwargs):
        response = super().dispatch(*args, **kwargs)
        if hasattr(self, "request") and hasattr(self.request, "subscriptions"):
            self.request.subscriptions.set_active_subscription_for(
                **self._get_subscriptions_kwargs_for_content()
            )
        return response

    def get_context_data(self, **kwargs):
        """ Inserts a flag indicating if the content can be accessed in the context. """
        context = super(ContentAccessCheckMixin, self).get_context_data(**kwargs)
        context["content_access_granted"] = self.content_access_granted

        active_subscription = self.request.subscriptions.active_subscription
        if active_subscription:
            context["subscription_type"] = active_subscription.get_subscription_type()
        return context

    @cached_property
    def content_access_granted(self):
        """Returns a boolean indicating if the content can be accessed.

        The following verifications are performed in order to determine if a given content
        can be browsed:

            1- it is in open access or not embargoed
            2- a valid prepublication ticket is provided
            3- the current user has access to it with its individual account
            4- the current IP address is inside the IP address ranges allowed to access to it
        """
        content = self.get_content()
        if isinstance(content, Article):
            issue = content.issue
        elif isinstance(content, Issue):
            issue = content
        else:
            issue = None

        if issue:
            # If the issue is in open access or if it's not embargoed, the access should always be
            # granted.
            if issue.journal.open_access or not issue.embargoed:
                return True

            # If the issue is not published, the access should only be granted if a valid
            # prepublication ticket is provided.
            if not issue.is_published:
                return issue.is_prepublication_ticket_valid(self.request.GET.get("ticket"))

        # Otherwise, check if the user has a valid subscription that provides access to the article.
        kwargs = self._get_subscriptions_kwargs_for_content()
        return self.request.subscriptions.provides_access_to(**kwargs)


class SolrDataMixin:
    @property
    def solr_data(self) -> SolrData:
        return get_solr_data()


class SingleArticleMixin(SolrDataMixin):
    def __init__(self):
        # TODO: make this a private instance variable
        # if this is only used for caching, it should not be accessible directly.
        self.object = None

    def get_object(self, queryset=None) -> Article:
        # We support two IDing scheme here: full PID or localidentifier-only. If we have the full
        # PID, great! that saves us a request to Solr. If not, it's alright too, we just need to
        # fetch the full PID from Solr first.
        if self.object is not None:
            return self.object
        journal_code = self.kwargs.get("journal_code")
        issue_localid = self.kwargs.get("issue_localid")
        localidentifier = self.kwargs.get("localid")
        if not (journal_code and issue_localid):
            fedora_ids = self.solr_data.get_fedora_ids(localidentifier)
            if fedora_ids is None:
                raise Http404()
            journal_code, issue_localid, localidentifier = fedora_ids
        try:
            self.object = Article.from_fedora_ids(journal_code, issue_localid, localidentifier)
            return self.object
        except Article.DoesNotExist:
            raise Http404()


class SingleArticleWithScholarMetadataMixin(SingleArticleMixin):
    """ Add Google Scholar Metadata to the context """

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        article = self.get_object()
        context["citation_title_metadata"] = article.title
        context[
            "citation_journal_title_metadata"
        ] = article.erudit_object.get_formatted_journal_title()
        context["citation_references"] = article.erudit_object.get_references(html=False)
        return context


class PrepublicationTokenRequiredMixin:
    def get(self, request, *args, **kwargs):

        object = self.get_object()
        if isinstance(object, Article):
            issue = object.issue
        elif isinstance(object, Issue):
            issue = object
        else:
            raise ValueError("This mixin should only be used with Article and Issue objects")

        if not issue.is_published and not issue.is_prepublication_ticket_valid(
            request.GET.get("ticket")
        ):
            return HttpResponseRedirect(
                reverse("public:journal:journal_detail", args=(issue.journal.code,))
            )

        return super().get(request, *args, **kwargs)


class ArticleViewMetricCaptureMixin:
    tracking_article_view_granted_metric_name = "erudit__journal__article_view"
    tracking_view_type = "html"

    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        subscription = request.subscriptions.active_subscription
        if response.status_code == 200 and subscription is not None and self.content_access_granted:
            # We register this metric only if the article can be viewed
            embargoed_article_views_by_subscription_type.labels(
                subscription_type=subscription.get_subscription_type()
            ).inc(1)
        return response


class MetaInfoIssueMixin:
    def get_cache_version(
        self, journal_info: Optional[JournalInformation] = None, issue: Optional[Issue] = None
    ) -> str:
        """Generate a cache version for caching template fragments.

        Since those template fragments display informations about the journal information and the
        current issue, we need a cache version that invalidates the cache when one of those two
        objects is updated. To do that, we concatenate the updated timestamp of both objects, if
        provided, to generate the cache version.
        """
        journal_info_updated = str(journal_info.updated.timestamp() if journal_info else None)
        issue_fedora_updated = str(
            issue.fedora_updated.timestamp() if issue and issue.fedora_updated else None
        )
        return f"{journal_info_updated}-{issue_fedora_updated}"

    def get_contributors(self, journal_info=None, issue=None):
        contributors = {
            "directors": [],
            "editors": [],
        }

        # Check if a journal_info has been provided and if it has any contributors.
        if journal_info is not None and journal_info.contributor_set.exists():
            for director in journal_info.get_directors():
                contributors["directors"].append(
                    {
                        "name": director.name,
                        "role": [director.role] if director.role is not None else [],
                    }
                )
            for editor in journal_info.get_editors():
                contributors["editors"].append(
                    {
                        "name": editor.name,
                        "role": [editor.role] if editor.role is not None else [],
                    }
                )

        # Otherwise, use the contributors from the provided issue.
        elif issue is not None:
            for director in issue.erudit_object.get_directors():
                contributors["directors"].append(
                    {
                        "name": director.format_name(),
                        "role": list(director.role.values()),
                    }
                )
            for editor in issue.erudit_object.get_editors():
                contributors["editors"].append(
                    {
                        "name": editor.format_name(),
                        "role": list(editor.role.values()),
                    }
                )

        return contributors

    def get_issn(self, journal=None, issue=None):
        issn = {
            "print": None,
            "web": None,
        }

        # If we are provided with an issue, it should always be the source for the ISSN.
        if issue:
            issn["print"] = issue.erudit_object.issn
            issn["web"] = issue.erudit_object.issn_num
        # Otherwise, it means the journal has not published yet, so get the ISSN from the Django
        # Journal object.
        elif journal:
            issn["print"] = journal.issn_print
            issn["web"] = journal.issn_web

        return issn

    def get_langcodes(
        self,
        current_issue: Optional[Issue] = None,
        journal_information: Optional[JournalInformation] = None,
    ) -> List[str]:
        """Get the journal's langcodes either from the current issue's XML or from the journal
        information's model."""
        langcodes = current_issue.erudit_object.get_languages() if current_issue else []
        if not langcodes and journal_information:
            for language in journal_information.main_languages:
                if language == "F":
                    langcodes.append("fr")
                else:
                    langcodes.append("en")
            for language in journal_information.other_languages.all():
                langcodes.append(language.code)
        return langcodes


class ArticleAccessLogMixin:
    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)

        # Do not log if status code is not 200.
        if response.status_code != 200:
            return response

        article = self.get_object()
        issue = article.issue
        journal = issue.journal

        # Do not log if issue is not published.
        if not issue.is_published:
            return response

        active_subscription = request.subscriptions.active_subscription
        if active_subscription and active_subscription.organisation:
            restriction_subscriber_id = active_subscription.organisation.account_id
            is_subscribed_to_journal = active_subscription.provides_access_to(journal=journal)
        else:
            restriction_subscriber_id = None
            is_subscribed_to_journal = False

        if "article_access_log_session_key" in request.COOKIES:
            session_key = request.COOKIES["article_access_log_session_key"]
        else:
            # Generate a 32 characters session key with lowercase letters and digits.
            session_key = get_random_string(32, string.ascii_lowercase + string.digits)
            response.set_cookie("article_access_log_session_key", session_key, max_age=3600)

        username = request.user.username if request.user else ""

        client_ip, _ = get_client_ip(request, proxy_order="right-most")
        article_access_log = ArticleAccessLog(
            # apache
            timestamp=timezone.now(),
            accessed_uri=request.get_raw_uri(),
            ip=client_ip,
            protocol=request.META.get("SERVER_PROTOCOL", ""),
            user_agent=request.META.get("HTTP_USER_AGENT", ""),
            referer=request.META.get("HTTP_REFERER", ""),
            subscriber_referer=request.session.get("HTTP_REFERER", ""),
            # article info
            article_id=article.localidentifier,
            article_full_pid=article.get_full_identifier(),
            # subscription info
            restriction_subscriber_id=restriction_subscriber_id,
            is_subscribed_to_journal=is_subscribed_to_journal,
            # access info
            access_type=self.get_access_type(),
            content_access_granted=self.content_access_granted,
            is_issue_embargoed=issue.embargoed,
            is_journal_open_access=journal.open_access,
            # user info
            session_key=session_key,
            username=username or "",
        )

        logger.info("article_access", json=json.loads(article_access_log.json()))

        return response

    def get_access_type(self) -> ArticleAccessType:
        raise NotImplementedError
