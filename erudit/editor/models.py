from django.db import models
from django.utils.translation import gettext as _
from django.contrib.auth.models import User


class JournalSubmission(models.Model):
    """ A journal issue submission by an editor """
    journal = models.ForeignKey(
        'erudit.journal',
        verbose_name=_("Revue"),
    )

    volume = models.CharField(
        max_length=100,
        verbose_name=_("Volume")
    )

    date_created = models.DateField(
        verbose_name=_("Date de l'envoi"),
    )

    contact = models.ForeignKey(
        User,
        verbose_name=_("Personne contact")
    )

    comment = models.TextField(
        verbose_name=_("Commentaire"),
        blank=True, null=True
    )

    submission_file = models.FileField(
        upload_to='uploads',
        verbose_name=_("Fichier")
    )

    def __str__(self):
        return "{} - {}, volume {}".format(
            self.date_created,
            self.journal,
            self.volume
        )

    class Meta:
        verbose_name = _("Envoi de numéro")
        verbose_name_plural = _("Envois de numéros")
