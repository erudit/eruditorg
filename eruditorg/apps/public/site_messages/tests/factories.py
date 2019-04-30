import factory

from ..models import SiteMessage, TargetSite


class TargetSiteFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = TargetSite


class SiteMessageFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = SiteMessage

    @factory.post_generation
    def target_sites(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            self.target_sites.set(extracted)
