# -*- coding: utf-8 -*-

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files import File
from io import BytesIO
from PIL import Image
import pytest

from tests.models import RESIZED_IMAGE_HEIGHT
from tests.models import RESIZED_IMAGE_WIDTH
from tests.models import DummyModel


# Note: the following TestSizeConstrainedImageField tests originally comes from the django-machina's
# unit tests.
# See: https://github.com/ellmetha/django-machina/blob/master/tests/unit/core/test_fields.py#L137


@pytest.mark.django_db
class TestSizeConstrainedImageField:
    @pytest.yield_fixture(autouse=True)
    def setup(self):
        # Set up some images used for doing image tests
        images_dict = {}

        # Fetch an image aimed to be resized
        f = open(settings.MEDIA_ROOT + "/to_be_resized_image.png", "rb")
        images_dict["to_be_resized_image"] = File(f)

        # Fetch a big image
        f = open(settings.MEDIA_ROOT + "/too_large_image.jpg", "rb")
        images_dict["too_large_image"] = File(f)

        # Fetch a wide image
        f = open(settings.MEDIA_ROOT + "/too_wide_image.jpg", "rb")
        images_dict["too_wide_image"] = File(f)

        # Fetch a high image
        f = open(settings.MEDIA_ROOT + "/too_high_image.jpg", "rb")
        images_dict["too_high_image"] = File(f)

        self.images_dict = images_dict

        yield

        # teardown
        # --

        for img in self.images_dict.values():
            img.close()
        tests = DummyModel.objects.all()
        for test in tests:
            try:
                test.resized_image.delete()
            except:  # noqa
                pass
            try:
                test.validated_image.delete()
            except:  # noqa
                pass

    def test_can_resize_images_before_saving_them(self):
        # Setup
        test = DummyModel()
        # Run
        field = test._meta.get_field("resized_image")
        field.save_form_data(test, self.images_dict["to_be_resized_image"])
        test.full_clean()
        test.save()
        # Check
        image = Image.open(BytesIO(test.resized_image.read()))
        assert image.size == (RESIZED_IMAGE_WIDTH, RESIZED_IMAGE_HEIGHT)

    def test_should_not_accept_images_with_incorrect_sizes_or_dimensions(self):
        # Setup
        test = DummyModel()
        field = test._meta.get_field("validated_image")
        invalid_images = [
            "too_large_image",
            "too_wide_image",
            "too_high_image",
        ]
        # Run & check
        for img in invalid_images:
            field.save_form_data(test, self.images_dict[img])
            with pytest.raises(ValidationError):
                test.full_clean()
