from django.db import models
from django.utils.translation import gettext as _
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from erudit.models import Publisher


class IssueSubmission(models.Model):
    """ A journal issue submission by an editor """

    DRAFT = "D"
    SUBMITTED = "S"
    VALID = "V"

    STATUS_CHOICES = (
        (DRAFT, _("Brouillon")),
        (SUBMITTED, _("Soumis")),
        (VALID, _("Validé"))
    )

    status = models.CharField(
        max_length=1,
        choices=STATUS_CHOICES,
        default=DRAFT
    )

    journal = models.ForeignKey(
        'erudit.journal',
        verbose_name=_("Revue"),
    )

    year = models.CharField(
        max_length=9,
        verbose_name=_("Année")
    )

    volume = models.CharField(
        max_length=100,
        verbose_name=_("Volume"),
        blank=True, null=True
    )

    number = models.CharField(
        max_length=100,
        verbose_name=_("Numéro")
    )

    date_created = models.DateField(
        verbose_name=_("Date de l'envoi"),
        auto_now_add=True
    )

    contact = models.ForeignKey(
        User,
        verbose_name=_("Personne contact")
    )

    comment = models.TextField(
        verbose_name=_("Commentaire"),
        blank=True, null=True
    )

    submissions = models.ManyToManyField(
        'plupload.ResumableFile'
    )

    def __str__(self):
        return "{} - {}, volume {}".format(
            self.date_created,
            self.journal,
            self.volume
        )

    def get_absolute_url(self):
        """ Return the absolute URL for this model """
        return reverse('editor:update', kwargs={'pk': self.pk})

    def has_access(self, user):
        """ Determine if the user has access to this IssueSubmission

        A user has access to an IssueSubmission if it is a member of the
        publisher of the journal.
        """
        if not user:
            return False

        return bool(
            Publisher.objects.filter(
                journals=self.journal,
                members=user
            ).count()
        )

    class Meta:
        verbose_name = _("Envoi de numéro")
        verbose_name_plural = _("Envois de numéros")
