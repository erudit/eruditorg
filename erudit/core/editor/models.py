from django.db import models
from django.utils.translation import gettext as _
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from django_fsm import FSMField, transition


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

    status = FSMField(default=DRAFT, protected=True)

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
        return reverse('userspace:editor:update', kwargs={'pk': self.pk})

    @transition(field=status, source=DRAFT, target=SUBMITTED,
                permission=lambda user: user.has_perm(
                    'editor.manage_issuesubmission'),
                custom=dict(verbose_name=("Soumettre")))
    def submit(self):
        """
        Send issue for review
        """
        pass

    @transition(field=status, source=SUBMITTED, target=VALID,
                permission=lambda user: user.has_perm(
                    'editor.review_issuesubmission'),
                custom=dict(verbose_name=_("Approuver")))
    def approve(self):
        """
        Validate the issue
        """
        pass

    @transition(field=status, source=SUBMITTED, target=DRAFT,
                permission=lambda user: user.has_perm(
                    'editor.review_issuesubmission'),
                custom=dict(verbose_name=_("Marquer à corriger")))
    def refuse(self):
        """
        Resend the issue for modifications
        """
        pass

    class Meta:
        verbose_name = _("Envoi de numéro")
        verbose_name_plural = _("Envois de numéros")
