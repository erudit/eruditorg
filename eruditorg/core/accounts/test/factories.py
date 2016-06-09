# -*- coding: utf-8 -*-

import factory

from base.test.factories import UserFactory

from ..models import AbonnementProfile


class AbonnementProfileFactory(factory.django.DjangoModelFactory):
    user = factory.SubFactory(UserFactory)

    class Meta:
        model = AbonnementProfile
