# -*- coding: utf-8 -*-
import os
import tempfile
import subprocess
import io
import mimetypes

from django.template.loader import get_template
from weasyprint import HTML
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


def generate_pdf(template_name, file_object=None, context=None, base_url=None):
    """
    Generates a PDF into the given file object from a specific Django template.
    """
    tmpl = get_template(template_name)
    # calling replace() on a django SafeString leads to messy stuff sometimes
    html = str(tmpl.render(context))
    if file_object is None:
        file_object = io.BytesIO()

    try:
        HTML(string=html, base_url=base_url, url_fetcher=local_url_fetcher).write_pdf(file_object)
    except Exception:
        # the 0xAD character is a soft hyphen. If we don't strip it, we *sometimes* get a decoding
        # error at the weasyprint/Cairo level. It's not an encoding problem per se: the 0xAD
        # character is encoded just fine. The problem is in the way that weasyprint splits lines
        # during layout. It seems to sometimes split utf-8 multibytes characters in two.
        # It's, however, very tricky to isolate. We could only manage to reproduce the problem
        # on whole document rendering so far and we went with this temporary bandaid.
        # ref eruditorg#1640
        html = html.replace('\xad', '')
        HTML(string=html, base_url=base_url, url_fetcher=local_url_fetcher).write_pdf(file_object)

    return file_object
