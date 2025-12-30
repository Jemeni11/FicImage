import os
import sys
import json
from urllib import request, error
from packaging.version import parse
from .global_state import state


def config_check(directory_path: str = None) -> tuple[bool, str]:
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
        print(
            f"[Config File Check]: No directory was passed, "
            f"checking current directory '{current_dir}'"
        )

        file_path = os.path.join(current_dir, "ficimage.json")

        if os.path.isfile(file_path):
            print(f"[Config File Check]: ficimage.json found in current directory!")
            return True, current_dir

        directory_path = os.path.expanduser("~")
        print(
            f"[Config File Check]: ficimage.json not found "
            f"in current directory, checking '{directory_path}'"
        )

    file_path = os.path.join(directory_path, "ficimage.json")

    is_file = os.path.isfile(file_path)
    print(
        f"[Config File Check]: "
        f"{'ficimage.json found!' if is_file else 'ficimage.json not found, using default config settings'}"
    )

    return is_file, directory_path


def load_config_json(ficimage_path: str) -> dict:
    """
    Loads ficimage.json. Calls `sys.exit` if there's a JSONDecodeError.
    :param ficimage_path: The path to ficimage.json.
    :return: A dict containing the data stored inside ficimage.json
    """
    try:
        with open(os.path.join(ficimage_path, "ficimage.json"), "r") as f:
            return json.load(f)
    except FileNotFoundError:
        sys.exit(
            f"[Loading Config JSON]: File not found. "
            f"Are you sure there's a ficimage.json file in {ficimage_path}"
        )
    except json.decoder.JSONDecodeError:
        sys.exit("[Loading Config JSON]: Invalid JSON in Config File")


def default_ficimage_settings() -> dict:
    """
    Returns a dict containing the default config settings for ficimage.
    :return: A dict
    """
    default_settings = {
        "compress_images": True,
        "default_image_format": "WEBP",
        "max_image_size": 100000,
        "zip_embed_images": False,
    }
    default_settings_str = "\n".join(
        [f"{key}: {value}" for key, value in default_settings.items()]
    )
    print(
        f"\nDefault config settings:"
        f"\n============================\n"
        f"{default_settings_str}"
        f"\n============================\n"
    )
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
    supported_extensions = (".epub", ".zip", ".pdf", ".mobi")
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


def check_for_update(current_version: str):
    """Checks if a new version of FicImage is available on PyPI."""
    try:
        url = "https://pypi.org/pypi/FicImageScript/json"
        with request.urlopen(url, timeout=5) as response:
            data = json.load(response)
            latest_version = data["info"]["version"]

        if parse(latest_version) > parse(current_version):
            print(f"Update available: v{latest_version}. You're on v{current_version}.")
            print("Run `pip install --upgrade FicImageScript` to update.")
        else:
            print(f"You're on the latest version: v{current_version}.")
            print("💖 Enjoying FicImage? Check out `ficimage --credits`")

    except error.URLError as e:
        print(f"Unable to check for updates: {e}")


def print_verbose(message: str):
    """Prints messages only if verbose mode is enabled."""
    if state.get("verbose", False):
        print(f"[VERBOSE] {message}")


def print_image_summary(base_name: str, images_downloaded: dict[str, list[int]]) -> None:
    """
    Print a summary table of images downloaded per file.

    :param base_name: The base file name (for the header).
    :param images_downloaded: Dict of {filename: [downloaded_count, total_count]}.
    :return: None
    """

    total_downloaded = sum(v[0] for v in images_downloaded.values())
    total_found = sum(v[1] for v in images_downloaded.values())

    if total_found == 0:
        print("No images found.")
        return

    print(f"\nImage overview of {base_name}")
    print("=" * 54)
    for filename, (downloaded, total) in images_downloaded.items():
        padding = " " * max(0, 18 - len(filename))
        print(f"{filename}{padding}\t{downloaded} out of {total} images downloaded")
    print("=" * 54)
    print(f"Total: {total_downloaded} out of {total_found}")
    print("=" * 54)


def show_credits():
    print("\nFicImage - Made by @Jemeni11")
    print("\nWhy I built this:")
    print("""
    ℹ️  NOTE: FicHub is a growing set of accessibility tools for reading fanfiction.

FicHub (https://fichub.net/) is great - it really is. But after one too many times of copying image links to open 
in my browser, I had to find an alternative. Building this tool wasn't my first thought. I initially found 
leech.py (https://github.com/kemayo/leech), but its image support was still a work in progress. After discovering 
a PR (https://github.com/kemayo/leech/pull/84) that added basic image support, I expanded on that code, which 
eventually became the core of what we now call FicImage.

The project wouldn't be where it is today without Iris (FicHub's creator), who helped with the finishing touches 
by fixing a major bug that prevented v1 from working properly. She also suggested making it a proper package - 
something I hadn't even considered.

So thank you to Iris for both creating FicHub and helping with this project. Without FicHub, this tool obviously 
wouldn't exist (lol).

Check out FicHub: 
  ✦  Website (https://fichub.net/)
  ✦  GitHub (https://github.com/FicHub/fichub.net)
  ✦  Discord (https://discord.gg/sByBAhX)

I've also made other Fanfiction tools like FicRadar (https://github.com/Jemeni11/FicRadar/), 
TalesTrove (https://github.com/Jemeni11/TalesTrove) and contributed to 
WebToEpub (https://github.com/dteviot/WebToEpub) and Leech.py (https://github.com/kemayo/leech).
""")

    print("\nFind me at:")
    print("  ✦  GitHub: https://github.com/Jemeni11")
    print("  ✦  LinkedIn: https://linkedin.com/in/emmanuel-jemeni")
    print("  ✦  BlueSky: https://bsky.app/profile/jemeni11.bsky.social")
    print("  ✦  Twitter/X: https://twitter.com/Jemeni11_")
    print("\nSupport FicImage:")
    print("  ✦  Star the repo: https://github.com/Jemeni11/FicImage")
    print("  ✦  Contribute: PRs and Issues welcome!")
    print("  ✦  Buy me a coffee: https://buymeacoffee.com/jemeni11")
    print("  ✦  GitHub Sponsors: https://github.com/sponsors/Jemeni11")
