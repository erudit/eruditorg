# -*- coding: utf-8*-

import datetime as dt
import ipaddress
from functools import reduce

import structlog
from django.conf import settings
from django.db import models
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

from account_actions.models import AccountActionToken

from erudit.models import Journal
from erudit.models import Organisation

from .abstract_models import AbstractSubscription
from .abstract_models import AbstractSubscriptionPeriod
from .managers import JournalAccessSubscriptionValidManager

logger = structlog.get_logger(__name__)


class UserSubscriptions:
    """ Helper model that aggregates the subscriptions of a user """

    def __init__(self):
        self._subscriptions = []
        self.active_subscription = None

        """ The active subscriptions for this session. """

    def add_subscription(self, subscription):
        """Adds a subscription to the users subscriptions

        The order in which the subscriptions are added is the order in which
        the subscription will be verified.

        The first subscription to be added will be the active subscription.
        """
        if not self.active_subscription:
            self.active_subscription = subscription
        self._subscriptions.append(subscription)

    def set_active_subscription_for(self, article=None, issue=None, journal=None):
        """Sets the active subscription for a given content

        Finds the first subscription that provides access to the specified content
        and sets it as the "active" subscription.
        """
        for subscription in self._subscriptions:
            if subscription.provides_access_to(article=article, issue=issue, journal=journal):
                self.active_subscription = subscription
                return

    def provides_access_to(self, article=None, issue=None, journal=None):
        """Determines if this set of subscriptions provides access to a given content

        Subscriptions are tested in the order in which they were added.

        :returns: True if it provides access content
        """
        if not any(
            (
                article,
                issue,
                journal,
            )
        ):
            raise ValueError("One of article, issue, journal must be specified.")
        for subscription in self._subscriptions:
            if subscription.provides_access_to(article=article, issue=issue, journal=journal):
                return True
        return False


class AccessBasket(models.Model):
    """A group of journal that we can subscribe someone all at once.

    Sometimes we have sub subscribe many individual users to the same group of journal as part of
    initiatives external to the journal itself (a group subscription plan). This is what this model
    represents.

    Subscribing to an AccessBasket does **not** count towards a journal's plan limit.
    """

    name = models.TextField(verbose_name=_("Nom"))
    journals = models.ManyToManyField(Journal, verbose_name=_("Revues"), related_name="+")

    class Meta:
        verbose_name = _("Panier de revues")
        verbose_name_plural = _("Paniers de revues")

    def __str__(self):
        return self.name


class JournalAccessSubscription(AbstractSubscription):
    """Defines a subscription allowing a user or an organisation to access journals.

    The subscription can associate many Journal instances to the user or the organisation.
    """

    TYPE_INSTITUTIONAL = "institutional"
    TYPE_INDIVIDUAL = "individual"
    TYPE_UNKNOWN = "unknown"

    # The subscription can be associated either with a user or an organisation.
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("Abonné individuel"),
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )
    """ User associated to the subscription"""

    organisation = models.ForeignKey(
        Organisation,
        verbose_name=_("Abonné institutionnel"),
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )
    """ Organisation associated to the subscription """

    journal_management_subscription = models.ForeignKey(
        "JournalManagementSubscription",
        verbose_name=_("Forfait"),
        blank=True,
        null=True,
        related_name="subscriptions",
        on_delete=models.CASCADE,
    )
    """ JournalManagementSubscription towards which the subscription will count """

    # Which Journal instances can be accessed using this subscription?
    journals = models.ManyToManyField(
        Journal, verbose_name=_("Revues"), related_name="+", blank=True
    )
    basket = models.ForeignKey(
        AccessBasket,
        verbose_name=_("Panier"),
        blank=True,
        null=True,
        related_name="accesses",
        on_delete=models.CASCADE,
    )

    # The subscription can be sponsored by a specific organisation
    sponsor = models.ForeignKey(
        Organisation,
        verbose_name=_("Commanditaire"),
        blank=True,
        null=True,
        related_name="sponsored_subscriptions",
        on_delete=models.CASCADE,
    )

    # Referer
    referer = models.URLField(verbose_name=_("URL référent"), null=True, blank=True)

    objects = models.Manager()
    valid_objects = JournalAccessSubscriptionValidManager()

    class Meta:
        verbose_name = _("Abonnement aux revues")
        verbose_name_plural = _("Abonnements aux revues")

    def __str__(self):
        dest = self.user if self.user else self.organisation
        return _("{} - Accès multiples").format(dest)

    @cached_property
    def is_ongoing(self):
        """ Returns a boolean indicating if the subscription is ongoing or not. """
        nowd = dt.datetime.now().date()
        return JournalAccessSubscriptionPeriod.objects.filter(
            subscription=self, start__lte=nowd, end__gte=nowd
        ).exists()

    def get_subscription_type(self):
        if self.organisation is not None:
            return JournalAccessSubscription.TYPE_INSTITUTIONAL
        if self.user is not None:
            return JournalAccessSubscription.TYPE_INDIVIDUAL

        logger.warning(
            "unknown.subscription", pk=self.pk, message="no user and no organisation specified"
        )

        return JournalAccessSubscription.TYPE_UNKNOWN

    def provides_access_to(self, article=None, issue=None, journal=None):
        """Returns if the subscription has access to the given article, issue
        or journal"""

        if not any(
            (
                article,
                issue,
                journal,
            )
        ):
            raise ValueError("One of article, issue, journal must be specified.")

        if article:
            journal = article.issue.journal
        elif issue:
            journal = issue.journal

        if journal in self.journals.all():
            return True

        if self.basket and journal in self.basket.journals.all():
            return True

        return False

    def get_journals(self):
        """ Returns the Journal instances targeted by the subscription. """
        journals = self.journals.all()
        if self.basket_id:
            journals |= self.basket.journals.all()
        return journals.distinct().order_by("name")


class JournalAccessSubscriptionPeriod(AbstractSubscriptionPeriod):
    """ Defines a period in which a user or an organisation is allowed to access journals. """

    subscription = models.ForeignKey(
        JournalAccessSubscription, verbose_name=_("Abonnement"), on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = _("Période d’abonnement aux revues")
        verbose_name_plural = _("Périodes d’abonnement aux revues")


class InstitutionIPAddressRange(models.Model):
    subscription = models.ForeignKey(
        JournalAccessSubscription, verbose_name=_("Abonnement aux revues"), on_delete=models.CASCADE
    )
    ip_start = models.GenericIPAddressField(verbose_name=_("Adresse IP de début"))
    ip_start_int = models.BigIntegerField(db_index=True, verbose_name=_("Adresse IP de début"))
    ip_end = models.GenericIPAddressField(verbose_name=_("Adresse IP de fin"))
    ip_end_int = models.BigIntegerField(db_index=True, verbose_name=_("Adresse IP de fin"))

    class Meta:
        verbose_name = _("Plage d’adresses IP d’institution")
        verbose_name_plural = _("Plages d’adresses IP d’institution")

    def __str__(self):
        return "{institution} / {start} - {end}".format(
            institution=self.subscription, start=self.ip_start, end=self.ip_end
        )

    def clean(self):
        super(InstitutionIPAddressRange, self).clean()
        try:
            start = ipaddress.ip_address(self.ip_start)
        except ValueError:
            raise ValidationError(_("{0} n’est pas une adresse IP valide").format(self.ip_start))
        try:
            end = ipaddress.ip_address(self.ip_end)
        except ValueError:
            raise ValidationError(_("{0} n’est pas une adresse IP valide").format(self.ip_end))
        if start > end:
            raise ValidationError(
                _("L’adresse IP de début doit être inférieure à l’adresse IP de fin")
            )

    def save(self, *args, **kwargs):
        self.ip_start_int = int(ipaddress.ip_address(self.ip_start))
        self.ip_end_int = int(ipaddress.ip_address(self.ip_end))
        return super().save(*args, **kwargs)

    @property
    def ip_addresses(self):
        """ Returns the list of IP addresses contained in the current range. """
        start = ipaddress.ip_address(self.ip_start)
        end = ipaddress.ip_address(self.ip_end)
        return reduce(
            lambda ips, ipn: ips + list(ipn), ipaddress.summarize_address_range(start, end), []
        )


class JournalManagementSubscription(AbstractSubscription):
    """ Defines a subscription allowing the members of a journal to manage its subscriptions. """

    journal = models.ForeignKey(Journal, verbose_name=_("Revue"), on_delete=models.CASCADE)
    plan = models.ForeignKey(
        "JournalManagementPlan", verbose_name=_("Forfait"), on_delete=models.CASCADE
    )

    class Meta:
        verbose_name = _("Abonnement aux forfaits d'abonnements individuels")
        verbose_name_plural = _("Abonnements aux forfaits d'abonnements individuels")
        ordering = ["journal__name"]

    @cached_property
    def is_ongoing(self):
        """ Returns a boolean indicating if the subscription is ongoing or not. """
        nowd = dt.datetime.now().date()
        return JournalManagementSubscriptionPeriod.objects.filter(
            subscription=self, start__lte=nowd, end__gte=nowd
        ).exists()

    def subscribe_email(self, email, first_name=None, last_name=None):
        """Create a JournalAccessSubscription for the given email

        Subscribe an email to the journal related to this
        management subscription.

        If a user account with the target email exists, it will be subscribed. Otherwise,
        it will be created and subscribed.

        :param email: the email to subscribe
        :param first_name: first name of the user. Only used if the user is created.
        :param last_name: last name of the user. Only used if the user is created.
        """

        user, created = get_user_model().objects.get_or_create(
            email=email,
            defaults={
                "username": email,
                "first_name": first_name or "",
                "last_name": last_name or "",
            },
        )

        if created:
            logger.info("user.created", user=user.username)

        subscription, created = JournalAccessSubscription.objects.get_or_create(
            journal_management_subscription=self, user=user
        )

        if created:
            subscription.journals.add(self.journal)
            logger.info(
                "subscription.created", user=user.username, journal=self.journal.code, plan=self.pk
            )

    def get_pending_subscriptions(self):
        return AccountActionToken.pending_objects.get_for_object(self)

    def email_exists_or_is_pending(self, email):
        from .account_actions import IndividualSubscriptionAction

        exists = JournalAccessSubscription.objects.filter(
            journal_management_subscription=self,
            user__email=email,
        ).exists()
        pending = (
            AccountActionToken.pending_objects.get_for_object(self)
            .filter(action=IndividualSubscriptionAction.name, email=email)
            .exists()
        )
        return exists or pending

    @property
    def slots_left(self):
        if self.plan.is_unlimited:
            return 10 ** 5
        count = self.subscriptions.count()
        pending = self.get_pending_subscriptions().count()
        slots = self.plan.max_accounts
        return max(0, slots - count - pending)

    @property
    def is_full(self):
        """ :returns: True if this JournalManagementSubscription is full """
        return self.slots_left <= 0

    def __str__(self):
        return "{} / {}".format(self.journal, self.plan)


class JournalManagementPlan(models.Model):
    """ Defines the limits of the possibilities provided by a journal management subscription. """

    title = models.CharField(max_length=255, verbose_name=_("Titre"), blank=True, null=True)
    code = models.SlugField(max_length=100, unique=True, verbose_name=_("Code"))
    max_accounts = models.PositiveSmallIntegerField(
        verbose_name=_("Nombre de comptes"),
        help_text=_("Nombre maximal de comptes que ce forfait permet d’abonner"),
    )
    is_unlimited = models.BooleanField(
        default=False,
        verbose_name=_("Illimité"),
        help_text=_(
            "Cocher si ce forfait d’abonnements individuels permet d’abonner un nombre illimité d’individus"  # noqa
        ),
    )

    class Meta:
        verbose_name = _("Forfait d’abonnements individuels")
        verbose_name_plural = _("Forfaits d’abonnements individuels")

    def __str__(self):
        return self.code if not self.title else self.title


class JournalManagementSubscriptionPeriod(AbstractSubscriptionPeriod):
    """ Defines a period in which the member of a journal is allowed to manage subscriptions. """

    subscription = models.ForeignKey(
        JournalManagementSubscription,
        related_name="period",
        verbose_name=_("Abonnement"),
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = _("Période d’abonnement aux forfaits d’abonnements individuels")
        verbose_name_plural = _("Périodes d’abonnement aux forfaits d’abonnements individuels")
