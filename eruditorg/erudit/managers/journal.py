from django.db import models
from django.db.models import Q
from django.http.response import Http404

from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings


class InternalJournalManager(models.Manager):
    """Provides methods to work with journals that are not external.

    That is journals without external URLs. We make the assumption that instances without external
    URLs are instances that should be fully displayed.
    """

    def get_queryset(self):
        """ Returns all the internal Journal instances. """
        return (
            super(InternalJournalManager, self)
            .get_queryset()
            .filter(redirect_to_external_url=False)
        )


class ManagedJournalManager(models.Manager):
    """ Returns journals that are in the managed collections """

    def get_queryset(self):
        return super().get_queryset().filter(collection__code__in=settings.MANAGED_COLLECTIONS)


class LegacyJournalManager(models.Manager):
    """ Provides utility methods to work with journals in the legacy databases. """

    def get_by_id(self, code):
        """Return the journal by id

        The legacy system use a different id for scientific and cultural journals
        For scientific journals, the identifier is the code (shortname)
        For cultural journals, the identifier is the fedora localidentifier
        """

        # Codes aka shortnames are not unique in the legacy database. However, the code
        # is only used to identify scientific journals: for cultural journals, the localidentifier
        # is used instead. Our import script adds "1" to the code if a Journal with the same code
        # but a different localidentifier exists. We mixed up 'cd' and 'cd1' during the first import
        # and before we fully fix this situation, we need this hack.
        # ref: https://gitlab.erudit.org/erudit/portail/eruditorg/issues/1441
        if code == "cd":
            code = "cd1"

        return self.get(Q(code=code) | Q(localidentifier=code))

    def get_by_id_or_404(self, code):
        """Return the journal or 404 by id

        The legacy system use a different id for scientific and cultural journals
        For scientific journals, the identifier is the code (shortname)
        For cultural journals, the identifier is the fedora localidentifier
        """
        try:
            return self.get_by_id(code)
        except ObjectDoesNotExist:
            raise Http404


class UpcomingJournalManager(models.Manager):
    """Provides methods to work with upcoming journals.

    An upcoming journal is an internal journal with no published issues
    """

    def get_queryset(self):
        is_external = Q(redirect_to_external_url=True)
        no_issues = Q(issues=None)
        has_unpublished_issues = Q(issues__is_published=False)
        has_published_issues = Q(issues__is_published=True)

        return (
            super()
            .get_queryset()
            .filter(no_issues | has_unpublished_issues)
            .exclude(has_published_issues | is_external)
            .distinct()
        )


class InternalIssueManager(models.Manager):
    """Provides methods to work with issues that are not external.

    That is issues without external URLs. We make the assumption that instances without external
    URLs are instances that should be fully displayed.
    """

    def get_queryset(self):
        """ Returns all the internal Issue instances. """
        has_no_external_url = Q(external_url__isnull=True) | Q(external_url="")
        return super(InternalIssueManager, self).get_queryset().filter(has_no_external_url)
