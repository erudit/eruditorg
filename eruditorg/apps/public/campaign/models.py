from django.db import models, transaction
from django.utils.translation import gettext_lazy as _

from erudit.modelfields import SizeConstrainedImageField

from .managers import CampaignManager


class Campaign(models.Model):
    active = models.BooleanField(
        verbose_name=_("Active"),
        help_text=_(
            "Activer la campagne. <strong>La campagne précédente sera désactivée et remplacée "
            "par celle-ci.</strong>"
        ),
        default=False,
    )
    url = models.URLField(
        verbose_name=_("URL"),
        help_text=_("URL du lien sur l'image"),
        null=False,
        blank=False,
        default="",
    )
    image = SizeConstrainedImageField(
        verbose_name=_("Image"),
        help_text=_(
            "L'image doit avoir une largeur exacte de 267px et une hauteur maximale de 450px."
        ),
        blank=False,
        null=False,
        upload_to="campaigns",
        min_width=267,
        max_width=267,
        max_height=450,
        default="",
    )
    title = models.CharField(
        verbose_name=_("title"),
        help_text=_("Attribut <em>title</em> de l'image"),
        blank=False,
        null=False,
        max_length=256,
        default="",
    )
    alt = models.CharField(
        verbose_name=_("alt"),
        help_text=_("Attribut <em>alt</em> de l'image"),
        blank=False,
        null=False,
        max_length=256,
        default="",
    )

    objects = CampaignManager()

    class Meta:
        verbose_name = _("Campagne")
        verbose_name_plural = _("Campagnes")

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        """ If we activate this campaign, deactivate the previously active one. """
        if not self.active:
            return super().save(*args, **kwargs)
        with transaction.atomic():
            Campaign.objects.filter(active=True).update(active=False)
            return super().save(*args, **kwargs)
