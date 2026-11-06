import sys
from pathlib import Path

from ficimagescript.utils.logging import print_verbose_exception


def identify_file_type(file_path: str) -> str:
    """
    Identifies whether a file is an EPUB, ZIP, PDF, or MOBI based on its magic number and extension.

    :param file_path: Path to the file.
    :return: The identified file type ("epub", "zip", "pdf", "mobi", or "unknown").
    """
    if not Path(file_path).is_file():
        return "unknown"

    try:
        with Path(file_path).open("rb") as f:
            # Read the first few bytes of the file
            file_header = f.read(8)

        # Check for file signatures (magic numbers)
        # ZIP and EPUB share the same magic number
        if file_header.startswith(b"PK"):
            if file_path.lower().endswith(".epub"):
                return "epub"
            return "zip"
        if file_header[:4] == b"%PDF":
            return "pdf"
        if file_header[:4] == b"BOOK":
            return "mobi"
        return "unknown"
    except Exception as e:
        print(f"Error reading file: {e}")
        print_verbose_exception(e)
        return "unknown"


def file_search(current_directory: str) -> list[Path]:
    """
    Search for files with specific extensions in a directory and its subdirectories.

    :param current_directory: The starting directory to search in.
    :return: A list of file paths matching the specified extensions.
    """
    # Supported file extensions
    supported_extensions = {".epub", ".zip"}
    files_path_list = []

    # Use pathlib to search recursively
    for file_path in Path(current_directory).rglob("*"):
        if file_path.suffix.lower() in supported_extensions:
            files_path_list.append(file_path)

    if len(files_path_list) == 0:
        sys.exit("No supported files (.epub or .zip) found!")

    print(f"Found {len(files_path_list)} files in total!")
    return files_path_list
