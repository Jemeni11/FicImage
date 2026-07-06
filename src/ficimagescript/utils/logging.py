from ficimagescript.config import state


def print_verbose(message: str):
    """Prints messages only if verbose mode is enabled."""
    if state.get("verbose", False):
        print(f"[VERBOSE] {message}")


def print_image_summary(
    base_name: str, images_downloaded: dict[str, list[int]]
) -> None:
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
