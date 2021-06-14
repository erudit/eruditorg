# -*- coding: utf-8 -*-

import structlog
import re
import ipaddress

from urllib.parse import urlparse

from django.db import models
from django.db.models import Q

logger = structlog.getLogger(__name__)


class JournalAccessSubscriptionQueryset(models.QuerySet):
    def get_for_ip_address(self, ip_address):
        """ Return all the subscriptions for the given ip address """
        ip_int = int(ipaddress.ip_address(ip_address))

        return self.filter(
            institutionipaddressrange__ip_start_int__lte=ip_int,
            institutionipaddressrange__ip_end_int__gte=ip_int,
        ).distinct()

    def get_for_referer(self, referer):
        """ Return all the subscriptions for the given referer """
        if not referer:
            return

        parsed_user_referer = urlparse(referer)

        if parsed_user_referer.netloc == "":
            return

        user_netloc = re.sub("^www.", "", parsed_user_referer.netloc)

        referer_subscription = self.filter(referer__contains=user_netloc).first()

        if referer_subscription:
            parsed_institution_referer = urlparse(referer_subscription.referer)

            institution_netloc = re.sub("^www.", "", parsed_institution_referer.netloc)

            if (
                # Compare full netloc
                institution_netloc == user_netloc
                and parsed_institution_referer.path in parsed_user_referer.path
            ):
                return referer_subscription


class JournalAccessSubscriptionValidManager(models.Manager):
    def get_queryset(self):
        """ Returns all the valid JournalAccessSubscription instances. """
        return self.institutional() | self.individual()

    def institutional(self):
        """Returns all the valid institutional JournalAccessSubscription instances."""
        institutional = Q(organisation__isnull=True) | Q(journals__isnull=True)
        qs = JournalAccessSubscriptionQueryset(self.model, using=self._db)
        return qs.exclude(institutional).prefetch_related("journals")

    def individual(self):
        """Returns all the valid individual JournalAccessSubscription instances.

        To be valid, an individual subscription needs a valid JournalManagementSubscriptionPeriod.
        That's because we let the journal manage validity themselves."""
        individual = Q(
            organisation__isnull=True,
        )
        qs = JournalAccessSubscriptionQueryset(self.model, using=self._db)
        return qs.filter(individual).prefetch_related("journals")

    def get_for_ip_address(self, ip_address):
        """ Return all the subscriptions for the given ip address """
        return self.get_queryset().get_for_ip_address(ip_address)

    def get_for_referer(self, referer):
        return self.get_queryset().get_for_referer(referer)
