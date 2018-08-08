from django.dispatch import receiver
from django_fsm import signals

from core.editor.models import IssueSubmission
from core.editor.models import IssueSubmissionStatusTrack


@receiver(signals.post_transition, sender=IssueSubmission)
def register_status_track(sender, instance, name, source, target, **kwargs):
    # Registers a new track for the status of the issue submission
    status_track = IssueSubmissionStatusTrack.objects.create(
        issue_submission=instance, status=instance.status)

    # If the IssueSubmission instance was submitted, attaches the last files version to
    # the status track.
    if instance.status == IssueSubmission.SUBMITTED:
        status_track.files_version = instance.last_files_version
        status_track.save()
