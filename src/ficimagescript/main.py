import argparse
import sys
from pathlib import Path

from .config import config_check, load_config_json, state, validate_format
from .formats import update_epub, update_zip
from .utils.files import file_search, identify_file_type
from .utils.update import check_for_update, show_credits


def initialize_state(config_file_path: Path | None = None) -> None:
    """
    Update the global state with config values from a file if it exists.

    :param config_file_path: Optional path to the config file. If None, checks default locations.
    """
    if config_file_path:
        (config_file_exists, config_file_location) = config_check(config_file_path)
    else:
        # Check default locations (current dir, then home dir)
        (config_file_exists, config_file_location) = config_check(None)

    if config_file_exists:
        ficimage_config = load_config_json(config_file_location)

        # Update state with values from the config file
        state["compress_images"] = ficimage_config.get(
            "compress_images", state["compress_images"]
        )
        state["default_image_format"] = ficimage_config.get(
            "default_image_format", state["default_image_format"]
        )
        state["max_image_size"] = ficimage_config.get(
            "max_image_size", state["max_image_size"]
        )
        state["zip_embed_images"] = ficimage_config.get(
            "zip_embed_images", state["zip_embed_images"]
        )

    try:
        state["default_image_format"] = validate_format(state["default_image_format"])
    except ValueError as e:
        print(f"[Config Warning]: {e} Defaulting to webp.")
        state["default_image_format"] = "webp"


def update_file(file_path: str):
    """
    Identify and process a FicHub file based on its type.

    :param file_path: Path to the file to process.
    """
    file_type = identify_file_type(file_path)
    update_function = None

    if file_type == "epub":
        update_function = update_epub
    elif file_type == "zip":
        update_function = update_zip
    elif file_type in ("pdf", "mobi"):
        print(
            f"[Unsupported] {file_type.upper()} is not supported. "
            "For best results, use an EPUB file and convert it to "
            f"{file_type.upper()} using a tool like Calibre."
        )
        return

    if update_function:
        update_function(file_path)
    else:
        print(f"Unsupported file type: {file_type}")


def main() -> None:
    """This function updates the FicHub file with images."""

    parser = argparse.ArgumentParser(
        description="Update a FicHub file with images.",
        epilog="Made with <3 by Emmanuel Jemeni | \
                Send Feedback: https://tally.so/r/7Rjpgz?project=FicImage",
    )
    parser.add_argument("-p", "--path", help="The path to the FicHub file.")
    parser.add_argument(
        "-c", "--config_file_path", help="The path to the ficimage.json file."
    )
    parser.add_argument(
        "-V", "--verbose", help="Enable verbose output", action="store_true"
    )
    parser.add_argument(
        "-v",
        "--version",
        help="Prints out the current version and quits.",
        action="version",
        version=f"FicImage Version {state['version']}",
    )
    parser.add_argument(
        "-r",
        "--recursive",
        help="This will update all files in the directory path given and its subdirectories.",
    )
    parser.add_argument(
        "-u",
        "--update",
        help="Check if a new version is available.",
        action="store_true",
    )
    parser.add_argument(
        "--credits", help="Show credits and support information", action="store_true"
    )
    args = parser.parse_args()

    file_path = args.path
    config_file_path = args.config_file_path
    verbose = args.verbose
    recursive = args.recursive

    if args.credits:
        show_credits()
        sys.exit()

    if args.config_file_path:
        initialize_state(config_file_path)

    if verbose:
        state["verbose"] = verbose

    if args.update:
        check_for_update(state["version"])
        sys.exit()

    if file_path is None and recursive is None:
        sys.exit(
            "Either pass in a path to a FicHub file or use the --recursive flag to convert "
            "the current directory and its sub-directories"
        )
    elif file_path:
        if recursive:
            print("Ignoring --recursive flag since file_path was given")
        update_file(file_path)
    elif recursive:
        list_of_files = file_search(recursive)
        for i in list_of_files:
            try:
                update_file(i)
            except Exception as e:
                print(f"Error! Skipping {i}")
                if state.get("verbose", False):
                    print(f"Exception: {e}")


if __name__ == "__main__":
    main()
