# -*- coding: utf-8 -*-

from ipware.ip import get_ip

from .models import JournalAccessSubscription


class SubscriptionMiddleware(object):
    """ This middleware attaches subscription information to the request object.

    This middleware attaches informations related to the subscription
    of the current user to the request object. It attaches a ``subscription_type``
    attribute to the request. This attribute can have three values: 'institution',
    'individual' or 'open_access'.
    """

    def _get_user_referer_for_subscription(self, request):
        """ Return the referer of the user, with regards to subscription validation

        If the user has a referer set in her session, return this referer. Otherwise
        return the value of 'HTTP_REFERER'
        """
        referer = request.session.get('HTTP_REFERER')
        return referer if referer else request.META.get('HTTP_REFERER')

    def _get_user_ip_address(self, request):
        if request.user.is_active and request.user.is_staff and 'HTTP_CLIENT_IP' in request.META:
            return request.META.get('HTTP_CLIENT_IP', None)
        return get_ip(request)

    def process_request(self, request):
        # Tries to determine if the user's IP address is contained into
        # an institutional IP address range.
        ip = self._get_user_ip_address(request)
        if request.user.is_active and request.user.is_staff:
            ip = request.META.get('HTTP_CLIENT_IP', ip)

        subscription = JournalAccessSubscription.valid_objects.get_for_ip_address(ip).first()
        if subscription:
            request.subscription = subscription
            request.subscription_type = 'institution'
            return

        # Tries to determine if the subscriber is refered by a subscribed organisation
        referer = self._get_user_referer_for_subscription(request)
        subscription = JournalAccessSubscription.valid_objects.get_for_referer(referer)
        if subscription:
            request.subscription = subscription
            request.subscription_type = 'institution-referer'
            request.session['HTTP_REFERER'] = referer
            return

        # Tries to determine if the user has an individual account
        subscription = JournalAccessSubscription.valid_objects.select_related('sponsor') \
            .filter(user=request.user).first() if request.user.is_authenticated() else False
        if subscription:
            request.subscription = subscription
            request.subscription_type = 'individual'
            return

        # In any other the user is is in open access.
        request.subscription = None
        request.subscription_type = 'open_access'
