import factory

from ..models import Campaign


class CampaignFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Campaign
