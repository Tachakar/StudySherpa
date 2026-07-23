from collections.abc import Callable

import pytest
from pymupdf import FileDataError

from studysherpa.ingestion.pdf import extract_pdf_from_bytes, filter_images_on_page


def test_single_page_without_images(pdf_factory: Callable[[int, bool], bytes]):
    pdf_bytes = pdf_factory(1, False)
    pdf_object = extract_pdf_from_bytes(pdf_bytes)
    assert len(pdf_object.pages) == 1
    assert pdf_object.pages[0].page_number == 1
    assert len(pdf_object.pages[0].images) == 0


def test_multiple_pages_without_images(pdf_factory: Callable[[int, bool], bytes]):
    pdf_bytes = pdf_factory(5, False)
    pdf_object = extract_pdf_from_bytes(pdf_bytes)
    assert len(pdf_object.pages) == 5
    for i, page in enumerate(pdf_object.pages, start=1):
        assert page.page_number == i
        assert len(page.images) == 0


def test_multiple_pages_with_images(pdf_factory: Callable[[int, bool], bytes]):
    pdf_bytes = pdf_factory(5, True)
    pdf_object = extract_pdf_from_bytes(pdf_bytes)
    assert len(pdf_object.pages) == 5
    for i, page in enumerate(pdf_object.pages, start=1):
        assert page.page_number == i
        if i % 2 == 0:  # Every other page has images
            assert len(page.images) != 0
            for image in page.images:
                assert image.height == image.width == 50
                assert image.page_number == page.page_number
        else:
            assert len(page.images) == 0


def test_incorrect_bytes():
    with pytest.raises(FileDataError):
        _ = extract_pdf_from_bytes(b"not a pdf")


def test_zero_pages(pdf_factory: Callable[[int, bool], bytes]):
    pdf_bytes = pdf_factory(0, True)
    pdf_object = extract_pdf_from_bytes(pdf_bytes)
    assert len(pdf_object.pages) == 0


def test_image_filtering(pdf_factory: Callable[[int, bool], bytes]):
    pdf_bytes = pdf_factory(5, True)
    pdf_object = extract_pdf_from_bytes(pdf_bytes)
    for page in pdf_object.pages:
        if len(page.images) == 0:
            continue
        """
        Image size in _make_pdf is 50px by 50px, page size = A4, so
            aspect_ratio = 1
            percentage_coverage = ~0.5
        """
        aspect_ratio = page.images[0].width / page.images[0].height
        percentage_coverage = (
            (page.images[0].width * page.images[0].height) / (page.width * page.height)
        ) * 100
        assert aspect_ratio == 1
        assert round(percentage_coverage, 2) == 0.5
        filtered_images_default_thr = filter_images_on_page(page)
        assert len(filtered_images_default_thr) == 0
        non_empty_filtered_images = filter_images_on_page(
            page, min_percentage_coverage=0.02
        )
        assert len(non_empty_filtered_images) == len(page.images)
