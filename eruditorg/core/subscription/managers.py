# -*- coding: utf-8 -*-

import structlog
import re

import datetime as dt
from urllib.parse import urlparse

from django.db import models
from django.conf import settings
from django.db.models import Q

logger = structlog.getLogger(__name__)


class JournalAccessSubscriptionQueryset(models.QuerySet):
    def get_for_ip_address(self, ip_address):
        """ Return all the subscriptions for the given ip address """
        from .models import InstitutionIPAddressRange
        database_engine = settings.DATABASES[self.db]['ENGINE']

        if 'mysql' in database_engine:
            ip_range = InstitutionIPAddressRange.objects.extra(
                where={
                    "inet_aton(ip_start) <= inet_aton('{}') AND inet_aton(ip_end) >= inet_aton('{}')".format(  # noqa
                        ip_address,
                        ip_address
                    )
                }
            )

            return self.filter(institutionipaddressrange__in=ip_range).distinct()

        if 'psycopg2' not in database_engine:
            logger.warning(
                "db.query",
                msg="Doing string comparison on IP addresses. The results may not be accurate."
            )

        return self.filter(
            institutionipaddressrange__ip_start__lte=ip_address,
            institutionipaddressrange__ip_end__gte=ip_address).distinct()

    def get_for_referer(self, referer):
        """ Return all the subscriptions for the given referer """
        from .models import InstitutionReferer

        if not referer:
            return

        parsed_user_referer = urlparse(referer)

        if parsed_user_referer.netloc == '':
            return

        user_netloc = re.sub('^www.', '', parsed_user_referer.netloc)

        referers_pk = self.filter(
            referers__referer__contains=user_netloc,
        ).values_list('referers', flat=True)

        for institution_referer in InstitutionReferer.objects.filter(pk__in=referers_pk):
            parsed_institution_referer = urlparse(institution_referer.referer)

            institution_netloc = re.sub('^www.', '', parsed_institution_referer.netloc)

            if (
                # Compare full netloc
                institution_netloc == user_netloc and
                parsed_institution_referer.path in parsed_user_referer.path
            ):
                return institution_referer.subscription


class JournalAccessSubscriptionValidManager(models.Manager):
    def get_queryset(self):
        """ Returns all the valid JournalAccessSubscription instances. """
        return self.institutional() | self.individual()

    def institutional(self):
        """ Returns all the valid institutional JournalAccessSubscription instances.

        To be valid, an institutional subscription needs a valid JournalAccessSubscriptionPeriod.
        """
        nowd = dt.datetime.now().date()
        institutional = Q(
            organisation__isnull=False,
            journalaccesssubscriptionperiod__start__lte=nowd,
            journalaccesssubscriptionperiod__end__gte=nowd)
        qs = JournalAccessSubscriptionQueryset(self.model, using=self._db)
        return qs.filter(institutional).prefetch_related('journals')

    def individual(self):
        """ Returns all the valid individual JournalAccessSubscription instances.

        To be valid, an individual subscription needs a valid JournalManagementSubscriptionPeriod.
        That's because we let the journal manage validity themselves. """
        nowd = dt.datetime.now().date()
        individual = Q(
            organisation__isnull=True,
            journal_management_subscription__period__start__lte=nowd,
            journal_management_subscription__period__end__gte=nowd)
        qs = JournalAccessSubscriptionQueryset(self.model, using=self._db)
        return qs.filter(individual).prefetch_related('journals')

    def get_for_ip_address(self, ip_address):
        """ Return all the subscriptions for the given ip address """
        return self.get_queryset().get_for_ip_address(ip_address)

    def get_for_referer(self, referer):
        return self.get_queryset().get_for_referer(referer)
