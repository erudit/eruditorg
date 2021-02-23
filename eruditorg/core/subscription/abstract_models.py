# -*- coding: utf-8 -*-

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _


class AbstractSubscription(models.Model):
    """ An abstract model that can be used to define a Subscription-like model. """

    created = models.DateTimeField(auto_now_add=True, verbose_name=_("Date de création"))
    updated = models.DateTimeField(auto_now=True, verbose_name=_("Date de modification"))

    class Meta:
        abstract = True


class AbstractSubscriptionPeriod(models.Model):
    """ Defines a period in which a subscription is valid. """

    start = models.DateField(verbose_name=_("Date de début"))
    end = models.DateField(verbose_name=_("Date de fin"))

    class Meta:
        abstract = True

    def __str__(self):
        return "[{start} - {end}]".format(start=self.start, end=self.end)

    def clean(self):
        super(AbstractSubscriptionPeriod, self).clean()

        # First we have to verify that the considered period is coherent.
        if self.start > self.end:
            raise ValidationError(
                _(
                    "La date de début d'une période d'abonnement ne doit pas être supérieure à la "
                    "date de fin."
                )
            )

        # Then we have to verify that there are no concurrent periods that could be in contention
        # with the considered period.
        concurrent_periods = (
            self.__class__._default_manager.filter(
                Q(start__lte=self.start, end__gte=self.end)
                | Q(start__gte=self.start, end__lte=self.end)  # Greater period
                | Q(start__lt=self.start, end__gt=self.start, end__lte=self.end)  # Smaller period
                | Q(  # Older period
                    start__gte=self.start, start__lt=self.end, end__gt=self.end
                )  # Younger period
            )
            .filter(**{self.subscription_field_name: getattr(self, self.subscription_field_name)})
            .exclude(pk=self.pk)
        )

        if concurrent_periods.exists():
            raise ValidationError(
                _("Cette période est en conflit avec une autre période pour cet abonnement.")
            )

    def get_subscription_field_name(self):
        """Returns the name of the foreign key to the subscription instance.

        This is the name of the foreign key that associates the model that inherits from the
        AbstractSubscriptionPeriod too a subclass of the AbstractSubscription abstract model.
        It defaults to ``subscription``.
        """
        return "subscription"

    @property
    def subscription_field_name(self):
        return self.get_subscription_field_name()
