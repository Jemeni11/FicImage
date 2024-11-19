from PIL import Image
from io import BytesIO
from base64 import b64decode
import math
import requests
from typing import Tuple
from .utils import print_verbose

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


# --- Image Transformation Functions ---

def transform_imgur_url(url: str) -> str:
    """
    Transforms an Imgur page URL into a direct image URL.
    :param url: The Imgur page URL.
    :return: The direct image URL.
    """
    return "https://i.imgur.com/" + url.split("https://imgur.com/")[-1]


def _convert_to_new_format(image_bytestream: bytes | str, image_format: str) -> bytes | str | BytesIO:
    """
    Converts an image byte stream into a new format.
    :param image_bytestream: The input image as a byte stream.
    :param image_format: The desired format (e.g., 'png', 'jpg').
    :return: A new byte stream containing the converted image.
    """
    new_image = BytesIO()
    try:
        Image.open(image_bytestream).save(new_image, format=image_format.upper())
        new_image.name = f"cover.{image_format.lower()}"
        new_image.seek(0)
        return new_image
    except Exception as e:
        print_verbose(
            f"Encountered an error converting image to {image_format}\nError: {e}"
        )
        return image_bytestream


# --- Image Handling Functions ---

def handle_base64_image(
        url: str, image_format: str, compress_images: bool, max_image_size: int
) -> Tuple[bytes, str, str]:
    """
    Handles Base64-encoded image data, optionally compressing or converting it.
    :param url: The Base64 image data URL.
    :param image_format: The target image format (e.g., 'png').
    :param compress_images: Whether to compress the image.
    :param max_image_size: The maximum allowed image size in bytes.
    :return: A tuple of (image data in bytes, image format, MIME type).
    """
    head, base64data = url.split(",")
    file_ext = str(head.split(";")[0].split("/")[1])
    imgdata = b64decode(base64data)

    if file_ext.lower() in ("gif", "webp", "svg"):
        print_verbose("GIF/WEBP/SVG image detected, skipping compression")
        return imgdata, file_ext, f"image/{file_ext}"

    if file_ext.lower() not in SUPPORTED_FORMATS:
        print_verbose(
            f"Image format {file_ext} not supported, converting to {image_format}"
        )
        return (
            _convert_to_new_format(imgdata, image_format).read(),
            image_format.lower(),
            f"image/{image_format.lower()}",
        )

    if compress_images:
        compressed_image = compress_image(BytesIO(imgdata), max_image_size)
        imgdata = PIL_Image_to_bytes(compressed_image, file_ext)

    return imgdata, file_ext, f"image/{file_ext}"


def handle_image_data(
        content: bytes, image_format: str, compress_images: bool, max_image_size: int
) -> Tuple[bytes, str, str]:
    """
    Processes raw image content and optionally compresses or converts it.
    :param content: The raw image content as bytes.
    :param image_format: The target format for the image (e.g., 'png').
    :param compress_images: Whether to compress the image.
    :param max_image_size: The maximum allowed image size in bytes.
    :return: A tuple of (image data in bytes, format, MIME type).
    """
    image = BytesIO(content)
    image.seek(0)

    PIL_image = Image.open(image)
    img_format = str(PIL_image.format)

    if img_format.lower() in ("gif", "webp"):
        return PIL_Image_to_bytes(PIL_image, img_format), img_format, f"image/{img_format.lower()}"

    if compress_images:
        PIL_image = compress_image(image, max_image_size)

    return (
        PIL_Image_to_bytes(PIL_image, image_format),
        image_format,
        f"image/{image_format.lower()}",
    )


def get_image_from_url(
        url: str, image_format: str, compress_images: bool, max_image_size: int
) -> Tuple[bytes, str, str]:
    """
    Downloads and processes an image from a URL.
    :param url: The URL of the image.
    :param image_format: The target format for the image (e.g., 'png').
    :param compress_images: Whether to compress the image.
    :param max_image_size: The maximum allowed image size in bytes.
    :return: A tuple of (image data in bytes, format, MIME type).
    """
    try:
        if is_base64_image(url):
            print_verbose("Base64 image detected")
            return handle_base64_image(
                url, image_format, compress_images, max_image_size
            )

        if url.startswith("https://imgur.com/"):
            url = transform_imgur_url(url)

        with requests.Session() as session:
            headers = {
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                              "Chrome/122.0.0.0 Safari/537.36"
            }
            response = session.get(url, stream=True, headers=headers)

            mime_type = response.headers.get("content-type", "").split("/")[-1]
            if mime_type == "svg+xml":
                return response.content, "svg", "image/svg+xml"

            return handle_image_data(response.content, image_format, compress_images, max_image_size)

    except Exception as e:
        print(f"Encountered an error downloading image from url: {url}")
        print_verbose(f"Error: {e}")


# --- Image Compression Functions ---
def calculate_target_pixel_count(max_size: int, bytes_per_pixel: int) -> float:
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
            f"Image is within the allowed size of {get_size_format(max_size)}, no compression needed."
        )
        return original_image

    print_verbose(
        f"Image exceeds {get_size_format(max_size)}, starting compression..."
    )

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
    print_verbose(
        f"Resizing image from {original_image.size} to ({new_width}, {new_height})..."
    )

    compressed_image = original_image.resize((new_width, new_height), resample=Image.LANCZOS)

    # Optional: Double-check the compressed size
    with BytesIO() as temp_output:
        compressed_image.save(temp_output, format="PNG")  # Adjust format as needed
        compressed_size = len(temp_output.getvalue())
        print_verbose(
            f"Compressed image size: {get_size_format(compressed_size)}"
        )

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
        background_img.paste(
            pil_image.convert("RGBA"), (0, 0), pil_image.convert("RGBA")
        )
        pil_image = background_img.convert("RGB")

    pil_image.save(out_io, format=image_format, optimize=True, quality=95)
    return out_io.getvalue()
