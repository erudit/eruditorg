# -*- coding: utf-8 -*-

from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from .defaults import AuthorizationConfig


class Authorization(models.Model):
    date_creation = models.DateTimeField(
        editable=False,
        null=True,
        default=timezone.now,
        verbose_name=_("Date de création")
    )
    date_modification = models.DateTimeField(
        editable=False,
        null=True,
        default=timezone.now,
        verbose_name=_("Date de modification")
    )

    content_type = models.ForeignKey(ContentType, verbose_name=_('Type'), blank=True, null=True)
    object_id = models.PositiveIntegerField(blank=True, null=True)
    content_object = GenericForeignKey('content_type', 'object_id')

    user = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True)
    group = models.ForeignKey('auth.Group', blank=True, null=True)

    # The 'authorization_codename' defines the authorization that will be
    # granted to the considered user or group.
    authorization_codename = models.CharField(
        choices=AuthorizationConfig.get_choices(include_staff_only=True), max_length=100)

    class Meta:
        verbose_name = _('Autorisation')

    def __str__(self):
        if self.user:
            who = self.user
        else:
            who = self.group

        if self.content_object:
            on = 'on {}'.format(self.content_object)
        else:
            on = ''
        return '"{} can {} {}"'.format(who, self.authorization_codename, on)

    def clean(self):
        if not self.user and not self.group:
            raise ValidationError(_("Choisissez un utilisateur OU un groupe"))
        if self.user and self.group:
            raise ValidationError(_("Choisissez SOIT un utilisateur SOIT un groupe"))
        if (self.content_type or self.object_id) and self.authorization_codename.startswith('all:'):
            raise ValidationError(
                _("Impossible de changer l'autorisation liée à un objet en particulier"))

            raise ValidationError(_("Choisissez SOIT un utilisateur SOIT un groupe"))
