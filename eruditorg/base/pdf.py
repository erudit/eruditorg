# -*- coding: utf-8 -*-
import fitz
import mimetypes

# Make sure mimetypes knows of all the extensions used in the pdf
mimetypes.add_type("application/vnd.ms-fontobject", ".eot")
mimetypes.add_type("font/woff", ".woff")
mimetypes.add_type("font/woff2", ".woff2")
mimetypes.add_type("font/ttf", ".ttf")
mimetypes.add_type("image/svg+xml", ".svg")


def add_coverpage_to_pdf(coverpage, content):
    """ Add the coverpage to the PDF

    Return the resulting PDF bytes """
    coverpage_pdf = fitz.Document(stream=coverpage, filetype="pdf")
    content_pdf = fitz.Document(stream=content, filetype="pdf")
    coverpage_pdf.insertPDF(content_pdf)
    return coverpage_pdf.write()


def get_pdf_first_page(content):
    """ Return the first page of the PDF
    """
    doc = fitz.Document(stream=content, filetype="pdf")
    first_page = fitz.Document()
    first_page.insertPDF(doc, to_page=1)
    return first_page.write()
