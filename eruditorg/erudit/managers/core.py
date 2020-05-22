from django.db import models


class LegacyOrganisationManager(models.Manager):

    def get_by_id(self, legacy_id):

        return self.get(legacyorganisationprofile__account_id=legacy_id)


class JournalCollectionManager(models.Manager):

    def get_queryset(self):
        """ Returns all collections associated with journals. """
        qs = super().get_queryset()
        return qs.filter(journal__isnull=False).distinct()
