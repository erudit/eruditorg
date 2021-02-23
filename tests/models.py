# -*- coding: utf-8 -*-

from django.db import models

from erudit.modelfields import SizeConstrainedImageField


RESIZED_IMAGE_WIDTH = 100
RESIZED_IMAGE_HEIGHT = 100
VALIDATED_IMAGE_MIN_WIDTH = 100
VALIDATED_IMAGE_MAX_WIDTH = 120
VALIDATED_IMAGE_MIN_HEIGHT = 100
VALIDATED_IMAGE_MAX_HEIGHT = 120
VALIDATED_IMAGE_MAX_SIZE = 12000


class DummyModel(models.Model):
    """ This model will be used for testing purposes only. """

    resized_image = SizeConstrainedImageField(
        upload_to="eruditcore/test_images",
        width=RESIZED_IMAGE_WIDTH,
        height=RESIZED_IMAGE_HEIGHT,
        null=True,
        blank=True,
    )
    validated_image = SizeConstrainedImageField(
        upload_to="eruditcore/test_images",
        min_width=VALIDATED_IMAGE_MIN_WIDTH,
        max_width=VALIDATED_IMAGE_MAX_WIDTH,
        min_height=VALIDATED_IMAGE_MIN_HEIGHT,
        max_height=VALIDATED_IMAGE_MAX_HEIGHT,
        max_upload_size=VALIDATED_IMAGE_MAX_SIZE,
        null=True,
        blank=True,
    )

    class Meta:
        app_label = "tests"
