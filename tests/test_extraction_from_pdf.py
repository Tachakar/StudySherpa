from collections.abc import Callable

import pypdf.errors
import pytest

from studysherpa.ingestion.pdf import extract_pdf_from_bytes


def test_single_page_without_images(pdf_factory: Callable[[int, bool], bytes]):
    pdf_bytes = pdf_factory(1, False)
    pdf_object = extract_pdf_from_bytes(pdf_bytes)
    assert len(pdf_object.pages) == 1
    assert pdf_object.pages[0].page_number == 1
    assert pdf_object.pages[0].images is None


def test_multiple_pages_without_images(pdf_factory: Callable[[int, bool], bytes]):
    pdf_bytes = pdf_factory(5, False)
    pdf_object = extract_pdf_from_bytes(pdf_bytes)
    assert len(pdf_object.pages) == 5
    for i, page in enumerate(pdf_object.pages, start=1):
        assert page.page_number == i
        assert page.images is None


def test_multiple_pages_with_images(pdf_factory: Callable[[int, bool], bytes]):
    pdf_bytes = pdf_factory(5, True)
    pdf_object = extract_pdf_from_bytes(pdf_bytes)
    assert len(pdf_object.pages) == 5
    for i, page in enumerate(pdf_object.pages, start=1):
        assert page.page_number == i
        if i % 2 == 0:  # Every other page has images
            assert page.images is not None
            for image in page.images:
                assert image.height == image.width == 50
                assert image.page_number == page.page_number
        else:
            assert page.images is None


def test_incorrect_bytes():
    with pytest.raises(pypdf.errors.PdfReadError):
        _ = extract_pdf_from_bytes(b"not a pdf")


def test_zero_pages(pdf_factory: Callable[[int, bool], bytes]):
    pdf_bytes = pdf_factory(0, True)
    pdf_object = extract_pdf_from_bytes(pdf_bytes)
    assert pdf_object.pages == []
