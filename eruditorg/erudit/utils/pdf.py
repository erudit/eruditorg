# -*- coding: utf-8 -*-

import io

from django.template.loader import get_template
from weasyprint import HTML


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
