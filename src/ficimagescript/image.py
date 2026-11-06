import math
from base64 import b64decode
from io import BytesIO

import httpx
from PIL import Image, UnidentifiedImageError

from ficimagescript.exceptions import ImageDecodeError, ImageFetchError
from ficimagescript.utils.logging import print_verbose

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
    if img_format in ("gif", "webp") and getattr(pil_image, "is_animated", False):
        return (
            PIL_Image_to_bytes(pil_image, img_format),
            img_format,
            f"image/{img_format}",
        )

    # For non-animated images, apply compression if requested
    if compress_images:
        image_bytes = compress_image(pil_image, max_image_size, target_format)
    else:
        image_bytes = PIL_Image_to_bytes(pil_image, target_format)

    return (
        image_bytes,
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
QUALITY_STEPS = {
    "jpeg": (95, 85, 75, 65, 55, 45),
    "jpg": (95, 85, 75, 65, 55, 45),
    "webp": (80, 70, 60, 50, 40, 30),
}

MIN_SCALE = 0.05
MAX_RESIZE_ATTEMPTS = 4


def compress_image(pil_image: Image.Image, max_size: int, image_format: str) -> bytes:
    """
    Encodes an image to fit within the specified size, lowering quality and resizing as needed.

    :param pil_image: The image to compress.
    :param max_size: The maximum allowed image size in bytes.
    :param image_format: The format the image will be saved as.
    :return: The compressed image bytes.
    """
    quality_steps = QUALITY_STEPS.get(image_format.lower(), ())
    first_quality = quality_steps[0] if quality_steps else None

    best_data = PIL_Image_to_bytes(pil_image, image_format, first_quality)
    print_verbose(f"Encoded image size: {get_size_format(len(best_data))}")

    if len(best_data) <= max_size:
        print_verbose(f"Image is within the allowed size of {get_size_format(max_size)}, no compression needed.")
        return best_data

    print_verbose(f"Image exceeds {get_size_format(max_size)}, starting compression...")

    for quality in quality_steps[1:]:
        data = PIL_Image_to_bytes(pil_image, image_format, quality)
        print_verbose(f"Quality {quality}: {get_size_format(len(data))}")
        if len(data) < len(best_data):
            best_data = data
        if len(data) <= max_size:
            return data

    scale = 1.0
    scale_data = best_data

    for _ in range(MAX_RESIZE_ATTEMPTS):
        # Encoded size roughly tracks pixel count, so the square root of the size ratio is the next scale.
        next_scale = max(MIN_SCALE, scale * math.sqrt(max_size / len(scale_data)))
        if next_scale >= scale:
            break

        scale = next_scale
        new_size = (max(1, int(pil_image.width * scale)), max(1, int(pil_image.height * scale)))
        resized = pil_image.resize(new_size, Image.Resampling.LANCZOS)
        print_verbose(f"Resizing image from {pil_image.size} to {new_size}...")

        scale_data = b""
        for quality in quality_steps or (None,):
            quality_label = quality if quality is not None else "default"
            data = PIL_Image_to_bytes(resized, image_format, quality)
            print_verbose(f"Quality {quality_label}: {get_size_format(len(data))}")
            if not scale_data or len(data) < len(scale_data):
                scale_data = data
            if len(data) <= max_size:
                return data

        if len(scale_data) < len(best_data):
            best_data = scale_data

    print_verbose(
        f"Warning: could not compress image below {get_size_format(max_size)}; "
        f"using the smallest result ({get_size_format(len(best_data))})."
    )
    return best_data


def PIL_Image_to_bytes(pil_image: Image.Image, image_format: str, quality: int | None = None) -> bytes:
    """
    Converts a PIL.Image.Image object to a byte stream.
    :param pil_image: The input PIL image.
    :param image_format: The target format for the image.
    :param quality: Optional encoder quality for lossy formats (JPEG and WebP).
    :return: The image data as bytes.
    """
    out_io = BytesIO()
    image_format = image_format.lower()

    save_options: dict[str, int | bool] = {"optimize": True}
    if quality is not None:
        save_options["quality"] = quality

    if image_format in ("gif", "webp"):
        n_frames = getattr(pil_image, "n_frames", 1)

        if n_frames == 1:
            pil_image.save(out_io, format=image_format, **save_options)
            return out_io.getvalue()

        frames = [pil_image.convert("RGBA")]
        for frame_idx in range(1, n_frames):
            pil_image.seek(frame_idx)
            frames.append(Image.alpha_composite(frames[-1], pil_image.convert("RGBA")))

        frames[0].save(
            out_io,
            format=image_format,
            save_all=True,
            append_images=frames[1:],
            loop=0,
            **save_options,
        )
        return out_io.getvalue()

    if image_format in ("jpeg", "jpg"):
        background_img = Image.new("RGBA", pil_image.size, "white")
        background_img.paste(pil_image.convert("RGBA"), (0, 0), pil_image.convert("RGBA"))
        pil_image = background_img.convert("RGB")
        save_options.setdefault("quality", 95)

    pil_image.save(out_io, format=image_format, **save_options)
    return out_io.getvalue()
