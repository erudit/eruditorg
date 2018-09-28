from django.conf import settings
from django.db import models


class SavedCitation(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='saved_citations',
        on_delete=models.CASCADE
    )
    solr_id = models.CharField(max_length=100)

    class Meta:
        unique_together = [('user', 'solr_id')]
