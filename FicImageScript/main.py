import argparse
import sys
from .shared_state import state
from .utils import config_check, load_config_json, file_search, check_for_update, update_file


def initialize_state(config_file_path: str) -> None:
    """
    Update the global state with config values from a file if it exists.

    :param config_file_path: Path to the config file.
    """
    (config_file_exists, config_file_location) = config_check(config_file_path)
    if config_file_exists:
        ficimage_config = load_config_json(config_file_location)

        # Update state with values from the config file
        state["compress_images"] = ficimage_config.get("compress_images", state["compress_images"])
        state["default_image_format"] = ficimage_config.get("default_image_format", state["default_image_format"])

        # Validate the image format
        if state["default_image_format"].lower() not in ("jpg", "jpeg", "png"):
            state["default_image_format"] = "JPEG"

        state["max_image_size"] = ficimage_config.get("max_image_size", state["max_image_size"])


def main() -> None:
    """
    This function updates the FicHub epub file with images.

    :return: None
    """

    parser = argparse.ArgumentParser(
        description="Update a FicHub file with images.")
    parser.add_argument("-p", "--path",
                        help="The path to the FicHub file.")
    parser.add_argument("-c", "--config_file_path",
                        help="The path to the ficimage.json file.")
    parser.add_argument(
        "-d", "--debug", help="Enable debug mode.", action="store_true")
    parser.add_argument(
        "-v",
        "--version",
        help="Prints out the current version and quits.",
        action='version',
        version=f"FicImage Version {state['version']}"
    )
    parser.add_argument(
        "-r",
        "--recursive",
        help="This will update all files in the directory path given and its subdirectories.",
    )
    parser.add_argument(
        "-u", "--update",
        help="Check if a new version is available.",
        action="store_true"
    )
    args = parser.parse_args()

    file_path = args.path
    config_file_path = args.config_file_path
    debug = args.debug
    recursive = args.recursive

    if args.config_file_path:
        initialize_state(config_file_path)

    if args.update:
        check_for_update(state['version'])
        sys.exit()

    if file_path is None and recursive is None:
        sys.exit("Either pass in a path to a FicHub file or use the --recursive flag to convert "
                 "the current directory and its sub-directories")
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
                if debug:
                    print(f"Exception: {e}")


if __name__ == '__main__':
    main()
