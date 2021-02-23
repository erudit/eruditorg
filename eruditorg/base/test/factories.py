from django.conf import settings
from django.contrib.auth.models import Group
from django.test import RequestFactory, Client
from django.contrib.auth.models import AnonymousUser

import factory
from faker import Factory as FakerFactory

from core.subscription.models import UserSubscriptions

faker = FakerFactory.create()


class UserFactory(factory.django.DjangoModelFactory):
    username = factory.Sequence(lambda n: "test{}".format(n))
    email = factory.Sequence(lambda n: "test{0}@example.com".format(n))

    class Meta:
        model = settings.AUTH_USER_MODEL

    @factory.post_generation
    def password(self, create, extracted, **kwargs):
        if extracted:
            password = extracted
        else:
            password = "default"
        self._plaintext_password = password
        self.set_password(password)
        self.save()


class GroupFactory(factory.django.DjangoModelFactory):
    name = factory.Sequence(lambda n: "{}-{}".format(str(n), faker.job()))

    class Meta:
        model = Group


def get_authenticated_request(user=None):
    request = RequestFactory().get("/")
    if user:
        request.user = user
    else:
        request.user = UserFactory()
    request.subscriptions = UserSubscriptions()
    request.session = dict()
    return request


def get_anonymous_request():
    request = RequestFactory().get("/")
    request.user = AnonymousUser()
    request.subscriptions = UserSubscriptions()
    request.session = dict()
    return request


def logged_client(user=None):
    if user is None:
        user = UserFactory.create()
    print(user.is_superuser)
    client = Client()
    client.login(username=user.username, password=user._plaintext_password)
    return client
