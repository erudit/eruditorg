# -*- coding: utf-8 -*-

from django.conf import settings
from django.contrib.auth.models import Group
from django.test import RequestFactory
from django.contrib.auth.models import AnonymousUser

import factory
from faker import Factory as FakerFactory

from core.subscription.models import UserSubscriptions

faker = FakerFactory.create()


class UserFactory(factory.django.DjangoModelFactory):
    username = factory.LazyAttribute(lambda t: faker.user_name())
    email = factory.Sequence(lambda n: 'test{0}@example.com'.format(n))

    class Meta:
        model = settings.AUTH_USER_MODEL

    @factory.post_generation
    def password(self, create, extracted, **kwargs):

        if extracted:
            self.set_password(extracted)
        else:
            self.set_password("default")
        self.save()


class GroupFactory(factory.DjangoModelFactory):
    name = factory.Sequence(lambda n: '{}-{}'.format(str(n), faker.job()))

    class Meta:
        model = Group


def get_authenticated_request(user=None):
    request = RequestFactory().get('/')
    if user:
        request.user = user
    else:
        request.user = UserFactory()
    request.subscriptions = UserSubscriptions()
    request.session = dict()
    return request


def get_anonymous_request():
    request = RequestFactory().get('/')
    request.user = AnonymousUser()
    request.subscriptions = UserSubscriptions()
    request.session = dict()
    return request
