# -*- coding: utf-8 -*-
import fitz
from io import BytesIO
import pikepdf
import mimetypes
import structlog

logger = structlog.getLogger(__name__)

# Make sure mimetypes knows of all the extensions used in the pdf
mimetypes.add_type("application/vnd.ms-fontobject", ".eot")
mimetypes.add_type("font/woff", ".woff")
mimetypes.add_type("font/woff2", ".woff2")
mimetypes.add_type("font/ttf", ".ttf")
mimetypes.add_type("image/svg+xml", ".svg")


def add_coverpage_to_pdf(coverpage, content):
    """ Add the coverpage to the PDF

    Return the resulting PDF bytes """
    try:
        coverpage_pdf = fitz.Document(stream=coverpage, filetype="pdf")
        content_pdf = fitz.Document(stream=content, filetype="pdf")
        coverpage_pdf.insertPDF(content_pdf)
        return coverpage_pdf.write()
    except RuntimeError:
        logger.exception("RuntimeError in fitz")
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
    try:
        doc = fitz.Document(stream=content, filetype="pdf")
        first_page = fitz.Document()
        first_page.insertPDF(doc, to_page=1)
        return first_page.write()
    except RuntimeError:
        logger.exception("RuntimeError in fitz")
        output = BytesIO()
        pdf = pikepdf.open(content)
        del pdf.pages[1:]
        pdf.save(output)
        output.seek(0)
        return output.read()
