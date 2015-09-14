from django.db import models
from erudit import models as e


class GrantingAgency(models.Model):
    """Organisme subventionnaire"""

    name

class Grant(models.Model):
    """Subvention"""

    granting_agency
    journal = models.ForeignKey('e.Journal', related_name='grants')

    amount
    date_start
    date_end
