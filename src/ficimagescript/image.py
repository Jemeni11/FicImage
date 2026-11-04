import math
from base64 import b64decode
from io import BytesIO

import httpx
from PIL import Image, UnidentifiedImageError

from .exceptions import ImageDecodeError, ImageFetchError
from .utils.logging import print_verbose

SUPPORTED_FORMATS = {"jpg", "jpeg", "png", "gif", "webp", "svg"}


# --- Utility Functions ---


def get_mime_type(extension: str) -> str:
    """
    Returns the MIME type for a given image file extension.
    :param extension: The file extension (e.g., 'png', 'jpg').
    :return: The corresponding MIME type as a string.
    """
    return f"image/{extension.lower()}"


def is_base64_image(url: str) -> bool:
    """
    Checks if a given URL is a Base64-encoded image.
    :param url: The URL string.
    :return: True if the URL is a Base64 image, False otherwise.
    """
    return url.startswith("data:image") and "base64" in url


def get_size_format(b, factor=1000, suffix="B"):
    """
    Scale bytes to its proper byte format
    e.g:
        1253656 => '1.20MB'
        1253656678 => '1.17GB'
    :param b: The size in bytes.
    :param factor: The factor for unit conversion (default is 1000).
    :param suffix: The suffix to use (default is 'B').
    :return: A string representation of the file size.
    """
    for unit in ["", "K", "M", "G", "T", "P", "E", "Z"]:
        if b < factor:
            return f"{b:.2f}{unit}{suffix}"
        b /= factor
    return f"{b:.2f}Y{suffix}"


# --- Image Handling Functions ---


def get_bytes_from_base64(url: str) -> tuple[bytes, str]:
    """
    Decodes a Base64-encoded image data URL.
    :param url: The Base64 image data URL.
    :return: A tuple of (decoded bytes, file extension).
    """
    head, base64data = url.split(",")
    file_ext = str(head.split(";")[0].split("/")[1])
    imgdata = b64decode(base64data)
    return imgdata, file_ext


def get_bytes_from_http(url: str) -> tuple[bytes, str]:
    """
    Downloads image bytes from an HTTP URL.
    :param url: The URL to download from.
    :return: A tuple of (image bytes, MIME type from response headers).
    :raises ImageFetchError: If the download fails.
    """
    if url.startswith("https://imgur.com/"):
        url = "https://i.imgur.com/" + url.split("https://imgur.com/")[-1]

    client_headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML,\
                     like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    }

    try:
        with httpx.Client(headers=client_headers).stream("GET", url) as response:
            try:
                response.raise_for_status()
            except httpx.HTTPStatusError as e:
                print(f"HTTP error {response.status_code} downloading image: {url}")
                print_verbose(f"Response content-type: {response.headers.get('content-type')}")
                raise ImageFetchError(url, f"HTTP {response.status_code}") from e

            mime_type = response.headers.get("content-type", "").split("/")[-1]
            response.read()
            return response.content, mime_type

    except httpx.RequestError as e:
        print(f"Network error downloading image from url: {url}")
        print_verbose(f"Error: {e}")
        raise ImageFetchError(url, "Network error") from e


def process_image_bytes(
    bytes_data: bytes,
    detected_format: str,
    target_format: str,
    compress_images: bool,
    max_image_size: int,
) -> tuple[bytes, str, str]:
    """
    Processes image bytes: validates format, converts if needed, compresses if requested.
    :param bytes_data: The raw image bytes.
    :param detected_format: The detected format from the source (e.g., 'svg+xml', 'png').
    :param target_format: The target format to convert to (e.g., 'webp').
    :param compress_images: Whether to compress the image.
    :param max_image_size: The maximum allowed image size in bytes.
    :return: A tuple of (processed bytes, final format, MIME type).
    :raises ImageDecodeError: If the bytes cannot be decoded as an image.
    """
    # Handle SVG (no PIL processing)
    if detected_format == "svg+xml":
        return bytes_data, "svg", "image/svg+xml"

    # Try to decode with PIL to get the actual format
    image_stream = BytesIO(bytes_data)
    image_stream.seek(0)

    try:
        pil_image = Image.open(image_stream)
    except UnidentifiedImageError as e:
        print("Could not decode downloaded content as an image.")
        print_verbose(
            "This can happen if the URL returns an error page (e.g. 404 HTML), "
            "the file is corrupted/truncated, or the image format isn't supported by Pillow."
        )
        print_verbose(
            "Check the URL in your browser. If it loads as an image, then there's something wrong"
            " with my code. Please contact me with the image URL so I can try to fix it. You can"
            " make an issue on this tool's GitHub Issue Tracker (https://github.com/Jemeni11/FicImage/issues)"
            " or if you don't have a GitHub, you can use this Tally Form "
            "(https://tally.so/r/7Rjpgz?project=FicImage)"
        )
        raise ImageDecodeError("unknown", str(e)) from e

    img_format = str(pil_image.format).lower()

    # Animated formats: preserve as-is
    if img_format in ("gif", "webp"):
        return (
            PIL_Image_to_bytes(pil_image, img_format),
            img_format,
            f"image/{img_format}",
        )

    # For non-animated images, apply compression if requested
    if compress_images:
        pil_image = compress_image(image_stream, max_image_size)

    return (
        PIL_Image_to_bytes(pil_image, target_format),
        target_format,
        f"image/{target_format}",
    )


def get_image_from_url(
    url: str, image_format: str, compress_images: bool, max_image_size: int
) -> tuple[bytes, str, str]:
    """
    Downloads and processes an image from a URL.
    :param url: The URL of the image.
    :param image_format: The target format for the image (e.g., 'png').
    :param compress_images: Whether to compress the image.
    :param max_image_size: The maximum allowed image size in bytes.
    :return: A tuple of (image data in bytes, format, MIME type).
    :raises ImageFetchError: If the image cannot be fetched (network/HTTP errors).
    :raises ImageDecodeError: If the downloaded content cannot be decoded as an image.
    :raises ImageFormatError: If the image format is not supported.
    """
    if is_base64_image(url):
        print_verbose("Base64 image detected")
        imgdata, file_ext = get_bytes_from_base64(url)

        # Return SVG as-is (no processing needed)
        if file_ext.lower() == "svg":
            return imgdata, "svg", "image/svg+xml"

        return process_image_bytes(imgdata, file_ext, image_format, compress_images, max_image_size)

    bytes_data, detected_format = get_bytes_from_http(url)

    return process_image_bytes(bytes_data, detected_format, image_format, compress_images, max_image_size)


# --- Image Compression Functions ---
def calculate_target_pixel_count(max_size: int, bytes_per_pixel: float | int) -> float:
    """
    Estimate the target pixel count to fit within the maximum size.

    :param max_size: Maximum file size in bytes.
    :param bytes_per_pixel: Bytes used per pixel in the image format.
    :return: Target pixel count.
    """
    return max_size / bytes_per_pixel


def compress_image(image: BytesIO, max_size: int) -> Image.Image:
    """
    Compresses an image to fit within the specified size while maintaining its aspect ratio.

    :param image: The input image as a byte stream.
    :param max_size: The maximum allowed image size in bytes.
    :return: The compressed image as a PIL.Image.Image object.
    """

    # Load the image and determine bytes per pixel from its mode
    original_image = Image.open(image)
    mode_to_bpp = {
        "1": 1 / 8,  # 1 bit per pixel (monochrome)
        "L": 1,  # 1 byte per pixel (grayscale)
        "P": 1,  # 1 byte per pixel (palette-based)
        "RGB": 3,  # 3 bytes per pixel (True color)
        "RGBA": 4,  # 4 bytes per pixel (True color with alpha)
        "CMYK": 4,  # 4 bytes per pixel (CMYK color space)
        "YCbCr": 3,  # 3 bytes per pixel (JPEG color space)
    }
    bytes_per_pixel = mode_to_bpp.get(original_image.mode, 4)  # Default to RGBA

    original_size = len(image.getvalue())
    print_verbose(f"Original image size: {get_size_format(original_size)}")
    print_verbose(f"Image mode: {original_image.mode}, bytes per pixel: {bytes_per_pixel}")

    if original_size <= max_size:
        print_verbose(
            f"Image is within the allowed size of {get_size_format(max_size)}, no \
                compression needed."
        )
        return original_image

    print_verbose(f"Image exceeds {get_size_format(max_size)}, starting compression...")

    # Calculate the target pixel count and the scale factor
    target_pixel_count = calculate_target_pixel_count(max_size, bytes_per_pixel)
    original_pixel_count = original_image.size[0] * original_image.size[1]
    scale_factor = math.sqrt(target_pixel_count / original_pixel_count)

    if scale_factor >= 1:
        print_verbose("Image already fits within the size; no resizing needed.")
        return original_image

    # Resize the image
    new_width = int(original_image.size[0] * scale_factor)
    new_height = int(original_image.size[1] * scale_factor)
    print_verbose(f"Resizing image from {original_image.size} to ({new_width}, {new_height})...")

    compressed_image = original_image.resize((new_width, new_height), resample=Image.Resampling.LANCZOS)

    # Optional: Double-check the compressed size
    with BytesIO() as temp_output:
        # Adjust format as needed
        compressed_image.save(temp_output, format="PNG")
        compressed_size = len(temp_output.getvalue())
        print_verbose(f"Compressed image size: {get_size_format(compressed_size)}")

        if compressed_size > max_size:
            print_verbose("Warning: Compressed image still exceeds max size.")

    return compressed_image


def PIL_Image_to_bytes(pil_image: Image.Image, image_format: str) -> bytes:
    """
    Converts a PIL.Image.Image object to a byte stream.
    :param pil_image: The input PIL image.
    :param image_format: The target format for the image.
    :return: The image data as bytes.
    """
    out_io = BytesIO()
    if image_format.lower() in ("gif", "webp"):
        frames = []
        current = pil_image.convert("RGBA")
        while True:
            try:
                frames.append(current)
                pil_image.seek(pil_image.tell() + 1)
                current = Image.alpha_composite(current, pil_image.convert("RGBA"))
            except EOFError:
                break
        frames[0].save(
            out_io,
            format=image_format,
            save_all=True,
            append_images=frames[1:],
            optimize=True,
            loop=0,
        )
        return out_io.getvalue()

    if image_format.lower() in ["jpeg", "jpg"]:
        background_img = Image.new("RGBA", pil_image.size, "white")
        background_img.paste(pil_image.convert("RGBA"), (0, 0), pil_image.convert("RGBA"))
        pil_image = background_img.convert("RGB")

    pil_image.save(out_io, format=image_format, optimize=True, quality=95)
    return out_io.getvalue()
