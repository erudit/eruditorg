# -*- coding: utf-8 -*-

import factory

from base.test.factories import UserFactory

from ..models import LegacyAccountProfile


class LegacyAccountProfileFactory(factory.django.DjangoModelFactory):
    user = factory.SubFactory(UserFactory)
    origin = LegacyAccountProfile.DB_RESTRICTION

    class Meta:
        model = LegacyAccountProfile
