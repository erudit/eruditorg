from django.db import models


class JournalCollectionManager(models.Manager):

    def get_queryset(self):
        """ Returns all collections associated with journals. """
        qs = super().get_queryset()
        return qs.filter(journal__isnull=False).distinct()
