# -*- coding: utf-8 -*-

from django.conf import settings
from django.contrib.auth.models import Group
import factory
from faker import Factory as FakerFactory

faker = FakerFactory.create()


class UserFactory(factory.django.DjangoModelFactory):
    username = factory.LazyAttribute(lambda t: faker.user_name())
    email = factory.Sequence(lambda n: 'test{0}@example.com'.format(n))

    class Meta:
        model = settings.AUTH_USER_MODEL


class GroupFactory(factory.DjangoModelFactory):
    name = factory.Sequence(lambda n: '{}-{}'.format(str(n), faker.job()))

    class Meta:
        model = Group
