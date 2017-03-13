# -*- coding: utf-8 -*-
import tempfile
import subprocess
import io

from django.template.loader import get_template
from weasyprint import HTML


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


def generate_pdf(template_name, file_object=None, context=None, base_url=None):
    """
    Generates a PDF into the given file object from a specific Django template.
    """
    tmpl = get_template(template_name)
    html = tmpl.render(context)
    if file_object is None:
        file_object = io.BytesIO()

    HTML(string=html, base_url=base_url).write_pdf(file_object)
    return file_object
