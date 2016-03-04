# -*- coding: utf-8 -*-

from django.conf import settings
import factory


class UserFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = settings.AUTH_USER_MODEL

    username = factory.Sequence(lambda n: 'username{}'.format(n))
