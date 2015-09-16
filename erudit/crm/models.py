from django.db import models
from erudit import models as e

class OrganisationType(models.Model):

    name

class PersonRole(models.Model):
    """Rôle"""

    name
    for_journal

class JournalPersonRole(models.Model):
    """Rôle pour revue"""

    # identification
    journal
    person
    role

    # meta
    date_start
    date_end
    comment
