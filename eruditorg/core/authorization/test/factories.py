# -*- coding: utf-8 -*-

import factory
from faker import Factory as FakerFactory

from base.test.factories import GroupFactory
from base.test.factories import UserFactory

from ..models import Authorization

faker = FakerFactory.create()


class AuthorizationFactory(factory.DjangoModelFactory):
    user = factory.SubFactory(UserFactory)
    group = factory.SubFactory(GroupFactory)
    authorization_codename = factory.LazyAttribute(lambda t: faker.text(max_nb_chars=100))

    class Meta:
        model = Authorization
