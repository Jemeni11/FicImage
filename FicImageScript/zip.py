from .global_state import state
import os
import base64
import zipfile
import tempfile
from bs4 import BeautifulSoup
from .image import get_image_from_url
from .utils import print_verbose, print_image_summary

FICHUB_ATTR = b"Exported with the assistance of FicHub.net"
FICHUB_DOMAIN = b"FicHub.net"


def extract_html_from_zip(input_zip_path: str) -> dict:
    """
    Extract HTML file(s) from a zip archive and return their contents.

    Args:
        input_zip_path (str): Path to the zip file.

    Returns:
        dict: A dictionary of {filename: content} for each HTML file in the zip.
    """
    html_files = {}

    with zipfile.ZipFile(input_zip_path, "r") as zf:
        for file_name in zf.namelist():
            if file_name.endswith(".html"):
                print(f"Processing HTML file: {file_name}")
                with zf.open(file_name) as html_file:
                    html_files[file_name] = html_file.read()

    if not html_files:
        raise ValueError("No HTML files found in the zip archive.")

    return html_files


def modify_html(content: bytes, images_dir: str, embed_images: bool) -> tuple[bytes, int, int]:
    """
    Modify the HTML content to replace image placeholders with downloaded images.

    :param content: The original HTML content.
    :param images_dir: Directory to store downloaded images.
    :param embed_images: If True, save the images directly in the HTML file as base64 images.
    :param verbose: If True, enables verbose output.
    :return: tuple of (modified_html_bytes, images_downloaded_count, total_images_found)
    """
    soup = BeautifulSoup(content, "lxml")
    p_tags = soup.find_all("p")
    images = [i for i in p_tags if "[img:" in i.text]

    total_images = len(images)
    downloaded_count = 0

    print_verbose(
        f"Found {total_images} image{'' if total_images == 1 else 's'}")

    for index, image in enumerate(images, start=1):
        if image is None:
            print("NoneType, Skipping")
            continue

        try:
            if not hasattr(image, "a") or image.a is None:
                print(f"Skipping image {index}: no link found")
                continue

            image_link = str(image.a["href"])
            print(f"Processing image {index}: {image_link}")

            # Download and process the image
            result = get_image_from_url(
                image_link, state.get("default_image_format", "WEBP"),
                state.get("compress_images", True),
                state.get("max_image_size", 100_000)
            )

            if result is None:
                print(f"Skipping image {index}: failed to download")
                continue

            image_content, image_extension, image_media_type = result
            downloaded_count += 1

            if embed_images:
                base64_data = base64.b64encode(image_content).decode("utf-8")
                data_uri = f"data:{image_media_type};base64,{base64_data}"

                # Replace the placeholder with the inline base64 image
                new_image = (
                    f"<img alt='Image {index}' "
                    f"style='text-align: center; margin: 2em auto; display: block; max-width: 100%;' "
                    f"src='{data_uri}' />"
                )
            else:
                # Write into the temp dir (filesystem path)
                filename = f"image_{index}.{image_extension.lower()}"
                image_path = os.path.join(images_dir, filename)
                with open(image_path, "wb") as img_file:
                    img_file.write(image_content)

                # Use a relative path inside the zip (NOT the temp path)
                zip_image_ref = os.path.join(
                    "images", filename).replace("\\", "/")

                # Replace the original placeholder with the new image tag
                new_image = (
                    f"<img alt='Image {index}' "
                    f"style='text-align: center; margin: 2em auto; display: block; max-width: 100%;' "
                    f"src='{zip_image_ref}' />"
                )

            image.replace_with(BeautifulSoup(new_image, "lxml"))

        except Exception as e:
            print(f"Error processing image {index}: {e}, skipping ...")

    return str(soup).encode("utf-8"), downloaded_count, total_images


def has_fichub_attribution(zip_path: str) -> bool:
    """
    Check whether a ZIP looks like a FicHub Zipped HTML export.

    Reads only the first 64KB of each .html file in the archive and searches for FicHub's
    attribution text ("Exported with the assistance of FicHub.net") near the top of the document.

    :param zip_path: Path to the ZIP file to inspect.
    :return: True if the ZIP contains a HTML file with the expected FicHub attribution; otherwise False.
    """

    with zipfile.ZipFile(zip_path, "r") as zf:
        for name in zf.namelist():
            if not name.lower().endswith(".html"):
                continue

            with zf.open(name) as f:
                head = f.read(64 * 1024)

            if FICHUB_ATTR in head:
                return True
            if FICHUB_DOMAIN in head and b"Exported with the assistance" in head:
                return True

    return False


def process_zip(input_zip_path: str, zip_embed_images: bool = False):
    """
    Process a ZIP archive that contains HTML files by replacing FicHub image placeholders
    (e.g., “[img: …]” blocks pointing to URLs) with actual images downloaded from those URLs.

    :param input_zip_path: Path to the input zip file.
    :param zip_embed_images: If True, embed images into HTML as base64 data URIs. If False, store images as files
                under `images/` in the output ZIP and reference them from HTML.
    """

    if not has_fichub_attribution(input_zip_path):
        print("This is not a FicHub Zipped HTML File (Did you unpack a FicHub epub and pass it in?)")
        return

    zip_base_name = os.path.splitext(os.path.basename(input_zip_path))[0]
    output_zip_path = f"[FicImage]{zip_base_name}.zip"

    images_downloaded = {}

    try:
        html_files = extract_html_from_zip(input_zip_path)

        if zip_embed_images:
            modified_files = {}
            for file_name, content in html_files.items():
                modified_content, downloaded, total = modify_html(
                    content, "", zip_embed_images)
                modified_files[file_name] = modified_content
                images_downloaded[file_name] = [downloaded, total]

            # Save the modified files back to a new zip
            with zipfile.ZipFile(output_zip_path, "w") as zf:
                for file_name, content in modified_files.items():
                    zf.writestr(file_name, content)
            return

        # Non-embed mode: use a temp directory and package images under images/
        with tempfile.TemporaryDirectory(prefix="ficimage_") as images_dir:

            modified_files = {}

            for fn, content in html_files.items():
                modified_content, downloaded, total = modify_html(
                    content, images_dir, False)
                modified_files[fn] = modified_content
                images_downloaded[fn] = [downloaded, total]

            with zipfile.ZipFile(output_zip_path, "w") as zf:
                for file_name, content in modified_files.items():
                    zf.writestr(file_name, content)

                # Write images into the zip under images/
                for file in os.listdir(images_dir):
                    file_path = os.path.join(images_dir, file)
                    zf.write(file_path, arcname=f"images/{file}")

        # Print summary
        total_downloaded = sum(v[0] for v in images_downloaded.values())
        if total_downloaded > 0:
            print(f"\nWrote {output_zip_path}")
            print_image_summary(zip_base_name, images_downloaded)
        else:
            print("No images successfully downloaded. No new zip was created.")
            if os.path.exists(output_zip_path):
                os.remove(output_zip_path)

    except Exception as e:
        print(f"Error: {e}")


def update_zip(file_path: str):
    process_zip(file_path, state.get("zip_embed_images", False))
