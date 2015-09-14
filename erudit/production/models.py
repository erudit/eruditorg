from django.db import models
from erudit import models as e


# choices

PRODUCTION_TYPE = (
    ('MIN', 'Minimal'),
    ('COMP', 'Complète'),
)


class ProductionCenter(models.Model):
    """Centre de production"""

class JournalProduction(models.Model):
    journal = models.ForeignKey('e.Journal', related_name='production')
    production_center = models.ForeignKey('ProductionCenter')
    production_type = models.CharField(choices=PRODUCTION_TYPE)
