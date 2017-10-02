# -*- coding: utf-8*-

import datetime as dt
import ipaddress
from functools import reduce

from django.conf import settings
from django.db import models
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError

from account_actions.models import AccountActionToken

from erudit.models import Collection
from erudit.models import Journal
from erudit.models import Organisation

from .abstract_models import AbstractSubscription
from .abstract_models import AbstractSubscriptionPeriod
from .managers import JournalAccessSubscriptionValidManager


class UserSubscriptions(object):
    """ Helper model that aggregates the subscriptions of a user """

    def __init__(self):
        self._subscriptions = []
        self.active_subscription = None

        """ The active subscriptions for this session. """

    def add_subscription(self, subscription):
        """ Adds a subscription to the users subscriptions

        The order in which the subscriptions are added is the order in which
        the subscription will be verified.

        The first subscription to be added will be the active subscription.
        """
        if not self.active_subscription:
            self.active_subscription = subscription
        self._subscriptions.append(subscription)

    def set_active_subscription_for(self, article=None, issue=None, journal=None):
        """ Sets the active subscription for a given content

        Finds the first subscription that provides access to the specified content
        and sets it as the "active" subscription.
        """
        for subscription in self._subscriptions:
            if subscription.provides_access_to(article=article, issue=issue, journal=journal):
                self.active_subscription = subscription
                return

    def provides_access_to(self, article=None, issue=None, journal=None):
        """ Determines if this set of subscriptions provides access to a given content

        Subscriptions are tested in the order in which they were added.

        :returns: True if it provides access content
        """
        if not any((article, issue, journal,)):
            raise ValueError("One of article, issue, journal must be specified.")
        for subscription in self._subscriptions:
            if subscription.provides_access_to(article=article, issue=issue, journal=journal):
                return True
        return False


class JournalAccessSubscription(AbstractSubscription):
    """ Defines a subscription allowing a user or an organisation to access journals.

    The subscription can associate many Journal instances to the user or the organisation.
    A subscription for collection of journals or a "full access" subscription can also be specified.
    """
    # The subscription can be associated either with a user or an organisation.
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, verbose_name=_('Abonné individuel'), blank=True, null=True)
    """ User associated to the subscription"""

    organisation = models.ForeignKey(
        Organisation, verbose_name=_('Abonné institutionnel'), blank=True, null=True)
    """ Organisation associated to the subscription """

    journal_management_subscription = models.ForeignKey(
        "JournalManagementSubscription", verbose_name=_('Forfait'), blank=True, null=True,
        related_name="subscriptions",
    )
    """ JournalManagementSubscription towards which the subscription will count """

    # Which Journal instances can be accessed using this subscription?
    journal = models.ForeignKey(
        Journal, verbose_name=_('Revue'), blank=True, null=True, related_name='+')
    collection = models.ForeignKey(
        Collection, verbose_name=_('Collection'), blank=True, null=True, related_name='+')
    journals = models.ManyToManyField(
        Journal, verbose_name=_('Revues'), related_name='+', blank=True)

    # The subscription can be sponsored by a specific organisation
    sponsor = models.ForeignKey(
        Organisation, verbose_name=_('Commanditaire'), blank=True, null=True,
        related_name='sponsored_subscriptions')

    objects = models.Manager()
    valid_objects = JournalAccessSubscriptionValidManager()

    class Meta:
        verbose_name = _('Abonnement aux revues')
        verbose_name_plural = _('Abonnements aux revues')

    def __str__(self):
        dest = self.user if self.user else self.organisation
        if self.journal_id:
            return '{} - {}'.format(dest, self.journal)
        elif self.collection_id:
            return '{} - {}'.format(dest, self.collection)
        return _('{} - Accès multiples').format(dest)

    @cached_property
    def is_ongoing(self):
        """ Returns a boolean indicating if the subscription is ongoing or not. """
        nowd = dt.datetime.now().date()
        return JournalAccessSubscriptionPeriod.objects.filter(
            subscription=self, start__lte=nowd, end__gte=nowd).exists()

    def provides_access_to(self, article=None, issue=None, journal=None):
        """ Returns if the subscription has access to the given article, issue
         or journal"""
        # FIXME check the journals of the collection

        if not any((article, issue, journal,)):
            raise ValueError("One of article, issue, journal must be specified.")

        if article:
            journal = article.issue.journal
        elif issue:
            journal = issue.journal

        if self.journal == journal:
            return True

        if journal in self.journals.all():
            return True
        return False

    def get_journals(self):
        """ Returns the Journal instances targetted by the subscription. """

        journal_ids = []
        if self.journal_id:
            journal_ids.append(self.journal_id)
        if self.collection:
            journal_ids.extend(list(Journal.objects.values_list('id', flat=True)))
        journal_ids.extend(list(self.journals.all().values_list('id', flat=True)))
        return Journal.objects.filter(id__in=journal_ids)


class JournalAccessSubscriptionPeriod(AbstractSubscriptionPeriod):
    """ Defines a period in which a user or an organisation is allowed to access journals. """
    subscription = models.ForeignKey(JournalAccessSubscription, verbose_name=_('Abonnement'))

    class Meta:
        verbose_name = _("Période d'abonnement aux revues")
        verbose_name_plural = _("Périodes d'abonnement aux revues")


class InstitutionReferer(models.Model):
    subscription = models.ForeignKey(
        JournalAccessSubscription, verbose_name=_("Abonnement aux revues"), related_name='referers'
    )
    referer = models.URLField(verbose_name=_("URL référent"))


class InstitutionIPAddressRange(models.Model):
    subscription = models.ForeignKey(
        JournalAccessSubscription, verbose_name=_('Abonnement aux revues'))
    ip_start = models.GenericIPAddressField(verbose_name=_('Adresse IP de début'))
    ip_end = models.GenericIPAddressField(verbose_name=_('Adresse IP de fin'))

    class Meta:
        verbose_name = _('Plage d\'adresses IP d\'institution')
        verbose_name_plural = _('Plages d\'adresses IP d\'institution')

    def __str__(self):
        return '{institution} / {start} - {end}'.format(
            institution=self.subscription, start=self.ip_start, end=self.ip_end)

    def clean(self):
        super(InstitutionIPAddressRange, self).clean()
        try:
            start = ipaddress.ip_address(self.ip_start)
        except ValueError:
            raise ValidationError(_(
                '{0} n\'est pas une adresse IP valide').format(self.ip_start))
        try:
            end = ipaddress.ip_address(self.ip_end)
        except ValueError:
            raise ValidationError(_(
                '{0} n\'est pas une adresse IP valide').format(self.ip_end))
        if start > end:
            raise ValidationError(_(
                'L\'adresse IP de début doit être inférieure à l\'adresse IP de fin'))

    @property
    def ip_addresses(self):
        """ Returns the list of IP addresses contained in the current range. """
        start = ipaddress.ip_address(self.ip_start)
        end = ipaddress.ip_address(self.ip_end)
        return reduce(
            lambda ips, ipn: ips + list(ipn),
            ipaddress.summarize_address_range(start, end), [])


class JournalManagementSubscription(AbstractSubscription):
    """ Defines a subscription allowing the members of a journal to manage its subscriptions. """
    journal = models.ForeignKey(Journal, verbose_name=_('Revue'))
    plan = models.ForeignKey('JournalManagementPlan', verbose_name=_('Forfait'))

    class Meta:
        verbose_name = _("Abonnement aux forfaits d'abonnements individuels")
        verbose_name_plural = _("Abonnements aux forfaits d'abonnements individuels")
        ordering = ['journal__name']

    @cached_property
    def is_ongoing(self):
        """ Returns a boolean indicating if the subscription is ongoing or not. """
        nowd = dt.datetime.now().date()
        return JournalManagementSubscriptionPeriod.objects.filter(
            subscription=self, start__lte=nowd, end__gte=nowd).exists()

    def get_pending_subscriptions(self):
        return AccountActionToken.pending_objects.get_for_object(self)

    @property
    def is_full(self):
        """ :returns: True if this JournalManagementSubscription is full """
        if self.plan.is_unlimited:
            return False
        return self.subscriptions.count() + \
            self.get_pending_subscriptions().count() >= self.plan.max_accounts

    def __str__(self):
        return "{} / {}".format(self.journal, self.plan)


class JournalManagementPlan(models.Model):
    """ Defines the limits of the possibilities provided by a journal management subscription. """
    title = models.CharField(max_length=255, verbose_name=_('Titre'), blank=True, null=True)
    code = models.SlugField(max_length=100, unique=True, verbose_name=_('Code'))
    max_accounts = models.PositiveSmallIntegerField(
        verbose_name=_('Nombre de comptes'),
        help_text=_("Nombre maximal de comptes que ce forfait permet d'abonner")
    )
    is_unlimited = models.BooleanField(
        default=False,
        verbose_name=_('Illimité'),
        help_text=_("Cocher si ce forfait d'abonnements individuels permet d'abonner un nombre illimité d'individus")  # noqa
    )

    class Meta:
        verbose_name = _("Forfait d'abonnements individuels")
        verbose_name_plural = _("Forfaits d'abonnements individuels")

    def __str__(self):
        return self.code if not self.title else self.title


class JournalManagementSubscriptionPeriod(AbstractSubscriptionPeriod):
    """ Defines a period in which the member of a journal is allowed to manage subscriptions. """
    subscription = models.ForeignKey(JournalManagementSubscription, verbose_name=_('Abonnement'))

    class Meta:
        verbose_name = _("Période d'abonnement de aux forfaits d'abonnements individuels")
        verbose_name_plural = _("Périodes d'abonnement aux forfaits d'abonnements individuels")
