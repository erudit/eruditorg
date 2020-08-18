# -*- coding: utf-8 -*-

import factory
from django.contrib.contenttypes.models import ContentType
from faker import Factory as FakerFactory

from base.test.factories import GroupFactory
from base.test.factories import UserFactory

from ..models import Authorization
from core.authorization.defaults import AuthorizationConfig as AC

faker = FakerFactory.create()


class AuthorizationFactory(factory.django.DjangoModelFactory):
    user = factory.SubFactory(UserFactory)
    group = factory.SubFactory(GroupFactory)
    authorization_codename = factory.LazyAttribute(lambda t: faker.text(max_nb_chars=100))

    class Meta:
        model = Authorization

    @staticmethod
    def create_can_manage_issue_subscriptions(user, journal):
        journal_ct = ContentType.objects.get(app_label="erudit", model="journal")
        return AuthorizationFactory(
            content_type=journal_ct,
            user=user,
            object_id=journal.id,
            authorization_codename=AC.can_manage_issuesubmission.codename
        )
