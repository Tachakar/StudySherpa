import logging
from dataclasses import dataclass
from io import BytesIO

from pymupdf import Document, Page

from studysherpa.core.config import filter_config


@dataclass(frozen=True)
class ExtractedImage:
    """
    Params:
        page_number: `int`
        data: `bytes`
        width: `float`
        height: `float`
    """

    page_number: int
    data: bytes
    width: float
    height: float


@dataclass(frozen=True)
class ExtractedPage:
    """
    Params:
        page_number: `int`
        text: `int`
        images: `list[ExtractedImage]`
        page_width: float
        page_height: float
    """

    page_number: int
    text: str
    images: list[ExtractedImage]
    width: float
    height: float


@dataclass(frozen=True)
class ExtractedDocument:
    """
    Params:
        pages: `list[ExtractedPage]`
    """

    pages: list[ExtractedPage]


def _extract_images_from_page(
    page: Page, page_num: int, doc: Document
) -> list[ExtractedImage]:
    image_list = page.get_images(full=True)
    if not image_list:
        return []
    res: list[ExtractedImage] = []
    for img in image_list:
        xref = img[0]
        extracted = doc.extract_image(xref)
        data = extracted["image"]
        bbox = page.get_image_bbox(img)
        if isinstance(bbox, tuple):
            bbox = bbox[0]
        res.append(
            ExtractedImage(
                page_number=page_num,
                data=data,
                width=bbox.width,
                height=bbox.height,
            )
        )
    return res


def extract_pdf_from_bytes(pdf_bytes: bytes) -> ExtractedDocument:
    stream = BytesIO(pdf_bytes)
    doc = Document(stream=stream, filetype="pdf")
    pages: list[ExtractedPage] = []
    for page_index in range(len(doc)):
        page = doc[page_index]
        page_num = page_index + 1
        images: list[ExtractedImage] = _extract_images_from_page(page, page_num, doc)
        text = page.get_text("text")
        width, height = page.mediabox_size.x, page.mediabox_size.y
        pages.append(
            ExtractedPage(
                page_number=page_num,
                text=text,
                width=width,
                height=height,
                images=images,
            )
        )
    return ExtractedDocument(pages)


def filter_images_on_page(
    page: ExtractedPage,
    min_percentage_coverage: float = filter_config.min_percentage_coverage,
    max_aspect_ratio: float = filter_config.max_aspect_ratio,
) -> list[ExtractedImage]:
    """
    Filters images based on aspect ratio and percentage coverage.

    Args:
        images: `list[ExtractedImage]`

    Returns:
        `list[ExtractedImage]`
    """
    images = page.images
    if len(images) == 0:
        logging.info(f"No images to filter on page {page.page_number}")
        return []
    res = []
    for image in images:
        percentage_coverage = (
            (image.width * image.height) / (page.width * page.height)
        ) * 100
        aspect_ratio = image.width / image.height
        if (aspect_ratio < max_aspect_ratio) and (
            percentage_coverage > min_percentage_coverage
        ):
            res.append(image)
    return res
