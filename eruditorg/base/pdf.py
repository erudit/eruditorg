# -*- coding: utf-8 -*-
import os
from io import BytesIO
import pikepdf
import mimetypes

from weasyprint.urls import default_url_fetcher
from django.conf import settings

# Make sure mimetypes knows of all the extensions used in the pdf
mimetypes.add_type("application/vnd.ms-fontobject", ".eot")
mimetypes.add_type("font/woff", ".woff")
mimetypes.add_type("font/woff2", ".woff2")
mimetypes.add_type("font/ttf", ".ttf")
mimetypes.add_type("image/svg+xml", ".svg")


def add_coverpage_to_pdf(coverpage, content):
    """ Add the coverpage to the PDF

    Return the resulting PDF bytes """
    output = BytesIO()
    coverpage_pdf = pikepdf.open(coverpage)
    content_pdf = pikepdf.open(content)
    coverpage_pdf.pages.extend(content_pdf.pages)
    coverpage_pdf.save(output)
    output.seek(0)
    return output.read()


def get_pdf_first_page(content):
    """ Return the first page of the PDF
    """
    output = BytesIO()
    pdf = pikepdf.open(content)
    del pdf.pages[1:]
    pdf.save(output)
    output.seek(0)
    return output.read()


def local_url_fetcher(url):
    """ An URL fetcher that supports reading local files from the disk

    If the file has the "local:" prefix, read it from the disk.
    Otherwise call the default url fetcher.

    Just like the ``default_url_fetcher``, it is the caller's responsibility
    to close the ``file_obj`` returned.
    """

    if url.lower().startswith('local:'):
        path = os.path.normpath(settings.STATIC_ROOT + url.lstrip('local:'))

        if not path.startswith(settings.STATIC_ROOT):
            raise ValueError("Path should be a subpath of settings.STATIC_ROOT")
        file_obj = open(path, "rb")
        asset = dict(
            file_obj=file_obj,
            mime_type=mimetypes.guess_type(path)[0],
        )

        return asset

    return default_url_fetcher(url)
