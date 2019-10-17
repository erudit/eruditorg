from django.db.models import Manager


class CampaignManager(Manager):
    def active_campaign(self):
        """ Return the first active campaign, there should be only one anyway. """
        return self.get_queryset().filter(active=True).first()
