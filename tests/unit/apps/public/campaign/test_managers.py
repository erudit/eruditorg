import pytest

from apps.public.campaign.models import Campaign
from apps.public.campaign.tests.factories import CampaignFactory


@pytest.mark.django_db
class TestCampaignManager:
    def test_active_campaign(self):
        campaign_1 = CampaignFactory()
        campaign_2 = CampaignFactory(active=True)
        campaign_3 = CampaignFactory()
        assert Campaign.objects.active_campaign() == campaign_2
