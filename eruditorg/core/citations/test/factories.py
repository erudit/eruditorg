# -*- coding: utf-8 -*-

import factory

from base.test.factories import UserFactory

from ..models import SavedCitationList


class SavedCitationListFactory(factory.DjangoModelFactory):
    user = factory.SubFactory(UserFactory)

    class Meta:
        model = SavedCitationList
