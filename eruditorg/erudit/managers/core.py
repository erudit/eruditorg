from django.db import models


class LegacyOrganisationManager(models.Manager):

    def get_by_id(self, legacy_id):

        return self.get(legacyorganisationprofile__account_id=legacy_id)
