import json
import sys
from pathlib import Path
from typing import Literal, TypedDict, TypeGuard

ImageFormat = Literal["webp", "jpeg", "jpg", "png"]


class State(TypedDict):
    compress_images: bool
    default_image_format: ImageFormat
    max_image_size: int
    verbose: bool
    zip_embed_images: bool
    version: str


state: State = {
    "compress_images": True,
    "default_image_format": "webp",
    "max_image_size": 100_000,
    "verbose": False,
    "zip_embed_images": False,
    "version": "5.0.0",
}

VALID_FORMATS: set[ImageFormat] = {"webp", "jpeg", "jpg", "png"}


def is_valid_format(value: str) -> TypeGuard[ImageFormat]:
    """Type guard to check if a string is a valid ImageFormat."""
    return value.lower() in VALID_FORMATS


def validate_format(format_str: str) -> ImageFormat:
    """Validate and normalize image format from CLI input."""
    normalized = format_str.lower()
    if is_valid_format(normalized):
        return normalized
    raise ValueError(
        f"Invalid format '{format_str}'. Must be one of: {', '.join(VALID_FORMATS)}"
    )


def config_check(directory_path: Path | None = None) -> tuple[bool, Path]:
    """
    This function checks if ficimage.json exists in the given directory path
    and returns a tuple containing a boolean and a string (the directory path).
    If no directory path is given, FicImage checks the current directory and
    then the Operating System's home directory.

    :param directory_path: A string or None
    :return: A tuple containing a boolean and a string
    """
    if directory_path is None:
        current_dir = Path.cwd()
        print(
            f"[Config File Check]: No directory was passed, checking current directory '{current_dir}'"
        )

        file_path = Path(current_dir) / "ficimage.json"

        if Path(file_path).is_file():
            print("[Config File Check]: ficimage.json found in current directory!")
            return True, current_dir

        directory_path = Path.home()
        print(
            f"[Config File Check]: ficimage.json not found in current directory, checking '{directory_path}'"
        )

    file_path = Path(directory_path) / "ficimage.json"

    is_file = Path(file_path).is_file()
    print(
        f"[Config File Check]: "
        f"{'ficimage.json found!' if is_file else 'ficimage.json not found, using default config settings'}"
    )

    return is_file, directory_path


def load_config_json(ficimage_path: Path) -> dict:
    """
    Loads ficimage.json. Calls `sys.exit` if there's a JSONDecodeError.
    :param ficimage_path: The path to ficimage.json.
    :return: A dict containing the data stored inside ficimage.json
    """
    full_path = ficimage_path / "ficimage.json"

    try:
        with full_path.open("r") as f:
            return json.load(f)
    except FileNotFoundError:
        sys.exit(
            f"[Loading Config JSON]: File not found. Are you sure there's a ficimage.json file in {ficimage_path}"
        )
    except json.decoder.JSONDecodeError:
        sys.exit("[Loading Config JSON]: Invalid JSON in Config File")
