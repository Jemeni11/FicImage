from .global_state import state
import os
import hashlib
import base64
import zipfile
import shutil
import tempfile
from typing import List
from bs4 import BeautifulSoup
from .image import get_image_from_url


def copy_zip(input_zip_path: str, backup_zip_path: str) -> None:
    """
    Create a backup copy of the input ZIP file.

    Args:
        input_zip_path (str): Path to the original ZIP file.
        backup_zip_path (str): Path where the backup ZIP file will be saved.
    """
    shutil.copy(input_zip_path, backup_zip_path)


def extract_zip_metadata(input_zip_path: str) -> List[zipfile.ZipInfo]:
    """
    Extract full metadata (ZipInfo objects) from the input ZIP file.

    Args:
        input_zip_path (str): Path to the input ZIP file.

    Returns:
        List[zipfile.ZipInfo]: A list of ZipInfo objects from the input ZIP.
    """
    with zipfile.ZipFile(input_zip_path, "r") as zf:
        return zf.infolist()


def create_images_dir(input_zip_path: str) -> str:
    """
    Create a unique images directory in the current working directory.

    Args:
        input_zip_path (str): The path to the input zip file.

    Returns:
        str: The path to the created images directory.
    """
    # Strip the extension and get the base name
    zip_base_name = os.path.splitext(os.path.basename(input_zip_path))[0]
    zip_hash = hashlib.md5(zip_base_name.encode()).hexdigest()[:8]
    dir_name = f"ficimage_{zip_base_name}_{zip_hash}"

    os.makedirs(dir_name, exist_ok=True)
    return dir_name


def clean_images_dir(dir_name: str) -> None:
    """
    Delete the directory containing temporary image files.

    Args:
        dir_name (str): Name of the directory.
    """
    if os.path.exists(dir_name):
        shutil.rmtree(dir_name)


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
            print(f"Found file: {file_name}")

            if file_name.endswith(".html"):
                print(f"Processing HTML file: {file_name}")
                with zf.open(file_name) as html_file:
                    html_files[file_name] = html_file.read()

    if not html_files:
        raise ValueError("No HTML files found in the zip archive.")

    return html_files


def modify_html(
        content: str | bytes, images_dir: str, embed_images: bool, debug: bool = True
) -> bytes:
    """
    Modify the HTML content to replace image placeholders with downloaded images.

    Args:
        content (bytes): The original HTML content.
        images_dir (str): Directory to store downloaded images.
        embed_images (bool): If True, save the images directly in the HTML file as base64 images.
        debug (bool): If True, enables debug output.

    Returns:
        bytes: The modified HTML content.

    """
    soup = BeautifulSoup(content, "lxml")
    p_tags = soup.find_all("p")
    images = [i for i in p_tags if "[img:" in i.text]

    if debug:
        print(f"Found {len(images)} images")

    for idx, image in enumerate(images):
        if image is None:
            print("NoneType, Skipping")
            continue

        try:
            image_link = image.a["href"]
            print(f"Processing image {idx + 1}: {image_link}")

            # Download and process the image
            (image_content, image_extension, image_media_type) = get_image_from_url(
                image_link, "jpeg", True, 100_000
            )

            if embed_images:
                base64_data = base64.b64encode(image_content).decode("utf-8")
                data_uri = f"data:{image_media_type};base64,{base64_data}"

                # Replace the placeholder with the inline base64 image
                new_image = (
                    f"<img alt='Image {idx + 1}' "
                    f"style='text-align: center; margin: 2em auto; display: block;' "
                    f"src='{data_uri}' />"
                )
            else:
                image_path = os.path.join(
                    images_dir, f"image_{idx + 1}.{image_extension.lower()}"
                )
                with open(image_path, "wb") as img_file:
                    img_file.write(image_content)

                # Replace the original placeholder with the new image tag
                new_image = (
                    f"<img alt='Image {idx + 1}' "
                    f"style='text-align: center; margin: 2em auto; display: block;' "
                    f"src='{image_path}' />"
                )

            image.replace_with(BeautifulSoup(new_image, "lxml"))

        except Exception as e:
            print(f"Error processing image {idx + 1}: {e}, skipping ...")

    return str(soup).encode("utf-8")


def process_zip(input_zip_path: str):
    """
    Process a zip file containing HTML files and replace image placeholders.

    Args:
        input_zip_path (str): Path to the input zip file.
    """
    # Create a unique directory for images
    _embed_images = True
    zip_base_name = os.path.splitext(os.path.basename(input_zip_path))[0]
    zip_hash = hashlib.md5(zip_base_name.encode()).hexdigest()[:8]
    images_dir = f"ficimage_{zip_base_name}_{zip_hash}"

    if not _embed_images:
        os.makedirs(images_dir, exist_ok=True)

    try:
        # Extract HTML files from the zip
        html_files = extract_html_from_zip(input_zip_path)

        modified_files = {}
        for file_name, content in html_files.items():
            modified_content = modify_html(content, images_dir, _embed_images)
            modified_files[file_name] = modified_content

        # Save the modified files back to a new zip
        output_zip_path = f"[FicImage]{zip_base_name}.zip"
        with zipfile.ZipFile(output_zip_path, "w") as zf:
            for file_name, content in modified_files.items():
                zf.writestr(file_name, content)

            if not _embed_images:
                # Add the images directory and its contents to the zip
                for root, _, files in os.walk(images_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        # Preserve the relative path of the images directory in the ZIP
                        arcname = os.path.relpath(
                            file_path, start=os.path.dirname(images_dir)
                        )
                        zf.write(file_path, arcname)

        print(f"Processed zip saved to {output_zip_path}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if not _embed_images:
            clean_images_dir(images_dir)


def update_zip(file_path: str):
    process_zip(file_path)
