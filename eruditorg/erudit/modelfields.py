# -*- coding: utf-8 -*-

import io
import os

from django.core.files.images import get_image_dimensions
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import models
from django.forms import ValidationError
from django.template.defaultfilters import filesizeformat
from django.utils.translation import gettext_lazy as _
from PIL import Image


# Note: the following SizeConstrainedImageField model field originally comes from the
# django-machina's model fields module.
# See: https://github.com/ellmetha/django-machina/blob/master/machina/models/fields.py#L193


class SizeConstrainedImageField(models.ImageField):
    """
    A SizeConstrainedImageField is an ImageField whose image can be resized before being saved.
    This field also adds the capability of checking the image size, width and height a user may
    send.
    """

    def __init__(self, *args, **kwargs):
        self.width = kwargs.pop("width", None)
        self.height = kwargs.pop("height", None)
        # Both min_width and max_width must be provided in order to be used
        self.min_width = kwargs.pop("min_width", None)
        self.max_width = kwargs.pop("max_width", None)
        # Both min_height and max_height must be provided in order to be used
        self.min_height = kwargs.pop("min_height", None)
        self.max_height = kwargs.pop("max_height", None)
        self.max_upload_size = kwargs.pop("max_upload_size", 0)
        super(SizeConstrainedImageField, self).__init__(*args, **kwargs)

    def clean(self, *args, **kwargs):
        data = super(SizeConstrainedImageField, self).clean(*args, **kwargs)
        image = data.file

        # Controls the file size
        if self.max_upload_size and hasattr(image, "size"):
            if image.size > self.max_upload_size:
                raise ValidationError(
                    _("Files of size greater than {} are not allowed. Your file is {}").format(
                        filesizeformat(self.max_upload_size), filesizeformat(image.size)
                    )
                )

        # Controls the image size
        image_width, image_height = get_image_dimensions(data)
        if (
            self.min_width
            and self.max_width
            and not self.min_width <= image_width <= self.max_width
        ):
            raise ValidationError(
                _(
                    "Images of width lesser than {}px or greater than {}px or are not allowed. "
                    "The width of your image is {}px"
                ).format(self.min_width, self.max_width, image_width)
            )
        if (
            self.min_height
            and self.max_height
            and not self.min_height <= image_height <= self.max_height
        ):
            raise ValidationError(
                _(
                    "Images of height lesser than {}px or greater than {}px or are not allowed. "
                    "The height of your image is {}px"
                ).format(self.min_height, self.max_height, image_height)
            )

        return data

    def save_form_data(self, instance, data):
        if data and self.width and self.height:
            content = self.resize_image(data.read(), (self.width, self.height))

            # Handle the filename because the image will be converted to PNG
            filename = os.path.splitext(os.path.split(data.name)[-1])[0]
            filename = "{}.png".format(filename)

            # Regenerate a File object
            data = SimpleUploadedFile(filename, content)
        super(SizeConstrainedImageField, self).save_form_data(instance, data)

    def resize_image(self, data, size):
        """
        Resizes the given image to fit inside a box of the given size
        """
        image = Image.open(io.BytesIO(data))

        # Resize!
        image.thumbnail(size, Image.ANTIALIAS)

        string = io.BytesIO()
        image.save(string, format="PNG")
        return string.getvalue()
