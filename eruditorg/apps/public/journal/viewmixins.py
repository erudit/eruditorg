import redis

from base64 import urlsafe_b64decode
from binascii import unhexlify
from Crypto.Cipher import AES
from datetime import datetime
from ipaddress import ip_address, ip_network
from ipware import get_client_ip
from urllib.parse import unquote

from django.conf import settings
from django.db.models import Q
from django.urls import reverse
from django.http import Http404
from django.http.response import HttpResponseRedirect
from django.utils.functional import cached_property

from erudit.models import Article
from erudit.models import Issue
from erudit.models import Journal
from erudit.solr.models import get_fedora_ids

from core.metrics.metric import metric


class RedirectExceptionsToFallbackWebsiteMixin:
    """ Mixin that redirects all exceptions to the fallback website """
    def dispatch(self, request, *args, **kwargs):
        try:
            return super().dispatch(request, *args, **kwargs)
        except Http404:
            return HttpResponseRedirect(
                settings.FALLBACK_BASE_URL + self.request.path.strip('/')
            )


class SingleJournalMixin:
    """ Simply allows retrieving a Journal instance using its code or localidentifier. """

    def get_journal_queryset(self):
        return Journal.internal_objects.select_related('previous_journal', 'next_journal')

    def get_journal(self):
        try:
            return self.get_journal_queryset().get(
                Q(code=self.kwargs['code']) | Q(localidentifier=self.kwargs['code']))
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
        """ Returns the considered content.

        By default the method will try to fetch the content using the ``object`` attribute. If this
        attribute is not available the
        :meth:`get_object<django:django.views.generic.detail.SingleObjectMixin.get_object>` method
        will be used. But subclasses can override this to control the way the content is retrieved.
        """
        return self.object if hasattr(self, 'object') else self.get_object()

    def _get_subscriptions_kwargs_for_content(self):
        content = self.get_content()
        kwargs = {}
        if isinstance(content, Article):
            # 1- Is the article in open access? Is the article subject to a movable limitation?
            kwargs['article'] = content
        elif isinstance(content, Issue):
            kwargs['issue'] = content
        elif isinstance(content, Journal):
            kwargs['journal'] = content
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
        context['content_access_granted'] = self.content_access_granted

        active_subscription = self.request.subscriptions.active_subscription
        if active_subscription:
            context['subscription_type'] = active_subscription.get_subscription_type()
        return context

    @cached_property
    def content_access_granted(self):
        """ Returns a boolean indicating if the content can be accessed.

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
                return issue.is_prepublication_ticket_valid(self.request.GET.get('ticket'))

        # Otherwise, check if the user has a valid subscription that provides access to the article.
        kwargs = self._get_subscriptions_kwargs_for_content()
        return self.request.subscriptions.provides_access_to(**kwargs)


class SingleArticleMixin:

    def __init__(self):
        self.object = None

    def get_object(self, queryset=None):
        # We support two IDing scheme here: full PID or localidentifier-only. If we have the full
        # PID, great! that saves us a request to Solr. If not, it's alright too, we just need to
        # fetch the full PID from Solr first.
        if self.object is not None:
            return self.object
        journal_code = self.kwargs.get('journal_code')
        issue_localid = self.kwargs.get('issue_localid')
        localidentifier = self.kwargs.get('localid')
        if not (journal_code and issue_localid):
            fedora_ids = get_fedora_ids(localidentifier)
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
        context['citation_title_metadata'] = article.title
        context['citation_journal_title_metadata'] = article.get_erudit_object()\
            .get_formatted_journal_title()
        context['citation_references'] = article.get_erudit_object()\
            .get_references(html=False)
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

        if not issue.is_published and \
                not issue.is_prepublication_ticket_valid(request.GET.get('ticket')):
            return HttpResponseRedirect(
                reverse('public:journal:journal_detail', args=(issue.journal.code, ))
            )

        return super().get(request, *args, **kwargs)


class ArticleViewMetricCaptureMixin:
    tracking_article_view_granted_metric_name = 'erudit__journal__article_view'
    tracking_view_type = 'html'

    def dispatch(self, request, *args, **kwargs):
        self.request = request
        response = super(ArticleViewMetricCaptureMixin, self).dispatch(request, *args, **kwargs)
        if response.status_code == 200 and self.content_access_granted:
            # We register this metric only if the article can be viewed
            metric(
                self.tracking_article_view_granted_metric_name,
                tags=self.get_metric_tags(), **self.get_metric_fields())
        return response

    def get_metric_fields(self):
        article = self.get_content()
        subscription = self.request.subscriptions.active_subscription
        return {
            'issue_localidentifier': article.issue.localidentifier,
            'localidentifier': article.localidentifier,
            'subscription_id': subscription.id if subscription else None,
        }

    def get_metric_tags(self):
        article = self.get_content()
        return {
            'journal_localidentifier': article.issue.journal.localidentifier,
            'open_access': article.open_access or not article.embargoed,
            'view_type': self.get_tracking_view_type(),
        }

    def get_tracking_view_type(self):
        return self.tracking_view_type


class GoogleCasaAuthorizationMixin:

    def get_context_data(self, **kwargs: dict) -> dict:
        """ Google CASA authorization for ArticleDetailView. """
        context = super(GoogleCasaAuthorizationMixin, self).get_context_data(**kwargs)
        casa_key = getattr(settings, 'GOOGLE_CASA_KEY', None)
        casa_token = self.request.GET.get('casa_token')
        user_ip, _ = get_client_ip(self.request)
        if casa_key and casa_token and user_ip:
            context['content_access_granted'] |= self.casa_authorize(casa_key, casa_token, user_ip)
        return context

    def has_permission(self) -> bool:
        """ Google CASA authorization for ArticleRawPdfView. """
        has_permission = super(GoogleCasaAuthorizationMixin, self).has_permission()
        casa_key = getattr(settings, 'GOOGLE_CASA_KEY', None)
        casa_token = self.request.GET.get('casa_token')
        user_ip, _ = get_client_ip(self.request)
        if casa_key and casa_token and user_ip:
            has_permission |= self.casa_authorize(casa_key, casa_token, user_ip)
        return has_permission

    def casa_authorize(self, key: str, token: str, user_ip: str) -> bool:
        """
        Check if the user is authorized to see the full text article.

        :param key: the encryption key
        :param token: the CASA token
        :param user_ip: the IP address of the user

        :returns: Whether the user is authorized to see the full text article.
        """
        # The key needs to be converted from the 32-byte hex-encoded form to a 16-byte binary string
        # before use.
        key = unhexlify(key)

        # The CASA token consists of two components separated by a colon:
        # * A 12-byte unique random number (nonce).
        # * A variable length payload which includes a 16-byte signature.
        components = token.split(':')
        if len(components) != 2:
            # Badly formed token.
            return False

        # The CASA token components are encoded using Base-64 encoding suitable for URLs. They need
        # to be decoded before use. Since the payload is of variable length, it needs some padding.
        nonce = urlsafe_b64decode(components[0])
        payload = urlsafe_b64decode(components[1] + '=' * (4 - len(components[1]) % 4))

        # Decrypt and verify the payload.
        try:
            cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
            # The payload includes a 16-byte signature at the end used for the verify.
            data = cipher.decrypt_and_verify(payload[:-16], payload[-16:])
        except ValueError:
            # Either the message has been modified or it didn’t come from Google Scholar.
            return False

        # Allow up to three times to handle user clicking on a search result a few times
        # (e.g., comparing figures in a few papers etc).
        if self.nonce_count(nonce) > 3:
            return False

        fields = data.decode().split(':')
        if len(fields) < 3:
            # Badly formatted token.
            return False

        # The timestamp in the token is the number of microseconds since Unix Epoch.
        timestamp = fields[0]
        if datetime.now().timestamp() * 1000000 - int(timestamp) > 60 * 60:
            # Token is too old and is no longer valid.
            return False

        # The ip_subnet field is URL-escaped in the token. It needs to be unescaped before use.
        ip_subnet = unquote(fields[2])
        if ip_address(user_ip) not in ip_network(ip_subnet):
            # User IP is outside the IP subnet the token is valid for.
            return False

        return True

    def nonce_count(self, nonce: str) -> int:
        """
        Check the nuber of times a nonce has been seen.

        :param nonce: the nonce

        :returns: The number of times the nonce has been seen.
        """
        try:
            # Try to store in Redis the number of times a particular nonce has been seen.
            redis_host = getattr(settings, 'REDIS_HOST')
            redis_port = getattr(settings, 'REDIS_PORT')
            redis_index = getattr(settings, 'REDIS_INDEX')
            if not redis_host or not redis_port or not redis_index:
                raise redis.exceptions.ConnectionError
            r = redis.Redis(host=redis_host, port=redis_port, db=redis_index)
            key = 'google_casa_nonce_{}'.format(nonce)
            count = r.get(key)
            count = int(count) + 1 if count is not None else 1
            r.set(key, count, 3600)
            return count
        except redis.exceptions.ConnectionError:
            # No access to Redis so we have no way to know how many times this nonce has been seen.
            return 0
