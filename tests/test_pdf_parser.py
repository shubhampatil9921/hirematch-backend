
import pymupdf
import pytest

from app.utils.pdf_parser import (
    extract_text_from_pdf,
    PDFExtractionError,
    PDFTextNotFoundError,
)

def create_pdf(text=None, page_count=1):
    """Create a small PDF in memory for testing."""

    document = pymupdf.open()

    for _ in range(page_count):
        page = document.new_page()

        if text:
            page.insert_text((72, 72), text)

    pdf_bytes = document.tobytes()
    document.close()

    return pdf_bytes

def test_extract_text_from_valid_pdf():
    pdf_bytes = create_pdf(
        "Python Developer with SQL experience."
    )

    result = extract_text_from_pdf(pdf_bytes)

    assert "Python Developer" in result["extracted_text"]
    assert result["page_count"] == 1
    assert result["character_count"] > 0

def test_reject_invalid_pdf():
    with pytest.raises(
        PDFExtractionError,
        match="Unable to read",
    ):
        extract_text_from_pdf(b"This is not a PDF")

def test_reject_pdf_without_selectable_text():
    pdf_bytes = create_pdf()

    with pytest.raises(
        PDFTextNotFoundError,
        match="No selectable text found",
    ):
        extract_text_from_pdf(pdf_bytes)

def test_reject_pdf_over_page_limit():
    pdf_bytes = create_pdf(
        text="Test page",
        page_count=2,
    )

    with pytest.raises(
        PDFExtractionError,
        match="maximum limit",
    ):
        extract_text_from_pdf(pdf_bytes, max_pages=1)