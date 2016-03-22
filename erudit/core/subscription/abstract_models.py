# -*- coding: utf-8 -*-

import datetime as dt

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import ugettext_lazy as _


class AbstractSubscription(models.Model):
    """ An abstract model that can be used to define a Subscription-like model. """
    title = models.CharField(max_length=120, verbose_name=_('Titre'), blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True, verbose_name=_('Date de création'))
    updated = models.DateTimeField(auto_now=True, verbose_name=_('Date de modification'))
    date_activation = models.DateField(verbose_name=_("Date d'activation"), blank=True, null=True)
    date_renew = models.DateField(verbose_name=_('Date de renouvellement'), blank=True, null=True)
    renew_cycle = models.PositiveSmallIntegerField(
        verbose_name=_('Cycle du renouvellement (en jours)'), blank=True, null=True)
    comment = models.TextField(verbose_name=_('Commentaire'), blank=True, null=True)

    class Meta:
        abstract = True

    def renew(self):
        if self.date_activation is None:
            raise ValidationError(_("Aucune date d'activation n'est spécifiée!"))
        if self.date_renew is None:
            self.date_renew = self.date_activation
        self.date_renew = self.date_renew + dt.timedelta(days=self.renew_cycle)
        self.save()
