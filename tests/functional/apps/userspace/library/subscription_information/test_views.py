# -*- coding: utf-8 -*-

import datetime as dt

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.files import File
from django.core.files.images import get_image_dimensions
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django.test.client import Client
import pytest

from erudit.test.factories import OrganisationFactory

from base.test.factories import UserFactory
from core.authorization.defaults import AuthorizationConfig as AC
from core.authorization.test.factories import AuthorizationFactory
from core.subscription.test.factories import JournalAccessSubscriptionFactory
from core.subscription.test.factories import JournalAccessSubscriptionPeriodFactory


@pytest.mark.django_db
class TestSubscriptionInformationUpdateView:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.client = Client()

        self.user = UserFactory.create(username="foobar")
        self.user.set_password("notsecret")
        self.user.save()

        self.organisation = OrganisationFactory.create()
        self.organisation.members.add(self.user)
        self.subscription = JournalAccessSubscriptionFactory.create(organisation=self.organisation)
        now_dt = dt.datetime.now()
        JournalAccessSubscriptionPeriodFactory.create(
            subscription=self.subscription,
            start=now_dt - dt.timedelta(days=10),
            end=now_dt + dt.timedelta(days=8),
        )

        # Set up some images used for doing image tests
        images_dict = {}

        # Fetch an image aimed to be resized
        f = open(settings.MEDIA_ROOT + "/200x200.png", "rb")
        images_dict["200x200"] = File(f)

        self.images_dict = images_dict

        yield

        # teardown
        # --

        for img in self.images_dict.values():
            img.close()

        try:
            self.organisation.badge.delete()
        except Exception:
            pass
        self.organisation.delete()

    def test_cannot_be_accessed_by_a_user_who_cannot_manage_subscriptions_information(self):
        # Setup
        self.organisation.members.clear()
        self.client.login(username=self.user.username, password="notsecret")

        url = reverse(
            "userspace:library:subscription_information:update",
            kwargs={
                "organisation_pk": self.organisation.pk,
            },
        )

        # Run
        response = self.client.get(url)

        # Check
        assert response.status_code == 403

    def test_can_be_used_to_set_a_badge(self):
        # Setup
        AuthorizationFactory.create(
            content_type=ContentType.objects.get_for_model(self.organisation),
            object_id=self.organisation.id,
            user=self.user,
            authorization_codename=AC.can_manage_organisation_subscription_information.codename,
        )

        self.client.login(username=self.user.username, password="notsecret")
        post_data = {
            "badge": SimpleUploadedFile("test.jpg", self.images_dict["200x200"].read()),
        }

        url = reverse(
            "userspace:library:subscription_information:update",
            kwargs={
                "organisation_pk": self.organisation.pk,
            },
        )

        # Run
        response = self.client.post(url, post_data, follow=False)

        # Check
        assert response.status_code == 302
        self.organisation.refresh_from_db()
        assert self.organisation.badge is not None
        width, height = get_image_dimensions(self.organisation.badge)
        assert width == 140
        assert height == 140
