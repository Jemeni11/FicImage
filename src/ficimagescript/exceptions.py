"""
Custom exceptions for FicImage.

These exceptions distinguish between different types of image processing failures,
allowing callers to make informed decisions about retrying vs skipping.
"""


class ImageFetchError(Exception):
    """
    Raised when an image cannot be fetched from its source.

    This includes network errors, HTTP errors (404, 403, etc.), and other
    transient failures that might be worth retrying.
    """

    def __init__(self, url: str, reason: str) -> None:
        self.url = url
        self.reason = reason
        super().__init__(f"Failed to fetch image from {url}: {reason}")


class ImageDecodeError(Exception):
    """
    Raised when downloaded content cannot be decoded as an image.

    This happens when the URL returns an error page (e.g., 404 HTML),
    the file is corrupted/truncated, or the format isn't supported by Pillow.
    This is typically a permanent failure (retrying won't help).
    """

    def __init__(self, url: str, reason: str) -> None:
        self.url = url
        self.reason = reason
        super().__init__(f"Failed to decode image from {url}: {reason}")


class ImageFormatError(Exception):
    """
    Raised when an image format is not supported or cannot be converted.

    This is a permanent failure - the format cannot be processed.
    """

    def __init__(self, format_name: str, reason: str) -> None:
        self.format_name = format_name
        self.reason = reason
        super().__init__(f"Unsupported image format '{format_name}': {reason}")
