from django.db import models
from erudit import models as e


class Contract(models.Model):
    """Contrat"""

    # parties
    journal

    type
    date_start
    date_end
    date_signature
    signatory

    quotation # cen-r devis propduction

    status # draft, valid

class ContractType(models.Model):
    """Type de contrat"""

    { production, abonnement, diffusion }
    name

