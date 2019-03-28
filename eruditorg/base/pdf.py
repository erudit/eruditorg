# -*- coding: utf-8 -*-
import os
import tempfile
import subprocess
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

    with tempfile.NamedTemporaryFile() as f1:
        with tempfile.NamedTemporaryFile() as f2:
            with tempfile.NamedTemporaryFile() as f3:
                coverpage.seek(0)
                content.seek(0)
                f1.write(coverpage.read())
                f2.write(content.read())

                subprocess.check_call(
                    [
                        'qpdf', '--empty', '--pages', f1.name,
                        '1-z', f2.name, '1-z', '--', f3.name
                    ]
                )

                return f3.read()


def get_pdf_first_page(content):
    """ Return the first page of the PDF
    """

    with tempfile.NamedTemporaryFile() as f1:
        with tempfile.NamedTemporaryFile() as f2:
            content.seek(0)
            f1.write(content.read())

            subprocess.check_call(
                [
                    'qpdf', '--empty', '--pages', f1.name,
                    '1-1', '--', f2.name
                ]
            )

            return f2.read()


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
