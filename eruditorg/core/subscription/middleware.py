# -*- coding: utf-8 -*-

import logging
from ipware.ip import get_ip

from .models import JournalAccessSubscription
from core.subscription.models import UserSubscriptions
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)


class SubscriptionMiddleware(MiddlewareMixin):
    """ This middleware attaches subscription information to the request object.

    This middleware attaches informations related to the subscription
    of the current user to the request object.
    """

    def _get_user_referer_for_subscription(self, request):
        """ Return the referer of the user, with regards to subscription validation

        If the user has a referer set in her session, return this referer. Otherwise
        return the value of 'HTTP_REFERER'
        """
        referer = request.COOKIES.get('HTTP_REFERER') or request.session.get('HTTP_REFERER')
        return referer if referer else request.META.get('HTTP_REFERER')

    def _get_user_ip_address(self, request):
        if request.user.is_active and request.user.is_staff and 'HTTP_CLIENT_IP' in request.META:
            return request.META.get('HTTP_CLIENT_IP', None)
        return get_ip(request, right_most_proxy=True)

    def process_request(self, request):
        # Tries to determine if the user's IP address is contained into
        # an institutional IP address range.

        ip = self._get_user_ip_address(request)
        if request.user.is_active and request.user.is_staff:
            ip = request.META.get('HTTP_CLIENT_IP', ip)

        request.subscriptions = UserSubscriptions()
        subscription = JournalAccessSubscription.valid_objects.get_for_ip_address(ip).first()
        if subscription:
            request.subscriptions.add_subscription(subscription)

        # Tries to determine if the subscriber is refered by a subscribed organisation
        referer = self._get_user_referer_for_subscription(request)
        subscription = JournalAccessSubscription.valid_objects.get_for_referer(referer)
        if subscription:
            request.subscriptions.add_subscription(subscription)
            request.session['HTTP_REFERER'] = referer

        # Tries to determine if the user has an individual account
        if request.user.is_authenticated:
            for subscription in JournalAccessSubscription.valid_objects.select_related(
                'sponsor'
            ).filter(user=request.user):
                request.subscriptions.add_subscription(subscription)

    def process_response(self, request, response):
        active_subscription = request.subscriptions.active_subscription

        referer = self._get_user_referer_for_subscription(request)

        if active_subscription and active_subscription.referers.filter(referer=referer):
            referer = active_subscription.referers.first()
            logger.info('{url} {method} {path} {protocol} - {client_port} - {client_ip} "{user_agent}" "{referer_url}" {code} {size} {referer_access}'.format(  # noqa
                url=request.get_raw_uri(),
                method=request.META.get('REQUEST_METHOD'),
                path=request.path,
                protocol=request.META.get('SERVER_PROTOCOL'),
                client_port="",
                client_ip=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT'),
                referer_url=request.META.get('HTTP_REFERER'),
                code=response.status_code,
                size="",
                referer_access=referer.referer
            ))

        return response
