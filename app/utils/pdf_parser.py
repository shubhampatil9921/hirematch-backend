
import pymupdf


MAX_PDF_PAGES = 20


class PDFExtractionError(Exception):
    """Raised when a PDF cannot be processed."""


class PDFTextNotFoundError(PDFExtractionError):
    """Raised when a PDF contains no selectable text."""


def extract_text_from_pdf(
    pdf_bytes: bytes,
    max_pages: int = MAX_PDF_PAGES,
):
    """
    Extract selectable text from a PDF held in memory.
    """

    if not pdf_bytes:
        raise PDFExtractionError("The uploaded PDF is empty.")

    try:
        document = pymupdf.open(
            stream=pdf_bytes,
            filetype="pdf",
        )

        if document.is_encrypted:
            raise PDFExtractionError(
                "Password-protected PDFs are not supported."
            )

        if document.page_count == 0:
            raise PDFExtractionError(
                "The PDF does not contain any pages."
            )

        if document.page_count > max_pages:
            raise PDFExtractionError(
                f"PDF exceeds the maximum limit of {max_pages} pages."
            )

        extracted_pages = [
            page.get_text("text")
            for page in document
        ]

        extracted_text = "\n".join(extracted_pages).strip()

        document.close()

        if not extracted_text:
            raise PDFTextNotFoundError(
                "No selectable text found. The PDF may be scanned "
                "or image-only. OCR is not supported yet."
            )

        return {
            "extracted_text": extracted_text,
            "page_count": len(extracted_pages),
            "character_count": len(extracted_text),
        }

    except PDFExtractionError:
        raise

    except Exception as error:
        raise PDFExtractionError(
            "Unable to read the uploaded PDF. Please upload a valid PDF."
        ) from error
