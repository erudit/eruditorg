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


def add_coverpage_to_pdf(coverpage: bytes, content: bytes) -> bytes:
    """Add the coverpage to the PDF

    Return the resulting PDF bytes"""
    try:
        with fitz.Document(stream=coverpage, filetype="pdf") as coverpage_pdf, fitz.Document(
            stream=content, filetype="pdf"
        ) as content_pdf:
            coverpage_pdf.insertPDF(content_pdf)
            doc = coverpage_pdf.write()
            return doc

    except RuntimeError:
        logger.error("RuntimeError in fitz", exc_info=True)
        output = BytesIO()
        with pikepdf.open(BytesIO(coverpage)) as coverpage_pdf, pikepdf.open(
            BytesIO(content)
        ) as content_pdf:
            coverpage_pdf.pages.extend(content_pdf.pages)
            coverpage_pdf.save(output)
        return output.getvalue()


def get_pdf_first_page(content: bytes) -> bytes:
    """Return the first page of the PDF"""
    try:
        with fitz.Document() as first_page, fitz.Document(
            stream=content, filetype="pdf"
        ) as content_pdf:
            first_page.insertPDF(content_pdf, to_page=0)
            doc = first_page.write()
            return doc

    except RuntimeError:
        logger.error("RuntimeError in fitz", exc_info=True)
        output = BytesIO()
        with pikepdf.open(BytesIO(content)) as pdf:
            del pdf.pages[1:]
            pdf.save(output)
        return output.getvalue()
