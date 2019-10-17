import pytest

from apps.public.campaign.models import Campaign
from apps.public.campaign.tests.factories import CampaignFactory


@pytest.mark.django_db
class TestCampaign:
    def test_save_active_campaign_deactivate_previously_active_campaign(self):
        campaign_1 = CampaignFactory(active=True)
        campaign_2 = CampaignFactory()
        campaign_2.active = True
        campaign_2.save()
        campaign_1 = Campaign.objects.get(pk=campaign_1.id)
        campaign_2 = Campaign.objects.get(pk=campaign_2.id)
        assert not campaign_1.active
        assert campaign_2.active
