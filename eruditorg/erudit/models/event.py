from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.template import defaultfilters


# Implementation note: If you look around to see where these events are recorded, you'll see that
# they's recorded at the view level. At first sight, using signals seems like a more proper hook
# to use for event recording, but the problem is that we want to fill the ``author`` field and
# we need to access the request for that. The request is not available during signal handling.

class Event(models.Model):
    """ Tracks important events in the system.

        Every time a specific and pre-determined event happens in the system, we log it in this
        model. This allows us to track who made what action when, and on which object.
    """

    TYPE_SUBMISSION_CREATED = 1
    TYPE_SUBMISSION_STATUS_CHANGE = 2
    TYPE_CHOICES = (
        (TYPE_SUBMISSION_CREATED, _("Création de soumission")),
        (TYPE_SUBMISSION_STATUS_CHANGE, _("Changement de statut de soumission")),
    )

    type = models.PositiveIntegerField(choices=TYPE_CHOICES)
    time = models.DateTimeField(auto_now_add=True, verbose_name=_("Date/Heure"))
    author = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_("Auteur"))
    target_content_type = models.ForeignKey(ContentType)
    target_object_id = models.PositiveIntegerField()
    target_object = GenericForeignKey('target_content_type', 'target_object_id')
    comment = models.TextField(verbose_name=_("Commentaire"))

    class Meta:
        verbose_name = _("Événement")
        verbose_name_plural = _("Événements")

    def __str__(self):
        datetime = defaultfilters.date(self.time, settings.SHORT_DATETIME_FORMAT)
        return "{} - {} - {}".format(self.get_type_display(), self.author, datetime)

    @classmethod
    def create_submission(cls, author, submission):
        return cls.objects.create(
            type=cls.TYPE_SUBMISSION_CREATED,
            author=author,
            target_object=submission,
            comment=""
        )

    @classmethod
    def change_submission_status(cls, author, submission, old_status):
        comment = "{} --> {}".format(old_status, submission.status)
        return cls.objects.create(
            type=cls.TYPE_SUBMISSION_STATUS_CHANGE,
            author=author,
            target_object=submission,
            comment=comment
        )
