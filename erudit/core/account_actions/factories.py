# -*- coding: utf-8 -*-

import factory
from faker import Factory

from .core.key import gen_action_key
from .models import AccountActionToken

faker = Factory.create()


class AccountActionTokenFactory(factory.django.DjangoModelFactory):
    key = factory.Sequence(lambda n: gen_action_key())

    email = faker.email()
    first_name = faker.first_name()
    last_name = faker.last_name()

    action = factory.Sequence(lambda n: 'action-{}'.format(n))

    class Meta:
        model = AccountActionToken
