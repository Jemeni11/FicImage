import os
import sys
from typing import Tuple
import json
from urllib import request, error


def config_check(directory_path: str = None) -> Tuple[bool, str]:
    """
    This function checks if ficimage.json exists in the given directory path
    and returns a tuple containing a boolean and a string (the directory path).
    If no directory path is given, FicImage checks the current directory and
    then the Operating System's home directory.
    :param directory_path: A string or None
    :return: A tuple containing a boolean and a string
    """
    if directory_path is None:
        current_dir = os.getcwd()
        print(f"[Config File Check]: No directory was passed, checking current directory '{
        current_dir}'")

        file_path = os.path.join(current_dir, "ficimage.json")

        if os.path.isfile(file_path):
            print(f"[Config File Check]: ficimage.json found in current directory!")
            return True, current_dir

        directory_path = os.path.expanduser("~")
        print(f"[Config File Check]: ficimage.json not found in current directory, checking '{
        directory_path}'")

    file_path = os.path.join(directory_path, "ficimage.json")

    is_file = os.path.isfile(file_path)
    print(f"[Config File Check]: "
          f"{'ficimage.json found!' if is_file else 'ficimage.json not found, using default config settings'}")

    return is_file, directory_path


def load_config_json(ficimage_path: str) -> dict:
    """
    Loads ficimage.json. Calls `sys.exit` if there's a JSONDecodeError.
    :param ficimage_path: The path to ficimage.json.
    :return: A dict containing the data stored inside ficimage.json
    """
    try:
        with open(os.path.join(ficimage_path, "ficimage.json"), 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        sys.exit(f"[Loading Config JSON]: File not found. Are you sure there's a ficimage.json file in {
        ficimage_path}")
    except json.decoder.JSONDecodeError:
        sys.exit("[Loading Config JSON]: Invalid JSON in Config File")


def default_ficimage_settings() -> dict:
    """
    Returns a dict containing the default config settings for ficimage.
    :return: A dict
    """
    default_settings = {
        "compress_images": True,
        "default_image_format": "JPEG",
        "max_image_size": 100000
    }
    default_settings_str = '\n'.join(
        [f"{key}: {value}" for key, value in default_settings.items()])
    print(f"\nDefault config settings:"
          f"\n============================\n"
          f"{default_settings_str}"
          f"\n============================\n")
    return default_settings


def identify_file_type(file_path: str) -> str:
    """
    Identifies whether a file is an EPUB, ZIP, PDF, or MOBI based on its magic number and extension.

    :param file_path: Path to the file.
    :return: The identified file type ("epub", "zip", "pdf", "mobi", or "unknown").
    """
    if not os.path.isfile(file_path):
        return "unknown"

    try:
        with open(file_path, "rb") as f:
            # Read the first few bytes of the file
            file_header = f.read(8)

        # Check for file signatures (magic numbers)
        if file_header.startswith(b"PK"):  # ZIP and EPUB share the same magic number
            if file_path.lower().endswith(".epub"):
                return "epub"
            return "zip"
        elif file_header[:4] == b"%PDF":
            return "pdf"
        elif file_header[:4] == b"BOOK":
            return "mobi"
        else:
            return "unknown"
    except Exception as e:
        print(f"Error reading file: {e}")
        return "unknown"


def file_search(current_directory: str) -> list:
    """
    Search for files with specific extensions in a directory and its subdirectories.

    :param current_directory: The starting directory to search in.
    :return: A list of file paths matching the specified extensions.
    """
    # Supported file extensions
    supported_extensions = ('.epub', '.zip', '.pdf', '.mobi')
    files_path_list = []

    # Walk through the directory tree
    for dir_path, dir_names, files in os.walk(current_directory):
        for file in files:
            if file.lower().endswith(supported_extensions):
                file_path = os.path.join(dir_path, file)
                files_path_list.append(file_path)

    if len(files_path_list) == 0:
        sys.exit("No supported files (.epub, .zip, .pdf, .mobi) found!")

    print(f"Found {len(files_path_list)} files in total!")
    return files_path_list


def parse_version(version: str):
    """Converts a version string (e.g., '1.2.3') into a tuple of integers (1, 2, 3)."""
    return tuple([int(part) for part in version.split(".")])


def check_for_update(current_version: str):
    """Checks if a new version of FicImage is available on PyPI."""
    try:
        url = "https://pypi.org/pypi/FicImageScript/json"
        with request.urlopen(url, timeout=5) as response:
            data = json.load(response)
            latest_version = data["info"]["version"]

        if parse_version(latest_version) > parse_version(current_version):
            print(f"Update available: v{latest_version}. You're on v{current_version}.")
            print(f"Run `pip install --upgrade FicImageScript` to update.")
        else:
            print(f"You're on the latest version: v{current_version}.")

    except error.URLError as e:
        print(f"Unable to check for updates: {e}")

