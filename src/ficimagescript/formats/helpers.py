"""
Common functions shared across format handlers.
"""

from bs4 import Tag

from ficimagescript.config import state
from ficimagescript.image import get_image_from_url


def try_get_image(
    image: Tag | None,
    index: int,
    total_images: int,
    context_name: str = "",
) -> tuple[bytes, str, str] | None:
    """
    Safely fetch an image from a BeautifulSoup Tag element.

    This function handles the common pattern of extracting an image URL from
    an <a> tag and downloading it, with proper error handling and guards.

    :param image: The BeautifulSoup Tag containing the image link.
    :param index: The image index (for logging).
    :param total_images: Total number of images (for logging).
    :param context_name: Optional context name for logging (e.g., file name).
    :return: A tuple of (image_content, image_extension, image_media_type) if successful,
             None if the image has no link or should be skipped.
    :raises ImageFetchError: If the image cannot be fetched.
    :raises ImageDecodeError: If the image cannot be decoded.
    :raises ImageFormatError: If the image format is not supported.
    """
    if image is None:
        print("NoneType, Skipping")
        return None

    # Guard: check if the image has an <a> tag with an href
    if not hasattr(image, "a") or image.a is None:
        print(f"Skipping image {index}: no link found")
        return None

    image_link = str(image.a["href"])
    print(f"[{context_name}] Image {index} (out of {total_images}). Source: {image_link}")

    return get_image_from_url(
        image_link,
        state.get("default_image_format", "WEBP"),
        state.get("compress_images", True),
        state.get("max_image_size", 100_000),
    )
