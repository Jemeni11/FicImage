from pathlib import Path

from bs4 import BeautifulSoup
from ebooklib import ITEM_DOCUMENT
from ebooklib.epub import EpubItem, read_epub, write_epub

from ficimagescript.config import state
from ficimagescript.image import get_image_from_url
from ficimagescript.utils.logging import print_image_summary, print_verbose


def has_fichub_attribution_epub(epub_path: str) -> bool:
    """
    Check whether an EPUB looks like a FicHub export by scanning introduction.xhtml.

    :param epub_path: Path to the epub
    :return: True if FicHub attribution found, otherwise False.
    """
    try:
        book = read_epub(epub_path)
        for item in book.get_items_of_type(ITEM_DOCUMENT):
            if item.file_name.startswith("introduction"):
                intro_soup = BeautifulSoup(item.content, "lxml-xml")
                intro_p_tags = intro_soup.find_all("p")
                if len(intro_p_tags) != 0:
                    intro_p_tag = intro_p_tags[-1]
                    fichub_attribution_text = intro_p_tag.get_text(strip=True)
                    if "FicHub.net" in fichub_attribution_text:
                        return True
        return False
    except Exception as e:
        print("Error! Could not confirm if this is a FicHub epub. Skipping")
        print_verbose(f"Error checking FicHub attribution: {e}")
        return False


def update_epub(path_to_epub: str):
    try:
        book = read_epub(path_to_epub)
        print(f"Opened {path_to_epub}")

        # Check if it's a FicHub epub before doing anything else
        if not has_fichub_attribution_epub(path_to_epub):
            print("This is not a FicHub epub")
            return

        compress_images_config: bool = state.get("compress_images", True)
        default_image_format_config: str = state.get("default_image_format", "WEBP")
        max_image_size_config: int = state.get("max_image_size", 100_000)

        file_name = Path(path_to_epub).stem

        images_downloaded = {}

        for item in book.get_items_of_type(ITEM_DOCUMENT):
            try:
                soup = BeautifulSoup(item.content, "lxml-xml")
                p_tags = soup.find_all("p")
                images = [i for i in p_tags if "[img:" in i.text]

                print_verbose(f"Found {len(images)} images in {item.file_name}")

                item_file_name = item.file_name.split(".")[0]
                images_downloaded[item.file_name] = [0, len(images)]

                # Clean up the images link
                # Right now they look like this: <p>[img: <a
                # href="https://i.imgur.com/ABCDEF.jpg" rel="noopener noreferrer">data:image/gif;base64,R0lGOD</a>]</p>
                # But we want to get the link in the href attribute:

                for index, image in enumerate(images, start=1):
                    try:
                        if image is None:
                            print("NoneType, Skipping")
                        else:
                            image_link = f"{image.a['href']}"  # ty:ignore[not-subscriptable]
                            print(
                                f"[{item_file_name}] Image {index} (out of {len(images)}). Source: {image_link}"
                            )
                            result = get_image_from_url(
                                url=image_link,
                                image_format=default_image_format_config,
                                compress_images=compress_images_config,
                                max_image_size=max_image_size_config,
                            )

                            if result is None:
                                print(
                                    f"Error with image {index}: failed to download, skipping ..."
                                )
                                continue

                            image_content, image_extension, image_media_type = result

                            images_downloaded[item.file_name][0] += 1

                            image_path = f"images/{item_file_name}_image_{index}.{image_extension.lower()}"
                            new_image = (
                                f"<img alt='Image {index} from {item.file_name}' "
                                f"style='text-align: center; margin: 2em auto; display: block; max-width: 100%;'"
                                f" src='{image_path}' />"
                            )

                            img = EpubItem(
                                uid=f"{item_file_name}_{index}",
                                file_name=image_path,
                                media_type=image_media_type,
                                content=image_content,
                            )
                            book.add_item(img)
                            image.replace_with(BeautifulSoup(new_image, "lxml-xml"))
                    except Exception as err:
                        print(f"Error with image {index}: {err}, skipping ...")
                item.content = str(soup).encode("utf-8")
            except Exception as error:
                print(f"Error while parsing images: {error}")

        try:
            total_number_of_images_downloaded = sum(
                v[0] for v in images_downloaded.values()
            )

            if total_number_of_images_downloaded > 0:
                try:
                    epub_dir = Path(path_to_epub).parent
                    new_filename = epub_dir / f"[FicImage]{file_name}.epub"
                    print_verbose(f"Saving in directory: {epub_dir} ")
                    write_epub(new_filename, book)
                except Exception as e:
                    print_verbose(
                        f"Error: {e}\n Trying to save in the current working directory instead"
                    )
                    write_epub(f"[FicImage]{file_name}.epub", book)

                print(f"\nWrote [FicImage]{file_name}.epub")
                print_image_summary(file_name, images_downloaded)
            else:
                print("No images successfully downloaded. No new epub was created")
        except Exception as e:
            print(f"Error while writing epub: {e}")
            return

    except FileNotFoundError:
        print(f"File {path_to_epub} not found.")
        return
    except TypeError:
        print("NoneType error, skipping ...")
