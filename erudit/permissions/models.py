from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


class Rule(models.Model):
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
    content_type = models.ForeignKey(
        ContentType,
        verbose_name=_('Type'),
        blank=True,
        null=True,
    )
    content_object = GenericForeignKey('content_type', 'object_id')
    object_id = models.PositiveIntegerField(blank=True, null=True)

    user = models.ForeignKey('auth.User', blank=True, null=True)
    group = models.ForeignKey('auth.Group', blank=True, null=True)
    permission = models.CharField(choices=(), max_length=100)

    class Meta:
        verbose_name = _("Règle")

    def __str__(self):
        if self.user:
            who = self.user
        else:
            who = self.group

        if self.content_object:
            on = "on {}".format(self.content_object)
        else:
            on = ""
        return "\"{} can {} {}\"".format(who, self.permission, on)

    def clean(self):
        if not self.user and not self.group:
            raise ValidationError(_('Choisissez un utilisateur OU un groupe'))
        if self.user and self.group:
            raise ValidationError(_('Choisissez SOIT un utilisateur SOIT un groupe'))
        if (self.content_type or self.object_id) and self.permission.startswith('all:'):
            raise ValidationError(
                _('Impossible de changer la permission liée à un objet en particulier'))

            raise ValidationError(_('Choisissez SOIT un utilisateur SOIT un groupe'))
