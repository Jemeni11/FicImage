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

def compress_image(image: BytesIO, target_size: int) -> Image.Image:
    """
    Compresses an image to fit within the specified size.
    :param image: The input image as a byte stream.
    :param target_size: The maximum allowed image size in bytes.
    :return: The compressed image as a PIL.Image.Image object.
    """
    image_size = get_size_format(len(image.getvalue()))
    print_verbose(f"Image size: {image_size}")

    big_photo = Image.open(image).convert("RGBA")

    target_pixel_count = 2.8114 * target_size
    if len(image.getvalue()) > target_size:
        print_verbose(
            f"Image is greater than {get_size_format(target_size)}, compressing"
        )
        scale_factor = target_pixel_count / math.prod(big_photo.size)
        if scale_factor < 1:
            x, y = tuple(int(scale_factor * dim) for dim in big_photo.size)
            print_verbose(
                f"Resizing image dimensions from {big_photo.size} to ({x}, {y})"
            )
            sml_photo = big_photo.resize((x, y), resample=Image.LANCZOS)
        else:
            sml_photo = big_photo
        return sml_photo
    else:
        print_verbose(
            f"Image is less than {get_size_format(target_size)}, not compressing"
        )
        return big_photo


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
