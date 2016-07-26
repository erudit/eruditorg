# -*- coding: utf-8 -*-

from ipware.ip import get_ip

from .models import InstitutionIPAddressRange
from .models import JournalAccessSubscription


class SubscriptionMiddleware(object):
    """ This middleware attaches subscription information to the request object.

    This middleware attaches informations related to the subscription
    of the current user to the request object. It attaches a ``subscription_type``
    attribute to the request. This attribute can have three values: 'institution',
    'individual' or 'open_access'.
    """
    def process_request(self, request):
        # Tries to determine if the user's IP address is contained into
        # an institutional IP address range.
        ip = get_ip(request)
        ip_range_subscription_ids = InstitutionIPAddressRange.objects \
            .select_related('subscription', 'subscription__organisation', 'subscription__sponsor') \
            .filter(ip_start__lte=ip, ip_end__gte=ip).values_list('id', flat=True)
        subscription = JournalAccessSubscription.valid_objects \
            .filter(id__in=ip_range_subscription_ids).first() if ip_range_subscription_ids \
            else False
        if subscription:
            request.subscription = subscription
            request.subscription_type = 'institution'
            return

        # Tries to determine if the user has an individual account
        subscription = JournalAccessSubscription.valid_objects.select_related('sponsor') \
            .filter(user=request.user).first() if request.user.is_authenticated() else False
        if subscription:
            request.subscription = subscription
            request.subscription_type = 'individual'
            return

        # In any other the user is is in open access.
        request.subscription_type = 'open_access'
