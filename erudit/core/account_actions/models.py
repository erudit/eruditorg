# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import datetime as dt

from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils import timezone
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from . import signals
from .conf import settings as account_actions_settings
from .core.key import gen_action_key
from .managers import ConsumedManager
from .managers import PendingManager


@python_2_unicode_compatible
class AccountActionToken(models.Model):
    """
    Defines an action that can be performed by a single user in a limited period of time.
    """
    created = models.DateTimeField(auto_now_add=True, verbose_name=_('Date de création'))
    updated = models.DateTimeField(auto_now=True, verbose_name=_('Date de modification'))

    # The 'user' foreign key should be filled only when the action token is consumed.
    consumption_date = models.DateTimeField(
        verbose_name=_('Date de consommation'), blank=True, null=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, verbose_name=_('Utilisateur'), blank=True, null=True)

    # This is a key used to identify the action
    key = models.CharField(max_length=40, unique=True)

    # The following information must be filled when creating an action token.
    first_name = models.CharField(
        max_length=30, verbose_name=_('Prénom'), blank=True, null=True)
    last_name = models.CharField(
        max_length=30, verbose_name=_('Nom'), blank=True, null=True)
    email = models.EmailField(verbose_name=_('Adresse e-mail'))

    # The 'action' field should contain a value identifying the considered action. It can be
    # associated with a content object through a generic foreign key.
    action = models.CharField(max_length=100, verbose_name=_('Action'))
    content_type = models.ForeignKey(ContentType, verbose_name=_('Type'), blank=True, null=True)
    object_id = models.PositiveIntegerField(blank=True, null=True)
    content_object = GenericForeignKey('content_type', 'object_id')

    objects = models.Manager()
    consumed_objects = ConsumedManager()
    pending_objects = PendingManager()

    class Meta:
        verbose_name = _("Jeton d'action")
        verbose_name_plural = _("Jetons d'actions")

    def __str__(self):
        return '{0} - {1}'.format(self.created, self.action)

    def save(self, *args, **kwargs):
        creation = self.pk is None
        if creation and not self.key:
            self.key = gen_action_key()

        old_instance = self.__class__._default_manager.get(pk=self.pk) if self.pk else None
        super(AccountActionToken, self).save(*args, **kwargs)

        # Triggers a signal indicating that the action token has been consumed.
        if old_instance and not old_instance.is_consumed and self.is_consumed:
            signals.action_token_consumed.send(sender=self, instance=self, consumer=self.user)

    def consume(self, user):
        self.user = user
        self.consumption_date = timezone.now()
        self.save()

    @property
    def expiration_date(self):
        """ Returns the expiration date of the action token. """
        return self.created + dt.timedelta(
            days=account_actions_settings.ACTION_TOKEN_VALIDITY_DURATION)

    @property
    def is_expired(self):
        """ Returns a boolean indicating if the action token has expired. """
        return timezone.now() > self.expiration_date

    @property
    def is_consumed(self):
        """ Returns a boolean indicating if the action token has been consumed. """
        return self.consumption_date is not None and self.user is not None
