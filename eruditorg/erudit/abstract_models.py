from django.db import models
from django.utils.translation import ugettext_lazy as _


class FedoraDated(models.Model):
    """ Provides a creation date and an update date for Fedora-related models.

    Note that these fields do not used the auto_now_add/auto_now attributes. So these values should
    be set manually.
    """
    fedora_created = models.DateTimeField(
        verbose_name=_('Date de création sur Fedora'), blank=True, null=True)

    fedora_updated = models.DateTimeField(
        verbose_name=_('Date de modification sur Fedora'), blank=True, null=True)

    class Meta:
        abstract = True
