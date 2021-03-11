import fitz
import io

from base.pdf import get_pdf_first_page


def test_get_pdf_first_page():
    with open("./tests/fixtures/pdf/044308ar.pdf", "rb") as pdf:
        content = io.BytesIO(pdf.read())
        # Original PDF has 4 pages.
        assert len(fitz.Document(stream=content, filetype="pdf")) == 4
        pdf_first_page = get_pdf_first_page(content)
        # `get_pdf_first_page()` should return one page only.
        assert len(fitz.Document(stream=pdf_first_page, filetype="pdf")) == 1
