import logging
from dataclasses import dataclass
from io import BytesIO

import pypdf
from PIL.Image import Image


@dataclass(frozen=True)
class ExtractedImage:
    """
    Class representing extracted image.

    Params:
        page_number: int
        data: bytes
        width: int
        height: int
    """
    page_number: int
    data: bytes
    width: int
    height: int


@dataclass(frozen=True)
class ExtractedPage:
    """
    Class representing extracted page.

    Params:
        page_number: int
        text: int
        images: list[ExtractedImage] | None
    """
    page_number: int
    text: str
    images: list[ExtractedImage] | None


@dataclass(frozen=True)
class ExtractedDocument:
    """
    Class representing extracted document.

    Params:
        pages: list[ExtractedPage]
    """
    pages: list[ExtractedPage]


def _extract_images_from_page(
    page: pypdf.PageObject, page_num: int
) -> list[ExtractedImage] | None:
    image_list = list(page.images)
    if len(image_list) == 0:
        return None
    extracted_images: list[ExtractedImage] = []
    for image in image_list:
        try:
            decoded_image: Image = image.image
            extracted_images.append(
                ExtractedImage(
                    page_number=page_num,
                    data=image.data,
                    width=decoded_image.size[0],
                    height=decoded_image.size[1],
                )
            )
        except AttributeError:
            logging.warning(f"Couldn't decode image on page_num = {page_num}.")
    return extracted_images


def extract_pdf_from_bytes(pdf_bytes: bytes) -> ExtractedDocument:
    stream = BytesIO(pdf_bytes)
    reader = pypdf.PdfReader(stream)
    pages: list[ExtractedPage] = []
    for page_num, page in enumerate(reader.pages, start=1):
        images = _extract_images_from_page(page, page_num)
        pages.append(
            ExtractedPage(page_number=page_num, text=page.extract_text(), images=images)
        )
    return ExtractedDocument(pages)


def filter_decorative_images(images: list[ExtractedImage]) -> list[ExtractedImage]:

