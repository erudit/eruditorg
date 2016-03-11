from copy import deepcopy

from django.db import models
from django.utils.translation import gettext as _
from django.utils import timezone
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from django_fsm import FSMField, transition


class LastVersionManager(models.Manager):
    """
    Return only last version issues
    """
    def get_queryset(self):
        qs = super(LastVersionManager, self).get_queryset()
        return qs.filter(parent__isnull=True)


class IssueSubmission(models.Model):
    """ A journal issue submission by an editor """

    DRAFT = "D"
    SUBMITTED = "S"
    VALID = "V"
    ARCHIVED = "A"

    STATUS_CHOICES = (
        (DRAFT, _("Brouillon")),
        (SUBMITTED, _("Soumis")),
        (VALID, _("Validé")),
        (ARCHIVED, _("Archivé"))
    )

    objects = models.Manager()
    head = LastVersionManager()

    status = FSMField(default=DRAFT, protected=False)

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

    date_created = models.DateTimeField(
        editable=False,
        null=True,
        verbose_name=_("Date de l'envoi"),
    )

    date_modified = models.DateTimeField(
        editable=False,
        null=True,
        verbose_name=_("Date de modification"),
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

    parent = models.OneToOneField(
        'self', null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return "{} - {}, volume {}".format(
            self.date_created,
            self.journal,
            self.volume
        )

    def get_absolute_url(self):
        """ Return the absolute URL for this model """
        return reverse('userspace:editor:update', kwargs={'pk': self.pk})

    @property
    def is_submitted(self):
        return self.status == self.SUBMITTED

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
        copy = self.save_version()
        copy.status = IssueSubmission.DRAFT
        copy.save()

    @transition(field=status, source='*', target=ARCHIVED,
                permission=lambda user: (
                    user.has_perm('editor.manage_issuesubmission') or
                    user.has_perm('editor.review_issuesubmission')),
                custom=dict(verbose_name=("Archiver")))
    def archive(self):
        """
        Archives the issue
        """
        pass

    def save_version(self):
        if self.parent is not None:
            raise Exception(
                "Version can't be created. This object is already one.")

        copy = deepcopy(self)
        copy.id = None
        copy.date_created = self.date_created
        copy.save()
        self.parent = copy
        self._save()
        return copy

    def _save(self, *args, **kwargs):
        """
        original save method renamed
        """
        super().save(*args, **kwargs)

    def save(self, *args, **kwargs):
        """
        Ensure an old version can't be modified.
        """
        if self.date_created is None:
            self.date_created = timezone.now()
        self.date_modified = timezone.now()
        if self.parent is None:
            super().save(*args, **kwargs)

    class Meta:
        verbose_name = _("Envoi de numéro")
        verbose_name_plural = _("Envois de numéros")
