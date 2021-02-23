# -*- coding :utf-8 -*-

from django.conf import settings
from django.core.files import File
from django.core.files.images import get_image_dimensions
from django.core.files.uploadedfile import SimpleUploadedFile
import pytest

from erudit.test.factories import OrganisationFactory

from apps.userspace.library.subscription_information.forms import SubscriptionInformationForm


@pytest.mark.django_db
class TestSubscriptionInformationForm:
    @pytest.yield_fixture(autouse=True)
    def setup(self):
        self.organisation = OrganisationFactory.create()

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
        except:
            pass
        self.organisation.delete()

    def test_can_resize_a_uploaded_badge(self):
        # Setup
        files_data = {
            "badge": SimpleUploadedFile("test.jpg", self.images_dict["200x200"].read()),
        }
        # Run
        form = SubscriptionInformationForm(
            data={}, files=files_data, organisation=self.organisation
        )
        # Check
        assert form.is_valid()
        form.save()
        self.organisation.refresh_from_db()
        assert self.organisation.badge is not None
        width, height = get_image_dimensions(self.organisation.badge)
        assert width == 140
        assert height == 140
