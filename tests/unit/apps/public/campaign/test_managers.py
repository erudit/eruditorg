import pytest

from apps.public.campaign.models import Campaign
from apps.public.campaign.tests.factories import CampaignFactory


@pytest.mark.django_db
class TestCampaignManager:
    def test_active_campaign(self):
        CampaignFactory()
        campaign_2 = CampaignFactory(active=True)
        CampaignFactory()
        assert Campaign.objects.active_campaign() == campaign_2
